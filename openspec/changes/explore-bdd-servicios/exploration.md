# Exploration: `bdd` — servicios e integraciones externas (baseline para refactor)

**Tipo:** exploración standalone — baseline as-is para un futuro change de extracción de `Patoba`/servicios.
**Fecha:** 2026-10-06 · **Rama:** `produccion`
**Fuentes:** lectura directa verificada de `bdd/classes.py` (870 líneas, no 832 como dicen las docs), `bdd/funtions.py` (307), `bdd/management/commands/{procesar_emails,apply_rounding}.py`, `bdd/templatetags/custom_filters.py`, `actualizador/{views.py,actualizador_main.py,actualizador_csv.py,sincronizador.py,task.py,apps.py,management/commands/*}`, `reportes/adapters_patoba.py`, `bdd/views_old.py`, `recrear_descargables.py`, raíz `actualizador_main.py`/`actualizador_csv.py`, `core_config/settings.py`, `utils/{outsider,queryset_to_xlsx}.py`, `scripts/deploy.sh`, `.gitignore`, `git ls-files`. Contexto: las 3 exploraciones previas en `openspec/changes/`.

---

## Current State

### `bdd/classes.py` — inventario completo de `Patoba` (única clase del archivo)

God-class de 870 líneas que mezcla **4 responsabilidades**: fábrica de credenciales OAuth, wrapper de Drive, wrapper de Sheets, y lógica de dominio del pipeline de planillas (pandas + ORM + filesystem).

**`__init__(request)` — `classes.py:33-58`:**
- `request=None` o `request.user` no autenticado → `SocialToken.objects.get(account__user=1)` (**user id=1 hardcodeado**). Si no existe → `DoesNotExist` (falla ruidosa, no silenciosa).
- Con request autenticado → `SocialToken` de ese usuario.
- Construye `Credentials(token, refresh_token, client_id, client_secret, token_uri)` desde el SocialToken y levanta **los 3 servicios siempre**: `gmail_service` (v1), `drive_service` (v3), `sheet_service` (v4) — aunque el caller solo necesite uno.
- `SCOPES` (`:22-29`) se declara pero **nunca se pasa a `Credentials`** → constante muerta; los scopes reales son los del SocialApp de allauth.
- Estado de instancia: `filtro_hojas_descarga` (lista de tabs internas a excluir) e `id_carpeta_pedidos = "1kkoTDNOCbWwzjmTzWOZPR3xVMUAYtYOj"` (**ID de Drive hardcodeado**).
- **Token lifecycle:** `google-auth` auto-refresha el access token dentro de `.execute()` vía `refresh_token`+`token_uri`, pero el token refrescado **nunca se persiste** de vuelta al `SocialToken` → cada proceso re-refreshea. Funciona, pero el token en DB queda stale para siempre.
- **Timeout/retry:** ninguno a nivel Patoba. `desaturar()` (`:257`) es solo `time.sleep(0.07)` como rate-limiter primitivo llamado tras ~10 operaciones. Los loops `MediaIoBaseDownload` no tienen timeout; `requests.get(export_url, headers=…)` en `actualizar_plantilla` (`:734`) tampoco tiene `timeout=` (hang potencial). El único retry real vive en `actualizador_main.py` (`retry_with_backoff`, timeout=600 para descargas BDD/Publico) — fuera de la clase.

**Métodos — inventario con servicio que toca y callers externos:**

