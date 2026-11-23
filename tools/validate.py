#!/usr/bin/env python3
"""Valida la estructura del skill: frontmatter, enlaces internos y límites de tamaño.

Uso: python3 tools/validate.py [carpeta-del-skill]
Sale con código 1 si encuentra errores. Solo usa la biblioteca estándar.
"""
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\]\(((?!https?://|#|mailto:)[^)\s]+)\)")
MAX_SKILL_LINES = 500  # un SKILL.md largo consume contexto del agente: el detalle va en references/


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md debe empezar con un bloque frontmatter (---)")
    end = text.find("\n---", 4)
    if end < 0:
        raise ValueError("el frontmatter no está cerrado con ---")
    fields = {}
    for line in text[4:end].splitlines():
        if line.strip() and ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def validate(root: Path) -> list[str]:
    errors = []
    skill = root / "SKILL.md"
    if not skill.is_file():
        return [f"falta {skill}"]
    text = skill.read_text(encoding="utf-8")
    try:
        fm = frontmatter(text)
    except ValueError as e:
        return [str(e)]

    name, desc = fm.get("name", ""), fm.get("description", "")
    if not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append(f"name inválido: {name!r} (minúsculas, números y guiones; máx. 64)")
    if name != root.resolve().name and root.resolve().name not in (".", ""):
        print(f"aviso: name ({name}) no coincide con la carpeta ({root.resolve().name}); "
              "al instalarlo, la carpeta debe llamarse igual que name")
    if not desc:
        errors.append("falta description")
    elif len(desc) > 1024:
        errors.append(f"description demasiado larga: {len(desc)} caracteres (máx. 1024)")
    if "<" in desc or ">" in desc:
        errors.append("description no debe contener < ni >")
    if len(text.splitlines()) > MAX_SKILL_LINES:
        errors.append(f"SKILL.md tiene más de {MAX_SKILL_LINES} líneas: mové detalle a references/")

    for md in [skill, *root.glob("references/*.md"), *root.glob("templates/*.md"), *root.glob("examples/**/*.md")]:
        for target in LINK_RE.findall(md.read_text(encoding="utf-8")):
            path = (md.parent / target.split("#")[0]).resolve()
            if not path.exists():
                errors.append(f"{md.relative_to(root)}: enlace roto a {target}")
    return errors


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    errors = validate(root)
    for e in errors:
        print("error:", e)
    if not errors:
        print("skill válido ✔")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
