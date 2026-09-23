# Exploration: Entorno de test separado — estado actual y opciones

**Tipo:** exploración standalone (sin change asociado) — evalúa cómo separar el entorno de test de producción Y de los datos de desarrollo.
**Fecha:** 2026-09-23 · **Rama:** `produccion` (v3.10.x)
**Fuentes:** verificación directa del código y del entorno local (Fedora, venv/, `pytest --collect-only`), git history de `settings_tests.py`, `openspec/changes/explore-arquitectura-monolito/exploration.md`.

---

## Current State

### Qué pasa HOY al correr `pytest`

1. `pytest.ini:5` fija `DJANGO_SETTINGS_MODULE = core_config.settings` → los tests corren con **las settings reales** (env-based, gitignored). No existe settings de test activa.
2. Sin `DB_HOST` en el entorno (verificado: no está exportado en esta máquina) → `settings.py:373-379` elige SQLite `db.sqlite3` (la copia local de ~40MB de datos de prod).
3. **PERO los datos reales ya están aislados por accidente, no por diseño:** pytest-django usa la maquinaria de test DB de Django, que para SQLite crea `file:memorydb_default?mode=memory&cache=shared` (verificado en `django/db/backends/sqlite3/creation.py` del venv). Los 9 tests `@pytest.mark.django_db` (que escriben via `ddf G()`) corren en una DB en memoria que se migra desde cero. `db.sqlite3` **no se toca** (mtime sin cambios tras `--collect-only` de los 45 tests).
4. Suite real: 45 tests — `tests/test_rounding.py` (~33 parametrizados de función pura `round_price`), `tests/articulos/test_articulo.py` (8, factories ddf), `tests/facturacion/test_facturacion.py` (1, `G(Cliente)`). Ninguno hace requests HTTP, `reverse()`, ni instancia `Patoba`/websocket/Drive → **cero contacto con servicios externos hoy**.
5. Sin conftest raíz ni `tests/conftest.py` — solo `tests/articulos/conftest.py` y `tests/facturacion/conftest.py` (fixtures con `G()`). Sin `__init__.py` en `tests/` (namespace packages). `tests/app_*` y `tests/facturacion/{test_models,utils}` son solo residuo de `__pycache__` (tests borrados).

### Side-effects reales de importar `core_config.settings` en pytest

- `settings.py:52` → `os.makedirs(LOGS_DIR_BASE)` y `log_config.py:24` → `os.makedirs` por app: crea `logs/{facturacion,bdd,actualizador,x_cartel}/` si no existen.
- Los `RotatingFileHandler` de LOGGING abren archivos reales en `logs/` durante el run (escritura en `logs/main.log`, `logs/<app>/info.log`, etc.).
- `settings.py:25,35` → `IP_BEW_SOCKET` default `ws://192.168.1.119:12000/ws` → **impresora fiscal real de la LAN** queda configurada como default en tests.
- `settings.py:31-33` → `INBOX`/`PLANTILLAS`/`DESCARGAR` con **IDs reales de carpetas Drive** como defaults.

### Historia relevante: `settings_tests.py` ya existió

`.gitignore:23` lista `core_config/settings_tests.py` y el archivo no existe en disco — pero `git show b215453:core_config/settings_tests.py` (commit de jul-2025 que lo destaqueó) muestra que era una copia completa del settings.py de entonces con:
- `DATABASES` → `sqlite3` en `core_config/db_test.sqlite3` (archivo, no `:memory:`),
- `IP_BEW_SOCKET = ws://127.0.0.1:12000/ws` (override a localhost — la idea correcta),
- **pero con los mismos IDs reales de Drive hardcodeados** (INBOX/PLANTILLAS/DESCARGAR).

Es decir: ya hubo un intento de entorno separado, se abandonó al gitignorear settings, y además nunca resolvió el aislamiento de Drive.

### Riesgos latentes (hoy no se disparan, pero el entorno actual no los previene)

