# Exploration: Flujo ACTUAL de etiquetado de artículos nuevos en Drive (as-is)

**Tipo:** exploración standalone (sin change asociado) — safety baseline antes de tocar el pipeline de planillas.
**Fecha:** 2026-10-06 · **Rama:** `produccion`
**Fuentes:** lectura directa de código (verificado 2026-10-06): `actualizador/{task.py,actualizador_main.py,actualizador_csv.py,sincronizador.py,views.py,urls.py,apps.py}`, `actualizador/management/commands/{detectar_planillas,procesar_planillas}.py`, `actualizador/templates/actualizar.html`, `bdd/{classes.py (Patoba),funtions.py (get_emails),models.py,views/base.py}`, `facturacion/views.py` (CierreZ), `core_config/settings.py`, `.env.production`, git log de `actualizador/`.

---

## Current State

### Glosario operativo — qué es "etiquetado" acá

El código usa "etiquetado" en **dos sentidos distintos**, y conviene no confundirlos:

1. **Etiquetado de planillas (humano, en `/actualizar/`):** asignar a cada archivo entrante del Inbox de Drive su `proveedor` + `hoja` y marcarlo `listo=True`. Es el paso manual obligatorio del pipeline. El tab de la UI se llama literalmente *"Email de hoy y etiquetado"* (`actualizar.html:18`).
2. **Hoja "Etiquetado" dentro de cada plantilla de Drive:** cada Google Sheet plantilla (carpeta `PLANTILLAS`) tiene tabs internas: `Reemplazable`, `Intermedio`, `Diccionario`, `BDD`, `Publico`, `Etiquetado`. Su lógica es **fórmulas de Google Sheets**, no código Django — el código solo las filtra de los descargables (`bdd/classes.py:50-56` `filtro_hojas_descarga`, y `classes.py:730`). Ahí es donde, por convención del negocio, se marcan/listan artículos nuevos o cambiados para imprimir etiquetas/carteles. El monolito NO escribe ni lee esa hoja.

### Pipeline end-to-end (as-is)

```
Gmail INBOX (adjuntos .xls/.xlsx de proveedores, últimas 24h)
   │  get_emails() — bdd/funtions.py:203  [AUTOMÁTICO]
   ▼
Drive carpeta INBOX (env INBOX; default 15yv7_…, prod 1JtiLUv_…)
   │  detección: principal() paso 2  o  manage.py detectar_planillas
   ▼
Listado_Planillas(identificador=fileId, descripcion=nombre, listo=False, descargar=False)
   │  lectura de hojas → campo `hojas` (";"-join) + file_hash (solo en detectar_planillas)
   ▼
UI /actualizar/ — tab "Email de hoy y etiquetado"   [MANUAL: el "etiquetado"]
   │  checkbox elemento_seleccionado="{id}:{n}" + select proveedor_{id} + select hoja_{id}
   │  POST → bulk_update(listo=True, proveedor, hoja)
   ▼
Procesamiento (nightly 21:00 vía principal() paso 5, o manage.py procesar_planillas)
   │  por cada planilla listo=True con proveedor válido (≠ "Otros"):
   │    plantilla = proveedor.identificador.nombre  (ListaProveedores)
   │    → copiar_reemplazable(): hoja elegida del xls → tab "Reemplazable" del GSheet
   │    → fórmulas del GSheet propagan a Intermedio/BDD/Publico/Etiquetado (en Drive)
   │    → descargar rango "BDD" → {Plantilla}.csv en cwd (raíz del repo)
   │    → validar hoja "Publico" (Codigo/Descripcion/Publico no vacías)
   │    → buscar_modificar_registros_lotes(csv, abreviatura, proveedor) → Item
   │    → actualizar_plantilla(): exporta GSheet → MEDIA_ROOT/descargas/
   │       {Plantilla}-{fecha}.xlsx + .ods (SIN tabs internas) → link_descarga*, descargar=True
   │    → borrar_por_id(archivo Inbox) + ListaProveedores.hay_csv_pendiente=True
   ▼
principal_csv() — segunda pasada para hay_csv_pendiente=True
   │  re-descarga BDD → re-procesa CSV → hay_csv_pendiente=False
   ▼
buckup() — sube db.sqlite3 a Drive (carpeta hardcodeada 1aAipX6U0thSHElqcIV2nsti8738IM2p2)
```