| Método | Línea | Servicio | Callers externos reales |
|---|---|---|---|
| `subir_sqlite3_a_drive` | :60 | Drive files | `sincronizador.buckup()` :32 |
| `descargar_sqlite3_de_drive` | :97 | Drive files | `sincronizador.reckup()` :43 |
| `crear_hoja_google_drive` | :126 | Sheets + Drive (mueve a `id_carpeta_pedidos`) | **MUERTO** (solo la llama `filtrar_trabajados`, muerta) |
| `filtrar_trabajados` | :227 | **ORM** (`Item`/`Proveedor`) + Sheets | **MUERTO** (única ref es comentario en `actualizador_csv.py:387`) |
| `desaturar` | :257 | `time.sleep` | interno |
| `listar` | :260 | Drive files | `actualizador_main:449`, `detectar_planillas:84`, raíz `actualizador_main.py:185` |
| `obtener_id_por_nombre` | :272 | Drive files | 9 refs: `views.py:461,465`, `main:610,923`, `csv:821` (+copias raíz) |
| `copiar_reemplazable` | :291 | Drive get_media + pandas + Sheets updateCells | `views.py:493`, `main:771,960` (+raíz) |
| `obtener_id_hoja_por_nombre` | :422 | Sheets get | `views.py:475`, `main:620,933` (+raíz) |
| `obtener_g_sheet_por_id` | :444 | Sheets get | `main:791,1104`, `recrear_descargables:66`, raíz `:357` |
| `copiar_hoja` | :457 | Sheets copyTo | **MUERTO** (única ref es un comentario en `views.py:500`) |
| `eliminar_hoja` | :473 | Sheets batchUpdate | **MUERTO** (solo en bloque comentado `:664-670`) |
| `renombrar_hoja` | :480 | Sheets batchUpdate | **MUERTO** |
| `buscar_copia_por_nombre` | :496 | Drive get+list | interno (de `crear_buscar_copia_descarga`) |
| `actualizar_contenido_copiar` | :504 | Sheets batchUpdate | interno |
| `crear_hoja_por_nombre` | :584 | Sheets batchUpdate | interno |
| `crear_buscar_copia_descarga` | :597 | Drive copy + Sheets read/write | `views.py:503` |
| `download_and_zip_files` | :675 | Drive export/get_media + pandas + ZipFile | `views.py:553` |
| `actualizar_plantilla` | :729 | HTTP export (Bearer token) + pandas + **filesystem (MEDIA_ROOT)** + **ORM (`sp.save()`)** | `main:792,1105`, `recrear_descargables:67`, raíz `:359` |
| `borrar_por_id` | :868 | Drive delete | `main:812,1125`, raíz `:364` |

**Atributos consumidos crudos (bypass total de la capa de métodos):**
- `patoba.drive_service`: `views.py:67`, `detectar_planillas:76` (incl. `.files().delete` crudo :129), `main:418`, `procesar_emails:23`, `adapters_patoba:11`.
- `patoba.sheet_service`: `main:637,663,986,1012`, `csv:834`, `recrear_descargables:34`, `adapters_patoba:68`.
- `patoba.gmail_service`: `main:417`, `procesar_emails:22`.
- `patoba.credenciales.token`: uso interno en `actualizar_plantilla:735`.

**Bugs latentes:** `sheet_rows`/`sheet_columns` quedan **unbound** si el `sheetId` no está en `sheet_properties` → `NameError` (`:373-376` en `copiar_reemplazable`, `:522-528` en `actualizar_contenido_copiar`). `except Exception: pass` en `:325`; bare `except:` en `:452`; `obtener_id_por_nombre` traga todo → `None` (caller no distingue "no existe" de "API caída").

### `bdd/funtions.py` (307 líneas — nombre con typo)

- `armar_tabla(id_carpeta_inbox, id_carpeta_plantillas, credentials)` `:15` — **código muerto roto**: usa `input()` interactivo (inutilizable en server) y `pd.read_excel` con `import pandas` **comentado** (`:5`) → `NameError` si se llamara. Cero callers.
- `EMAIL_NAME_MAPPING` `:100-110` — dict hardcodeado con **emails personales reales** en el repo (reglas: `"subject"` / `"email_name"` / nombre fijo).
- Helpers puros: `extract_name_from_email` `:112`, `extract_email_address` `:134`, `clean_subject` `:147` — solo usados por `get_emails`.
- `_extraer_attachments` `:162` — recorre parts MIME recursivamente, solo `.xls/.xlsx`, baja por `attachmentId`; except por-attachment loggea y sigue.
- `get_emails(gmail_service, drive_service, days_back=1)` `:203` — lista Gmail INBOX `after:` últimas 24h (**sin whitelist de remitente**), extrae adjuntos Excel, renombra por `EMAIL_NAME_MAPPING`/fallback, sube a carpeta `folder_id` **solo si no existe archivo con ese nombre** (preserva fileId). `try/except` por mensaje y por upload con log.
- **Side effect en import:** `folder_id = const.INBOX` `:95` lee settings al importar (requiere Django configurado; queda congelado al valor de ese momento).
- **Callers de `get_emails`:** `actualizador_main.py:73,436` (lazy `_load_django_deps`), `bdd/management/commands/procesar_emails.py:32`, `bdd/views_old.py:18` (import muerto), raíz `actualizador_main.py:20,183` (copia stale).

