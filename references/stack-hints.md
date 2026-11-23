# Funciones peligrosas por lenguaje y framework

Puntos donde un dato del usuario se vuelve peligroso. Encontrar uno es una **pista**: después hay que
trazar si el dato puede venir de un atacante (ver SKILL.md, paso 3).

Comando base para buscar sin perderse en dependencias:

```bash
rg -n --hidden -g '!node_modules' -g '!vendor' -g '!.venv' -g '!dist' -g '!*.min.js' 'PATRON' .
```

## Python (Flask, Django, FastAPI)

| Riesgo | Buscar |
|---|---|
| SQL | `execute(f"`, `execute("..." %`, `.format(` dentro de SQL, `text(f"`, `.raw(`, `.extra(` |
| Comandos | `os.system`, `os.popen`, `subprocess.*(..., shell=True)`, `commands.` |
| Código / deserialización | `eval(`, `exec(`, `pickle.loads`, `yaml.load(` sin `SafeLoader`, `marshal.loads`, `jsonpickle` |
| SSTI / XSS | `render_template_string`, `Markup(`, `\|safe`, `mark_safe`, `autoescape false` |
| Archivos | `open(` / `send_file(` / `os.path.join(` con datos de `request`; `zipfile.extractall` (zip slip) |
| SSRF | `requests.get(`, `httpx.`, `urllib.request.urlopen(` con URL de `request` |
| Autorización | rutas sin `@login_required` / `Depends(get_current_user)` / `permission_classes`; `get_object_or_404(Model, pk=pk)` sin filtrar por usuario |
| Configuración | `DEBUG = True`, `app.run(debug=True)`, `SECRET_KEY = "`, `ALLOWED_HOSTS = ["*"]`, `CORS(app, supports_credentials=True, origins="*")` |
| Cripto | `hashlib.md5(`/`sha1(` sobre contraseñas, `random.` para tokens, `verify=False`, `jwt.decode(..., options={"verify_signature": False})` |

## JavaScript / TypeScript (Node, Express, Next.js, NestJS)

| Riesgo | Buscar |
|---|---|
| SQL / NoSQL | template literals en `query(`/`raw(`, `$where`, `find(req.body)`, `findOne({ ...req.query })` |
| Comandos | `child_process.exec(`, `execSync(`, `spawn(..., { shell: true })` |
| Código | `eval(`, `new Function(`, `vm.runInNewContext(`, `setTimeout("string"` |
| XSS | `dangerouslySetInnerHTML`, `innerHTML =`, `outerHTML`, `document.write`, `v-html`, `res.send(` con HTML armado |
| Prototype pollution | merges recursivos con datos del usuario (`_.merge`, `Object.assign` profundo), claves `__proto__` |
| Archivos | `res.sendFile(`/`fs.readFile(` con `req.params`; `path.join` sin verificar que siga dentro de la carpeta base |
| SSRF | `fetch(req.`, `axios.get(req.`, `got(` |
| Autorización | rutas registradas antes del middleware de auth; `app.use(auth)` aplicado a un router y no a otro |
| Configuración | `cors({ origin: true, credentials: true })`, `NODE_ENV` sin definir, `helmet` ausente (informativo) |
| Cripto / JWT | `Math.random()` para tokens, `jwt.verify` sin `algorithms`, `jwt.decode` usado como verificación, `rejectUnauthorized: false` |

## Go

| Riesgo | Buscar |
|---|---|
| SQL | `fmt.Sprintf` dentro de `Query(`/`Exec(`, concatenación en SQL |
| Comandos | `exec.Command("sh", "-c", ...)`, `exec.Command("bash", "-c", ...)` |
| Plantillas / XSS | `text/template` para HTML (en lugar de `html/template`), `template.HTML(` con datos del usuario |
| Archivos | `os.Open(`/`http.ServeFile(` con datos de la petición; `filepath.Join` sin verificar el prefijo |
| SSRF | `http.Get(` con URL del usuario |
| Cripto | `math/rand` para tokens, `InsecureSkipVerify: true`, `md5.Sum` sobre contraseñas |
| Errores | `if err != nil { }` vacío en verificaciones de seguridad, `_ = verify(...)` |

## Java (Spring)

| Riesgo | Buscar |
|---|---|
| SQL | `createQuery("..." +`, `Statement.execute`, `@Query` con concatenación, `JdbcTemplate` con `+` |
| Comandos | `Runtime.getRuntime().exec(`, `ProcessBuilder` con datos del usuario |
| Deserialización | `ObjectInputStream.readObject`, `XMLDecoder`, Jackson con `enableDefaultTyping` |
| XXE | `DocumentBuilderFactory`, `SAXParserFactory` sin deshabilitar entidades externas |
| SpEL / plantillas | `SpelExpressionParser().parseExpression(` con datos del usuario |
| Autorización | `@PreAuthorize` ausente en un método de un controlador protegido, `permitAll()` amplio en `SecurityFilterChain` |

## PHP (Laravel, WordPress)

| Riesgo | Buscar |
|---|---|
| SQL | `DB::raw(`, `whereRaw(` con variables, `mysqli_query(` con concatenación, `$wpdb->query(` sin `prepare` |
| Comandos / código | `system(`, `exec(`, `shell_exec(`, `passthru(`, backticks, `eval(`, `assert(` |
| Deserialización | `unserialize(` con datos del usuario |
| Inclusión | `include`/`require` con variables (LFI/RFI) |
| XSS | `{!! $var !!}` en Blade, `echo $_GET[...]` |

## Infraestructura y CI

| Riesgo | Buscar |
|---|---|
| Docker | `FROM ...:latest`, `USER root` o sin `USER`, `curl ... \| sh`, secretos en `ENV`/`ARG` |
| Compose / K8s | `privileged: true`, puertos de bases de datos publicados, `hostNetwork`, `allowPrivilegeEscalation` |
| GitHub Actions | `pull_request_target` + checkout del PR, `${{ github.event.* }}` interpolado en `run:` (inyección), Actions sin fijar por SHA, `permissions: write-all` |
| Terraform | buckets públicos, `0.0.0.0/0` en grupos de seguridad, cifrado deshabilitado |