### Disparadores (4 caminos)

| Trigger | Entrada | Qué corre |
|---|---|---|
| **Cierre Z** | POST `/vista_cierre_z/` → `facturacion/views.py:760` → `agregar_tareas_en_cola()` | `principal` + `principal_csv` + `buckup`, encoladas en `ColaTareasWorker` (hilo daemon singleton) que **espera hasta las 21:00** (`task.py:265-274, 299-313`). Si ya pasaron las 21:00, corren de inmediato. |
| **Actualizar ahora** | GET `/actualizar/ahora/` → `ActualizarAhora` (`views.py:40-56`) | Misma cola con `hora_inicio = ahora + 1min`. |
| **Comandos manuales** | `manage.py detectar_planillas` / `procesar_planillas` | Detección (con dedup por hash) / procesamiento de `listo=True`, respectivamente. Sin emails en `procesar_planillas`. |
| **Interactivo** | POST `/actualizar/` con `actualizar_planillas=True` (`views.py:391-569`) | Variante síncrona en-request: copia a `Reemplazable`, `crear_buscar_copia_descarga` en carpeta DESCARGAR, opcional ZIP (`download_and_zip_files`). No toca Items ni genera locales. |

Además `actualizador/apps.py:ready()` instancia el `ColaTareasWorker` al boot (salvo en comandos de management listados o `RUNNING_ACTUALIZADOR_SCRIPT=1`).

### "Proveedores en automático" vs manual

- **Automático** = solo la **llegada y detección**: `get_emails` baja adjuntos `.xls/.xlsx` de Gmail (últimas 24h, `days_back=1`), los renombra por `EMAIL_NAME_MAPPING` hardcodeado (`funtions.py:100-110`: sender→`"subject"`/`"email_name"`/string fijo; fallback = prefijo del email limpiado) y los sube a `INBOX` **si no existe ya un archivo con ese nombre** (preserva el fileId). Luego la detección crea filas `Listado_Planillas` y precarga `hojas`. **Nada asigna proveedor automáticamente** — el vínculo planilla→proveedor→plantilla es 100% manual en la UI.
- **Manual/plantilla** = el etiquetado propiamente dicho: la planilla queda `listo=True` solo cuando un humano le asignó `proveedor` y `hoja`. La plantilla de Drive se resuelve por `proveedor.identificador` (FK `Proveedor.identificador → ListaProveedores`; `ListaProveedores.nombre` = nombre exacto del Google Sheet en carpeta `PLANTILLAS`). Proveedor sin `identificador` o con nombre `"Otros"` → la planilla se salta con warning (`actualizador_main.py:587-591`).

### Qué pasa por cada plantilla (procesamiento)

Dos bloques casi idénticos de ~290 líneas hacen esto: `principal()` paso 5 (`actualizador_main.py:562-856`) y `procesar_planillas_listas()` (`:859-1169`). **Difieren en el orden**: `procesar_planillas_listas` copia a `Reemplazable` ANTES de leer `BDD` (orden correcto, fix `2c2b0d6`); `principal()` lee `BDD` ANTES de copiar (lee datos viejos). La segunda pasada `principal_csv()` compensa: como `hay_csv_pendiente=True` queda seteado, re-descarga `BDD` ya actualizado esa misma noche.