### `bdd/management/commands/` y `bdd/templatetags/`

- `procesar_emails.py` (33 líneas) — `Patoba(None)` + `get_emails(gmail, drive, days_back=N)`; valida servicios no-nulos. **No hay cron/scheduler que lo invoque** — solo manual.
- `apply_rounding.py` (92 líneas) — batch `Item` × `round_price` con `--dry-run`/`--batch-size`. **No es de servicios** — es housekeeping de dominio mal ubicado en `bdd`.
- `bdd/templatetags/custom_filters.py` (41 líneas) — `zip_lists`, `to_float` (×1.15 IVA + redondeo a 10 — **lógica de precios duplicada distinta de `round_price`**), `en_lista` (**abreviaturas de proveedor hardcodeadas** `/Nc /Dx /B /Cb /3D /F`). Cargado en 5 templates (`descargar_planillas`, `plantilla_tabla` — única que usa `en_lista`+`to_float`, `tabla_listado_carteles_prueva` (sic), `tabla_pedidos`, `tabla_registros`); `zip_lists` no tiene uso visible en templates.
- `actualizador/management/commands/` (fuera de `bdd` pero del slice): `detectar_planillas` (156 líneas — `Patoba(None)`, dedup MD5, cadena xlrd2→xls2xlsx, borra duplicados de Drive) y `procesar_planillas` (wrapper de `procesar_planillas_listas`).

### Acoplamiento — quién instancia `Patoba`

| Consumidor | Sitio | Qué usa realmente |
|---|---|---|
| `actualizador/views.py` | `:66` (GET de `Actualizar`), `:398` (POST) | `drive_service` crudo + pipeline (obtener_id×2, copiar_reemplazable, crear_buscar_copia_descarga, download_and_zip_files) |
| `actualizador/actualizador_main.py` | `:416` (`principal`), `:865` (`procesar_planillas_listas`) — lazy `_load_django_deps` `:53-101` | `gmail_service`+`drive_service` crudos + `listar` + pipeline + `sheet_service` crudo + `borrar_por_id` |
| `actualizador/actualizador_csv.py` | `:802` (`principal_csv`) — lazy import propio | `obtener_id_por_nombre` + `sheet_service` crudo |
| `actualizador/sincronizador.py` | `:31` (`buckup`), `:42` (`reckup`) | solo `subir/descargar_sqlite3_a_drive` + carpeta backup hardcodeada `"1aAipX6U0thSHElqcIV2nsti8738IM2p2"` |
| `actualizador/management/commands/detectar_planillas.py` | `:75` | `listar` + `drive_service` crudo |
| `bdd/management/commands/procesar_emails.py` | `:21` | `gmail_service`+`drive_service` crudos |
| `reportes/adapters_patoba.py` | `:10` — `PatobaDriveAdapter(DrivePort)` | **SOLO credenciales**: usa `drive_service`/`sheet_service` crudos; ningún método de Patoba |
| `recrear_descargables.py` (raíz, one-off) | `:17` | `sheet_service` crudo + `obtener_g_sheet_por_id` + `actualizar_plantilla` |
| Raíz `actualizador_main.py`/`actualizador_csv.py` | `:178`/`:222` | copias **stale divergentes** (374/391 líneas vs 1178/1160 en la app) |
| `bdd/views_old.py` | `:16,18` | imports muertos de `Patoba`+`get_emails` (nunca llamados en el archivo) |
| `pedido`, `facturacion`, `x_cartel`, `administracion_financiera` | — | **cero uso de Patoba** |

Detalle de acoplamiento clave: `actualizador_main`/`actualizador_csv` hacen **lazy-import rebind** (`_Patoba` global + `from bdd.classes import Patoba` dentro de `_load_django_deps()`), diseñado para poder correr como scripts standalone vía `utils/outsider.arrancar_django_config()`. `actualizador/apps.py:ready()` instancia `ColaTareasWorker` al boot (salvo `RUNNING_ACTUALIZADOR_SCRIPT=1` o mgmt commands en `sys.argv`).