1. **`DB_HOST` exportado** → Django intentaría crear `test_<DB_NAME>` en ese Postgres. Si apunta al servidor de la migración staged (o peor, a prod), pytest tocaría infra real.
2. **`bdd/urls.py` consulta `NavBar`/`Armador` en import-time** → el primer test que use `client`/`reverse()` carga `ROOT_URLCONF` → queries contra la test DB vacía → el `except: pass` traga todo → URLs inexistentes → 404s silenciosos difíciles de diagnosticar.
3. **Instanciar `Patoba`** en un test → `SocialToken.objects.get(account__user=1)` contra test DB → `DoesNotExist` (fail ruidoso, no write a Drive). Pero cualquier ejecución fuera de pytest-django (scripts de raíz como `reset_pass.py`, `script.py`, `cargar_datos_csv.py` — todos fijan `DJANGO_SETTINGS_MODULE=core_config.settings` y usan `db.sqlite3` real) sí tiene credenciales reales disponibles.
4. **`TicketFactura`/`conectar_a_websocket`** → socket real a la impresora LAN si un test los alcanza.
5. `bdd/classes.py` no tiene side-effects en import (Patoba solo se instancia explícito) y los `admin.py` solo importan modelos → `django.setup()` es seguro hoy.

### Infra / tooling

- Docker: `docker-compose.yml` (postgres:16-alpine + web `ferreteria_web:latest`) + `.env.production` (IDs Drive reales, solo lo consume compose via `env_file:` — settings no carga dotenv) + `entrypoint.sh` (migrate + collectstatic + gunicorn). **No existe compose de test.** Prod real = contenedor viejo `django_server` con SQLite en RPi; la migración a Postgres está staged pero nunca ejecutada.
- Sin CI. Sin coverage (`htmlcov/` es residuo de jul-2025; `.coverage` y `*,cover` se borraron del repo en b215453). `black 26.1.0` en venv sin pin.
- **Drift venv vs requirements.txt:** venv tiene `pytest 8.4.1`/`pytest-django 4.11.1` (requirements: 8.3.2/4.8.0) y además `djangorestframework`, `django-filter`, `django-cors-headers`, `django-extensions` que no están en requirements.txt (no están en INSTALLED_APPS, no afectan tests, pero el venv no es reproducible desde requirements).

## Affected Areas

- `pytest.ini` — apunta a settings reales; es el switch principal del entorno de test.
- `core_config/settings.py` — side-effects en import (makedirs, handlers de archivo, defaults con IDs reales); a respetar o encapsular.
- `core_config/settings_tests.py` — nombre gitignored (línea 23); un settings de test commiteado necesita **otro nombre** o tocar `.gitignore`.
- `tests/` — conftests por directorio; falta conftest raíz para guardas de aislamiento.
- `bdd/classes.py` (Patoba), `bdd/urls.py` (query en import), `facturacion/classes.py`/`cliente.py` (websocket fiscal) — superficies a bloquear/mockear en tests.
- `docker-compose.yml` / `.env.production` — base para la opción B; nunca cargar `.env.production` en pytest.
- `requirements.txt` — drift con venv; un settings_test commiteado debería venir con pinning de pytest/pytest-django.
- `openspec/config.yaml` — `testing.workspace_test_command: "pytest"` y rules verify/apply referencian el comando; si cambia el settings module o se agrega compose de test, actualizar.

## Approaches

| Enfoque | Pros | Cons | Esfuerzo |
|---------|------|------|----------|
| **A. `settings_test.py` commiteado + conftest de guardas** | Cero infra nueva; rápido (`:memory:`); deps ya instaladas; matchea prod actual (SQLite); commiteable sin secretos; resuelve de raíz logs/Drive/printer | Diverge del futuro Postgres; no valida comportamientos específicos de engine ni migraciones Postgres | **Low** |
| **B. `docker-compose.test.yml` con Postgres 16** | Paridad con el destino Postgres; valida migraciones reales; aislamiento total | Más lento (migrations por run o `--reuse-db`); requiere Docker en Fedora; dos engines a mantener; overkill sin CI | **Medium** |
| **C. Híbrido: settings_test commiteado, default SQLite `:memory:` + rama `DB_HOST` opcional** | Default rápido hoy; un solo archivo de settings sirve local y futuro CI/Postgres descartable; camino incremental | Ligera complejidad condicional; la rama Postgres puede quedar sin ejercitar ("works on sqlite") | **Low-Medium** |