1. Resuelve `id_archivo_plantilla` por nombre en `PLANTILLAS` y `id_hoja_reemplazable` (tab "Reemplazable") por sheetId.
2. `copiar_reemplazable` (`classes.py:291-420`): descarga el xls/xlsx del Inbox, lee la `hoja` elegida con pandas, y **sobrescribe** la tab "Reemplazable" vía `updateCells` (todo como `stringValue`; expande filas si hace falta). Maneja `.xls` vía xlrd2 → fallback xls2xlsx.
3. Descarga rango `BDD` (timeout 600s, `retry_with_backoff` 5 intentos) → escribe `{Plantilla}.csv` en el cwd (los `*.csv` de la raíz del repo — `Maglia.csv`, `Cedica.csv`, etc. — son artefactos de este paso).
4. Valida hoja `Publico`: columnas `Codigo`, `Descripcion`, `Publico` presentes y con datos. Si fallan → `error_columnas`, `descargar=True`, `listo=False`, sin links (la UI muestra "Corregir en Drive").
5. `buscar_modificar_registros_lotes(csv, abreviatura, proveedor_obj)` (`actualizador_csv.py:711`): `desactualizar_anteriores(abreviatura)` marca `actualizado=False` a Items `codigo__endswith=abreviatura` (el código del artículo lleva la abreviatura del proveedor como sufijo) → descuento efectivo opcional (`ACT_CSV_EFECTIVO_DESCUENTO_PCT`) → `round_price` → `bulk_create`/`bulk_update` (nunca toca `factor_division`) → `recompute_finales_para_codigos`. **Artículos nuevos** = `Item` creados por `bulk_create` con `actualizado=True` y `proveedor` seteado (solo en la 1ª pasada; en `principal_csv` se llama sin `proveedor_obj` → quedan con `proveedor=None`).
6. `actualizar_plantilla` (`classes.py:729-866`): exporta el GSheet a xlsx vía HTTP con el token OAuth, lo re-escribe con pandas a `MEDIA_ROOT/descargas/{Plantilla}-{fecha}.xlsx` y `.ods` **excluyendo** `Reemplazable/Intermedio/Diccionario/Etiquetado/BDD`, setea `link_descarga`, `link_descarga_ods`, `descargar=True`, y limpia pares fechados viejos + el temporal sin fecha.
7. `patoba.borrar_por_id(id_archivo_proveedor)` — el xls original del Inbox se **borra de Drive**.
8. `ListaProveedores.hay_csv_pendiente=True` → `marcar_revisar_carteles(proveedor.id)` pone `revisar=True` en `x_cartel.Carteles`/`CartelesCajon` del proveedor (cola de re-impresión de carteles — esto es lo más cercano a "etiquetar artículos" en la BD).

### Flags de `Listado_Planillas` (bdd/models.py:578-615)

| Campo | Semántica real |
|---|---|
| `identificador` | Drive fileId del archivo en Inbox (unique). |
| `descripcion` | Nombre del archivo en Drive. |
| `hojas` | `";"`-join de nombres de hojas (con entrada vacía inicial). Cache para no re-descargar en la UI (fix `7104f37`). |
| `hoja` | Hoja elegida por el humano para copiar a `Reemplazable`. |
| `proveedor` | Asignado manualmente en `/actualizar/`. |
| `listo` | "Etiquetada, lista para procesar". Se apaga tras procesar o ante errores. |
| `descargar` | "Tiene descargables generados" (o error de columnas). La pone `actualizar_plantilla` o el chequeo de `Publico`. |
| `id_sp` | spreadsheetId de la plantilla (para link "Corregir en Drive"). |
| `link_descarga` / `link_descarga_ods` | Rutas relativas `media/descargas/…` al xlsx/ods local. |
| `file_hash` | MD5 del contenido, para dedup (solo lo llena `detectar_planillas`). |
| `error_columnas` | Columnas vacías detectadas en `Publico`. |
| `descargado` / `fecha_descarga` / `usuario_descarga` | Tracking de descarga por el usuario (AJAX `MarcarDescargado`, `views.py:612-648`). |

### Estado de "etiquetado" en la UI

- Badge navbar: `nuevas_planillas` = count(`listo=False, descargar=False`) y `nuevas_planillas_descarga` = count(`descargar=True, descargado=False`) (`bdd/views/base.py:215-223`).
- Tab "Actualizar" muestra `listo=True, descargar=False` (en espera del script nocturno). Tab "Descargar" muestra `descargar=True` con links XLS/ODS o botón "Corregir en Drive".
- Ojo: el GET de `Actualizar` hace trabajo pesado y **destructivo**: descarga de Drive cada planilla sin `hojas` cacheadas, borra filas con 404, y **borra registros + archivos físicos de todas las planillas que no sean la más reciente por proveedor** (`views.py:202-263`).

