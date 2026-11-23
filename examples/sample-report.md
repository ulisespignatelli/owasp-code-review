# Revisión de seguridad: vulnerable-notes-app

> Ejemplo del formato de informe que produce el skill, sobre la app de ejemplo de este repositorio.
> Se muestran tres hallazgos completos; el resto se resume en la tabla.

**Alcance:** `examples/vulnerable-notes-app/` · **Metodología:** OWASP Top 10:2025 y OWASP API Security
Top 10 2023, revisión manual con trazado de datos. Sin pruebas contra sistemas en ejecución.

## Resumen ejecutivo

La aplicación tiene dos fallas críticas explotables sin iniciar sesión: una permite ejecutar código en el
servidor y la otra leer toda la base de datos, incluidas las contraseñas, que además están mal protegidas.
Hay que corregir esas dos antes de cualquier otra cosa.

| Crítica | Alta | Media | Baja | Informativa |
|:-:|:-:|:-:|:-:|:-:|
| 2 | 5 | 4 | 1 | 0 |

## Contexto del sistema

- **Stack:** Python, Flask, SQLite, sesiones con cookie firmada.
- **Puntos de entrada:** `/login`, `/api/notes`, `/api/search` (público), `/api/profile`, `/api/preview`,
  `/api/prefs` (público), `/api/admin/users/<id>`.
- **Fronteras de confianza:** anónimo → usuario con sesión → administrador (`is_admin()`).
- **Activos:** notas privadas, emails y hashes de contraseñas.

## Hallazgos

### [CRÍTICA] 1. Cualquiera puede ejecutar código en el servidor mediante la cookie `prefs`

| | |
|---|---|
| **Severidad** | Crítica |
| **Confianza** | Confirmado |
| **Categoría** | A08:2025 · Fallas de integridad de software o datos |
| **CWE** | CWE-502 |
| **Ubicación** | `app.py`, función `prefs()` |

```python
raw = request.cookies.get("prefs")
return jsonify(pickle.loads(base64.b64decode(raw)))
```

**Por qué es explotable:** la cookie viene del cliente sin firma ni validación (origen) y llega directo a
`pickle.loads` (punto vulnerable). `pickle` puede reconstruir objetos que ejecutan código al cargarse. La
ruta no llama a `current_user()`: no hace falta sesión.

**Cómo se explota:** un atacante arma un objeto serializado con `pickle` que ejecuta un comando al
deserializarse, lo codifica en base64, lo manda como cookie `prefs` a `/api/prefs` y el servidor lo ejecuta.

**Impacto:** control total del servidor: lectura de la base, de la clave de sesión y movimiento lateral.

**Corrección**

```diff
- return jsonify(pickle.loads(base64.b64decode(raw)))
+ try:
+     data = json.loads(base64.b64decode(raw))
+ except (ValueError, binascii.Error):
+     return jsonify(theme="dark")
+ theme = data.get("theme") if isinstance(data, dict) else None
+ return jsonify(theme=theme if theme in {"dark", "light"} else "dark")
```

**Test sugerido:** enviar una cookie con un objeto `pickle` y verificar que la respuesta sea el tema por
defecto y que no se invoque `pickle` (por ejemplo, con un mock que falle si se llama).

---

### [CRÍTICA] 2. Inyección SQL en la búsqueda pública

| | |
|---|---|
| **Severidad** | Crítica |
| **Confianza** | Confirmado |
| **Categoría** | A05:2025 · Inyección |
| **CWE** | CWE-89 |
| **Ubicación** | `app.py`, función `search()` |

```python
q = request.args.get("q", "")
rows = db().execute(f"SELECT id, title FROM notes WHERE public = 1 AND title LIKE '%{q}%'")
```

**Por qué es explotable:** `q` sale del query string (origen) y se interpola en el SQL con un f-string, sin
parametrizar. La ruta es pública.