Detalle de **A**: `core_config/settings_test.py` (nombre nuevo — `settings_tests.py` con "s" está gitignored) con `from .settings import *` y overrides: `DATABASES['default'] = sqlite3 :memory:` (+ `TEST: {'NAME': ':memory:'}` explícito), `DEBUG=False`, `SECRET_KEY` dummy fija, `INBOX/PLANTILLAS/DESCARGAR='test-*'`, `IP_BEW_SOCKET='ws://127.0.0.1:1/ws'` (puerto muerto), `LOG_DIR`/`MEDIA_ROOT` a `tmp`. `pytest.ini` → `DJANGO_SETTINGS_MODULE = core_config.settings_test`. Más `tests/conftest.py` (o raíz) con guardas autouse: bloquear `socket.socket` (o dep `pytest-socket`), fixture que haga fallar `bdd.classes.Patoba` y `googleapiclient.discovery.build`, y `settings.INTERNET=False` ya existe como flag (línea 226) reutilizable como guarda semántica.

Detalle de **C**: igual que A pero `settings_test.py` conserva la rama `if os.getenv('DB_HOST')` apuntando a Postgres — documentada para correr contra un contenedor descartable (`docker run postgres:16` efímero o service de compose override) cuando se quiera validar paridad, y sería la base natural del job de CI cuando exista.

## Recommendation

**Ahora: A implementada con el diseño de C.** Es decir, `settings_test.py` commiteado que por default use SQLite `:memory:` pero respete `DB_HOST` si está seteado — así el mismo archivo sirve para el run rápido local hoy y para validar contra Postgres descartable cuando la migración a prod se concrete o llegue CI. B como compose dedicado se posterga: sin CI no hay consumidor que justifique el peso.

Las guardas en conftest son parte esencial del alcance, no opcional: lo que hoy es seguro "porque nadie escribió el test" debe volverse seguro "porque el entorno lo impide".

**Para que los tests NUNCA toquen Drive/datos reales se necesita:**
1. `settings_test.py` sin IDs reales de Drive, `IP_BEW_SOCKET` a destino muerto, `LOG_DIR`/`MEDIA_ROOT` a tmp.
2. `conftest.py` raíz con guardas autouse: sockets bloqueados + `Patoba`/`build()` prohibidos (monkeypatch que levante `RuntimeError` descriptivo).
3. Mantener la regla "pytest nunca carga `.env.production` ni dotenv" (hoy se cumple: settings usa `os.getenv` puro — documentarla para no regresarla).
4. `TEST: {'NAME': ':memory:'}` explícito aunque sea el default, como seguro contra overrides.
5. Opcional: marker `FERRETERIA_ENV=test` + guarda en `Patoba.__init__` que rechace correr bajo ese flag con SocialToken real.

## Risks

- **Naming trap:** crear `core_config/settings_tests.py` (con "s") cae en `.gitignore:23` → el archivo quedaría invisible a git silenciosamente. Usar `settings_test.py` o quitar la línea del gitignore.
- Herencia `from .settings import *` arrastra los side-effects de import (makedirs, handlers de archivo reales) → minimizar apuntando `LOG_DIR`/`MEDIA_ROOT` a tmp antes, o aceptar que `logs/` se ensucie (ya gitignored).
- `bdd/urls.py` import-time DB query sigue siendo trampa para futuros view tests — la guarda no lo arregla, solo hay que saberlo (fix real = change separado de deuda).
- Si alguien exporta `DB_HOST` (ej. ensayo de migración Postgres) y corre `pytest` con las settings actuales → Django crea `test_*` en ese servidor. Con `pytest.ini` fijado a `settings_test` este riesgo desaparece del camino default.
- Drift venv vs `requirements.txt` (pytest 8.4.1 vs 8.3.2 pinned, DRF/filter/cors sueltos): el entorno commiteado debería acompañarse de re-pin o documentación del drift.
- Los scripts de raíz (`reset_pass.py`, `script.py`, `cargar_datos_csv.py`, `actualizador_*.py`) seguirán usando settings reales + `db.sqlite3` real — fuera del scope de pytest pero mismo patrón de riesgo; no los cubre este change.

## Ready for Proposal

**Sí.** Alcance claro y de bajo riesgo: change SDD viable tipo "entorno de test separado" = `settings_test.py` commiteado (A con diseño de C) + `pytest.ini` apuntado + `conftest.py` raíz con guardas de aislamiento + re-pin de pytest/pytest-django en requirements + actualizar `openspec/config.yaml` (test_command / known_issues) + limpieza de residuo `__pycache__` en `tests/`. El orquestador puede lanzar `sdd-propose` con este documento como contexto. La opción B (compose de test) queda como follow-up documentado para cuando exista CI o se concrete la migración Postgres en prod.