## Affected Areas

- `actualizador/actualizador_main.py` — `principal()` (orquestador nightly + procesamiento `listo=True` con orden BDD-antes-de-copiar) y `procesar_planillas_listas()` (duplicado con orden corregido). Líneas clave: 410-856, 859-1169.
- `actualizador/management/commands/detectar_planillas.py` — detección standalone: crea `Listado_Planillas`, dedup MD5 (`:115-135`), xlrd2→xls2xlsx (`:12-63`), borra duplicados de Drive.
- `actualizador/management/commands/procesar_planillas.py` — wrapper del procesamiento.
- `actualizador/views.py` + `templates/actualizar.html` — la UI de etiquetado (selects `proveedor_{id}`/`hoja_{id}`, fix desfase `80c642e`), rama interactiva de procesamiento, `MarcarDescargado`.
- `actualizador/task.py` — `ColaTareasWorker` (singleton in-process, espera 21:00), `agregar_tareas_en_cola`. Stubs vacíos `etiquetado()`/`recoleccion()`/`procesar()` (placeholder Celery).
- `actualizador/actualizador_csv.py` — `principal_csv` (segunda pasada por `hay_csv_pendiente`), `buscar_modificar_registros_lotes`, `recompute_finales*`.
- `actualizador/sincronizador.py` — `buckup`/`reckup` (carpeta Drive hardcodeada).
- `bdd/classes.py` — `Patoba`: `listar`, `copiar_reemplazable`, `actualizar_plantilla`, `crear_buscar_copia_descarga`, `download_and_zip_files`, `borrar_por_id`. Auth: `SocialToken` del `user id=1` cuando `request=None` (`classes.py:36`).
- `bdd/funtions.py` — `get_emails` + `EMAIL_NAME_MAPPING` (remitentes hardcodeados).
- `bdd/models.py` — `Listado_Planillas`, `ListaProveedores` (`hay_csv_pendiente`), `Proveedor.identificador`, `Item` (`actualizado`, `*_base`, `factor_division`, `recompute_finales`). **`Condiciones` es código muerto** (solo la define el modelo y la FK `Archivo.condiciones`); las docs aún dicen que el parseo usa `Condiciones` — falso: la transformación vive en las fórmulas del GSheet plantilla.
- `facturacion/views.py:760` — trigger del cierre Z.
- `core_config/settings.py:31-33` + `.env.production:12-14` — `INBOX`/`PLANTILLAS`/`DESCARGAR` por env (prod usa Inbox y Descargar distintos a los defaults).
- `x_cartel/models.py` — `Carteles.revisar`/`CartelesCajon.revisar` (cola de re-impresión de etiquetas).
- Raíz del repo: `actualizador_main.py`, `actualizador_csv.py` (copias stale distintas a las de la app), `{Proveedor}.csv` (artefactos del pipeline en cwd), `recrear_descargables.py` (script one-off de reparación, IDs 1532/1538).

## Approaches

Esta exploración documenta el as-is; enfoques posibles para un futuro change de refactor:

1. **Unificar los 3 caminos de procesamiento en un solo servicio** — `principal()` paso 5, `procesar_planillas_listas` y la rama POST de `Actualizar` son tres variantes divergentes del mismo algoritmo (una ya tiene un orden distinto y mejor). Extraer una función `procesar_planilla(sp, patoba)` única.
   - Pros: elimina divergencia de orden BDD/Reemplazable; un solo lugar para quirks. Cons: tocar el pipeline más sensible del negocio. Effort: Medium.
2. **Mover dedup por hash + fallback xls al camino nightly** — hoy `detectar_planillas` tiene dedup y xlrd2/xls2xlsx pero el paso 3 de `principal()` no.
   - Pros: comportamiento consistente entre caminos. Cons: bajo. Effort: Low.
