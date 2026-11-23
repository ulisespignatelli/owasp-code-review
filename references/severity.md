# Cómo calificar la severidad

La severidad responde una sola pregunta: **¿qué tan mal le va a la organización si alguien lo explota,
y qué tan fácil es?** Calificá el impacto real en este sistema, no el peor caso teórico de la categoría.

## Escala

| Severidad | Criterio | Ejemplos |
|---|---|---|
| **Crítica** | Explotable sin autenticación o por cualquier usuario, con impacto grave y directo: ejecución de código, toma de cuentas masiva, acceso a toda la base de datos. | Inyección SQL en el login; deserialización insegura en un endpoint público; secreto de producción con permisos amplios en un repo público. |
| **Alta** | Impacto grave que requiere una condición razonable (ser usuario registrado, una interacción simple), o impacto acotado pero sin condiciones. | IDOR que expone datos personales de otros usuarios; SSRF hacia la red interna; XSS almacenado en una vista de administración. |
| **Media** | Impacto limitado o explotación con condiciones menos probables. | XSS reflejado que requiere un enlace armado; falta de límite de intentos en el login; CORS permisivo sin credenciales. |
| **Baja** | Impacto menor, difícil de explotar o que solo ayuda a otros ataques. | Mensajes de error detallados; enumeración de usuarios; cookies sin `SameSite`. |
| **Informativa** | Buenas prácticas sin impacto demostrable. | Cabeceras de seguridad faltantes; dependencias desactualizadas sin CVE. |

## Ajustes

- **Quién puede llegar:** anónimo > cualquier usuario registrado > usuario con un rol específico > solo admin.
  Bajá un nivel si solo un administrador puede explotarlo, salvo que el impacto cruce esa frontera.
- **Datos o activos en juego:** datos personales, credenciales, dinero o acceso a la infraestructura suben
  la severidad.
- **Controles compensatorios:** un WAF o una red privada pueden bajar la probabilidad, pero no corrigen
  el código. Mencionalos y no bajes más de un nivel por ellos.
- **Encadenamiento:** si dos hallazgos juntos permiten algo grave (enumeración + falta de límite de
  intentos = toma de cuentas), describilo y calificá la cadena.

## Dependencias con CVE

No copies el puntaje CVSS del CVE sin pensar. Calificá según:

1. ¿El proyecto usa la función o el componente vulnerable? Si no, Baja o Informativa.
2. ¿Hay explotación activa? Si está en el catálogo KEV de CISA
   (https://www.cisa.gov/known-exploited-vulnerabilities-catalog), subila.
3. ¿Qué probabilidad de explotación tiene? EPSS (https://www.first.org/epss/) alto suma urgencia.

## CVSS v4.0 (opcional)

Si el usuario o su organización usan CVSS, agregá el vector de CVSS v4.0
(https://www.first.org/cvss/v4.0/) junto a la severidad, por ejemplo
`CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N`. Usá el vector para explicar, no
para reemplazar el criterio: un puntaje sin contexto no sirve para priorizar.
