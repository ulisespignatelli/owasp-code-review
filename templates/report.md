# Revisión de seguridad: {nombre del proyecto}

**Fecha:** {fecha} · **Alcance:** {repo / carpeta / PR revisado} · **Commit:** {hash si se conoce}
**Metodología:** OWASP Top 10:2025 y OWASP API Security Top 10 2023, revisión manual de código con
trazado de datos (origen → camino → punto vulnerable). Sin pruebas contra sistemas en ejecución.

## Resumen ejecutivo

{2 a 4 oraciones para alguien que no lee código: estado general, el riesgo más importante y qué hacer primero.}

| Crítica | Alta | Media | Baja | Informativa |
|:-:|:-:|:-:|:-:|:-:|
| {n} | {n} | {n} | {n} | {n} |

## Contexto del sistema

- **Stack:** {lenguaje, framework, base de datos}
- **Puntos de entrada:** {rutas/servicios principales}
- **Fronteras de confianza:** {público / usuarios / admin / servicios}
- **Activos sensibles:** {qué se protege}

## Hallazgos

### [{SEVERIDAD}] {N}. {Título que diga problema e impacto}

| | |
|---|---|
| **Severidad** | {Crítica / Alta / Media / Baja / Informativa} |
| **Confianza** | {Confirmado / Probable} |
| **Categoría** | {A01:2025 · Pérdida de control de acceso} {+ API1:2023 si aplica} |
| **CWE** | {CWE-639} |
| **Ubicación** | `{archivo}:{línea}` |

**Código**

```{lenguaje}
{fragmento mínimo}
```

**Por qué es explotable**

{Origen del dato → camino → punto vulnerable, con referencias a líneas. Qué controles faltan.}

**Cómo se explota**

1. {paso en palabras, sin exploit listo para usar}
2. {…}

**Impacto:** {qué obtiene un atacante, en concreto}

**Corrección**

```diff
- {línea actual}
+ {línea corregida}
```

**Test sugerido:** {test que falla hoy y pasa con la corrección}

---

## A verificar

{Patrones riesgosos sin camino demostrado: una línea cada uno, con qué habría que mirar para confirmarlos.}

## Descartados

{Pistas revisadas que no son explotables, con el motivo. Ej.: "`hashlib.md5` en `cache.py:12`: se usa para claves de caché, no para contraseñas."}

## Cobertura

- **Revisado:** {carpetas/archivos}
- **No revisado:** {qué quedó afuera y por qué}
- **Supuestos:** {configuración que no se pudo ver}

## Hacer primero

1. {acción}
2. {acción}
3. {acción}