### Credenciales — dónde vive cada cosa

- **`SocialToken(user id=1)`** — LA credencial real de todo Google: `Patoba.__init__` (única fuente). Config: `SOCIALACCOUNT_STORE_TOKENS=True` (`settings.py:318`), provider `allauth.socialaccount.providers.google`.
- **`service_credentials.json`** — service account RSA **trackeado en git** (en `git ls-files` aunque también está en `.gitignore` → el ignore no protege lo ya trackeado). **Ningún `.py` lo referencia**; solo `scripts/deploy.sh:33` lo copia fuera del container viejo como backup. Huérfano + secreto filtrado en historia.
- **`token.json`** — no existe en el repo ni se referencia.
- **Folder IDs**: `settings.py:31-33` `INBOX`/`PLANTILLAS`/`DESCARGAR` por env con defaults inseguros; `classes.py:58` pedidos; `sincronizador.py:33` backup — hardcodeados.
- **MercadoPago** (otro servicio externo, fuera de Patoba): `bdd/views/base.py:239-256` — `mercadopago.SDK(mp_token)` leyendo `settings.MP_TOKEN_FILE` (`./mp_access_token.txt`) **dentro de `get_context_data` de la vista base** → token file leído por request cuando `INTEGRATE_MERCADOPAGO` e `INTERNET` están activos (`INTERNET=False` default en `settings.py:226`).

## Affected Areas

- `bdd/classes.py` — la clase entera; el ~35% es código muerto o helpers internos.
- `bdd/funtions.py` — `get_emails` vivo; `armar_tabla` muerto y roto.
- `actualizador/` — consumidor principal (views, main, csv, sincronizador, detectar_planillas, task/apps para el scheduling).
- `reportes/adapters_patoba.py` — solo necesita la fábrica de credenciales.
- `bdd/management/commands/procesar_emails.py` — consume gmail+drive crudos.
- `bdd/management/commands/apply_rounding.py` — no es de servicios (candidato a moverse al dominio).
- `bdd/templatetags/custom_filters.py` — `to_float`/`en_lista` duplican lógica de negocio (precio ×1.15, abreviaturas) fuera de `utils/rounding`.
- `bdd/views_old.py` — imports muertos a eliminar.
- Raíz: `actualizador_main.py`, `actualizador_csv.py`, `recrear_descargables.py`, `service_credentials.json`, `{Proveedor}.csv` — residuos del pipeline.
- `scripts/deploy.sh`, `.gitignore`, historia de git — `service_credentials.json` trackeado.

## Approaches

1. **A. Extracción directa con shim (recomendada)** — mover `Patoba` a `services/google/` (o `core_google/`) split por servicio + dejar `bdd/classes.py` como re-export temporal.
   - Pros: rompe el acoplamiento bdd↔automatización sin big-bang; `reportes` ya demuestra que solo hace falta la fábrica de credenciales; la clase es casi ORM-free (ver abajo).
   - Cons: hay que tocar los ~10 sitios de import + la maquinaria lazy `_load_django_deps`.
   - Effort: Medium.
2. **B. Ports/adapters primero** — definir `DrivePort`/`SheetsPort`/`GmailPort` (extender lo de `reportes`) y reimplementar adapters sin heredar la clase.
   - Pros: interfaz mínima por consumidor (sincronizador necesita 2 métodos, reportes 0 métodos de Patoba); testeable con fakes.
   - Cons: más diseño upfront; dos capas conviviendo hasta migrar consumidores.
   - Effort: Medium-High.
3. **C. Solo limpieza in-place** — borrar métodos muertos (`filtrar_trabajados`, `crear_hoja_google_drive`, `copiar_hoja`, `eliminar_hoja`, `renombrar_hoja`, `armar_tabla`, `SCOPES`), `Patoba(user_id)`, timeouts.
   - Pros: Low effort, reduce la superficie antes de decidir extracción.
   - Cons: `bdd` sigue siendo god-app.
   - Effort: Low.

## Recommendation