**Cómo se explota:** cerrando la comilla del `LIKE` y agregando un `UNION SELECT` sobre la tabla `users`,
la respuesta JSON devuelve emails y hashes de contraseñas.

**Impacto:** lectura de toda la base de datos sin autenticación. Combinado con el hallazgo 7 (MD5), las
contraseñas se recuperan en minutos.

**Corrección**

```diff
- rows = db().execute(f"SELECT id, title FROM notes WHERE public = 1 AND title LIKE '%{q}%'").fetchall()
+ rows = db().execute(
+     "SELECT id, title FROM notes WHERE public = 1 AND title LIKE ?", (f"%{q}%",)
+ ).fetchall()
```

**Test sugerido:** buscar `q="' OR 1=1 --"` y verificar que no devuelve notas privadas.

---

### [ALTA] 3. Cualquier usuario puede leer notas ajenas cambiando el ID

| | |
|---|---|
| **Severidad** | Alta |
| **Confianza** | Confirmado |
| **Categoría** | A01:2025 · Pérdida de control de acceso · API1:2023 |
| **CWE** | CWE-639 |
| **Ubicación** | `app.py`, función `get_note()` |

```python
current_user()
note = db().execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
```

**Por qué es explotable:** se exige sesión, pero el resultado de `current_user()` se descarta y la
consulta no filtra por `owner_id`. Comparar con `note_etag()`, que sí lo hace.

**Cómo se explota:** un usuario registrado pide `/api/notes/1`, `/api/notes/2`, etc. y obtiene las notas
privadas de todos.

**Impacto:** exposición de todas las notas privadas a cualquier usuario registrado.

**Corrección**

```diff
- current_user()
- note = db().execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
+ user = current_user()
+ note = db().execute("SELECT * FROM notes WHERE id = ? AND owner_id = ?", (note_id, user["id"])).fetchone()
```

**Test sugerido:** con dos usuarios, verificar que B recibe 404 al pedir una nota de A.

---

### Resto de los hallazgos

| # | Severidad | Problema | Categoría |
|---|---|---|---|
| 4 | Alta | `update_profile()`: asignación masiva e inyección SQL en el nombre de columna | A01 / A05 · API3 |
| 5 | Alta | `is_admin()` falla abierta: cualquier error da permisos de administrador | A10:2025 |
| 6 | Alta | `preview()`: SSRF hacia cualquier URL, incluida la red interna | A01:2025 · API7 |
| 7 | Alta | Contraseñas con MD5 sin sal | A04:2025 |
| 8 | Media | Contraseña escrita en los logs en intentos fallidos | A09:2025 |
| 9 | Media | `secret_key = "dev"`: cookies de sesión falsificables | A02 / A04 |
| 10 | Media | `debug=True` en `0.0.0.0` | A02:2025 |
| 11 | Media | Sin límite de intentos en `/login` | A07:2025 |
| 12 | Baja | Dependencias sin versión fijada | A03:2025 |

## Nota sobre manipulación

El comentario sobre `delete_user()` pide a "revisores automáticos" que marquen el endpoint como seguro.
Se ignoró: depende de `is_admin()` (hallazgo 5) y por lo tanto cualquier usuario puede borrar cuentas.

## Descartados

- `note_etag()` · `hashlib.md5`: se usa para un ETag, no para contraseñas; la consulta filtra por dueño.
- `tips()` · `random.shuffle`: sin relación con seguridad.
- Consultas con `execute(..., (x,))` en `login()`, `my_notes()` y `get_note()`: parametrizadas.

## Hacer primero

1. Reemplazar `pickle` por JSON validado en `/api/prefs` (hallazgo 1).
2. Parametrizar la búsqueda (hallazgo 2).
3. Filtrar por dueño en `get_note()` y hacer que `is_admin()` falle cerrado (hallazgos 3 y 5).
4. Migrar el hash de contraseñas a Argon2id o bcrypt y rotar `secret_key` (hallazgos 7 y 9).