3. **Persistir la cola / sacarla del hilo in-process** — la cola muere con el proceso entre el cierre Z y las 21:00.
   - Pros: pipeline confiable. Cons: requiere scheduler persistente (Celery ya está en settings pero muerto). Effort: Medium-High.
4. **Eliminar código muerto del dominio** — `Condiciones`, `Archivo`, `HiloManager`, stubs `etiquetado/recoleccion/procesar`, copias de raíz, `armar_tabla` (input() interactivo inutilizable en server).
   - Pros: el mapa deja de mentir. Cons: riesgo bajo pero requiere cuidado con imports. Effort: Low.

## Recommendation

No tocar nada todavía — esto es la baseline de seguridad. Si el objetivo del usuario es cambiar cómo se etiquetan artículos nuevos, el punto de intervención real es: (a) el paso manual `/actualizar/` (asignación proveedor+hoja), o (b) la tab "Etiquetado" del GSheet (fórmulas, fuera del código). Antes de proponer, confirmar con el usuario cuál de los dos "etiquetados" quiere modificar — el código solo controla (a); (b) vive en Drive.

## Risks

- **Orden divergente**: `principal()` lee BDD antes de copiar `Reemplazable` (procesa datos del día anterior); `procesar_planillas_listas` ya copia primero. El sistema "funciona" porque `principal_csv` re-procesa después — frágil por diseño, no por azar.
- **Cola volátil**: `ColaTareasWorker` es in-process; si gunicorn reinicia entre el cierre Z y las 21:00, el pipeline no corre esa noche. Sin persistencia ni reintento.
- **Single point of failure OAuth**: todo corre con `SocialToken` del `user id=1` (`Patoba(None)`). Si ese token muere, se caen emails, detección, procesamiento, backup y reportes.
- **Destructivo por defecto**: el archivo original del Inbox se borra de Drive tras procesar; el GET de `/actualizar/` borra registros y archivos media de planillas no-recientes por proveedor; `detectar_planillas` borra archivos de Drive por hash duplicado.
- **Proveedor perdido en 2ª pasada**: `principal_csv` llama a `buscar_modificar_registros_lotes` sin `proveedor_obj` → Items nuevos creados ahí quedan `proveedor=None`.
- **Dedup asimétrico**: hash MD5 solo en `detectar_planillas`; `principal()` puede re-crear planillas ya procesadas si el archivo sigue en Inbox.
- **Secretos/IDs**: folder IDs de backup y pedidos hardcodeados en código (`sincronizador.py:33`, `classes.py:58`); `EMAIL_NAME_MAPPING` con emails reales en el repo; `.env.production` trackeado con IDs distintos a los defaults inseguros de settings.
- **`.xls` corruptos**: manejados con cadena xlrd2→xls2xlsx en 3 lugares (detectar_planillas, GET de `/actualizar/`, `copiar_reemplazable`) pero NO en el paso 3 de `principal()` (usa `pd.read_excel` a secas → un .xls viejo rompe la lectura de hojas nightly).
- **CSV en cwd**: `{Plantilla}.csv` se escribe en BASE_DIR; en Docker/prod contamina el working dir (los 8 CSV de la raíz son residuo de esto).
- **`get_emails` mira todo el INBOX de Gmail** (no filtra por remitente whitelist) — cualquier adjunto .xls de cualquier correo de las últimas 24h termina en el Inbox de Drive con nombre derivado del email.

## Ready for Proposal

**No — exploración standalone de baseline.** El orquestador debería decirle al usuario: el flujo está mapeado; "etiquetado" tiene dos sentidos (UI `/actualizar/` vs tab "Etiquetado" del GSheet); confirmar cuál quiere cambiar antes de lanzar `sdd-propose`. Si el objetivo es automatizar la asignación proveedor↔planilla ("proveedores en automático" de verdad), el change natural sería: reglas nombre-de-archivo→`ListaProveedores` en `detectar_planillas`, dejando la UI como override.