**A con pre-paso C.** La extracción es más fácil de lo que sugiere el tamaño: `classes.py` solo importa `Item`/`Proveedor` para el método **muerto** `filtrar_trabajados` — borrando los ~6 métodos muertos, `Patoba` queda 100% libre de ORM (`actualizar_plantilla` usa `sp.save()` duck-typed, sin import de modelo). Mapa de extracción propuesto:

| Grupo | Métodos | Módulo destino | Consumidores |
|---|---|---|---|
| **Credenciales** | `__init__`, `SCOPES`, `desaturar` | `services/google/auth.py` (`build_google_services(user_id\|request)`) | todos; `reportes` usa SOLO esto |
| **Drive files** | `listar`, `obtener_id_por_nombre`, `borrar_por_id`, `subir/descargar_sqlite3`, `buscar_copia_por_nombre`, `download_and_zip_files` | `services/google/drive.py` | actualizador (main/detectar/views), sincronizador, procesar_emails |
| **Sheets** | `obtener_id_hoja_por_nombre`, `obtener_g_sheet_por_id`, `crear_hoja_por_nombre`, `actualizar_contenido_copiar` (+muertos: copiar/eliminar/renombrar/crear_hoja_google_drive) | `services/google/sheets.py` | main, views, csv, recrear_descargables |
| **Pipeline planillas** (dominio, mezcla todo+pandas+ORM+FS) | `copiar_reemplazable`, `crear_buscar_copia_descarga`, `actualizar_plantilla` | `actualizador/services/planilla_sync.py` — NO en services/google | main (×2), views POST, recrear_descargables |
| **Pedidos→Sheets** | `filtrar_trabajados`, `id_carpeta_pedidos` | ELIMINAR (muerto) o `pedido/` si se revive | ninguno |
| **Gmail ingest** | `get_emails` + helpers + `EMAIL_NAME_MAPPING` | `actualizador/services/email_ingest.py` (param `inbox_id`, no global) | main paso 1, procesar_emails |

**Qué se rompe si Patoba sale de `bdd`:** los 10 `from bdd.classes import Patoba` (7 sitios reales + lazy-imports + views_old muerto + copias raíz) — mitigable con re-export shim; la maquinaria `_load_django_deps` hay que repuntarla; nada más. La dirección de dependencia se invierte sanamente: `actualizador → services.google` en vez de `actualizador → bdd.classes`.

## Risks

- **Secreto trackeado:** `service_credentials.json` (RSA private key de service account) está en git — debe rotarse y purgarse de historia, no solo gitignorarse. `EMAIL_NAME_MAPPING` expone emails personales reales.
- **Single point of failure OAuth:** todo el pipeline (emails, detección, procesamiento, backup, reportes) depende del `SocialToken` del user 1; el refresh nunca se persiste — si Google revoca el refresh token, se cae toda la automatización de golpe.
- **`requests.get` sin timeout** en `actualizar_plantilla` + loops `MediaIoBaseDownload` sin timeout → cuelgues indefinidos en el worker nocturno.
- **Excepts que tragan errores:** `obtener_id_por_nombre`→None indistingible, bare `except:` en `obtener_g_sheet_por_id`, `except: pass` en `:325`; bugs `sheet_rows` unbound.
- **GET destructivo:** `Actualizar.get_context_data` (`views.py:66-263`) hace trabajo de Drive en GET y borra registros/archivos — instanciar Patoba por request con credenciales del usuario logueado es frágil si ese user no tiene SocialToken.
- **Duplicados divergentes en raíz** (`actualizador_main.py`/`actualizador_csv.py`, ~1/3 del tamaño real): importan `bdd.classes`/`bdd.funtions` y pueden ejecutarse contra DB real.
- **`funtions.py` lee `settings.INBOX` a nivel módulo** — el folder queda congelado al primer import; tests o scripts con settings distintos heredan el valor viejo.

## Ready for Proposal

**Sí — para un change acotado.** El alcance natural del primer change: (1) borrar código muerto de `classes.py`/`funtions.py` + imports muertos de `views_old.py` (C), (2) extraer `Patoba`→`services/google/` con shim de re-export (A), dejando el pipeline de dominio en `actualizador/services/`. Antes de proponer, el orquestador debería confirmar con el usuario si también entra el saneamiento de credenciales (`service_credentials.json` fuera de git + rotación) — es trabajo separado pero urgente.
