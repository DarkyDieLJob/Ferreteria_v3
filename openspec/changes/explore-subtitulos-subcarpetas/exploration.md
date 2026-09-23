# Exploration: Flujo ACTUAL de sub_títulos y sub_carpetas (as-is)

**Tipo:** exploración standalone (sin change asociado) — documentación as-is pedida antes de modificar el flujo.
**Fecha:** 2026-10-02 · **Rama:** `produccion` (v3.10.x)
**Fuentes:** verificación directa del código, `bdd/DOCUMENTATION.md`, `auxiliares_apps/DOCUMENTATION.md`, `openspec/changes/explore-arquitectura-monolito/exploration.md`, CHANGELOG v3.10.0 y volcado **read-only** de `db.sqlite3` local (`mode=ro&immutable=1`).

---

## Mapeo de vocabulario (desambiguación)

| Concepto pedido | Implementación real | Dónde |
|---|---|---|
| `sub_títulos` | Modelo `Sub_Titulo` + FK `Item.sub_titulo` | `bdd` |
| `sub_carpetas` | Modelo `Sub_Carpeta` + FK `Item.sub_carpeta` | `bdd` |

**Falsos positivos con el mismo nombre (NO son estos conceptos):**
- `pedido/views/pdf_devoluciones.py:156-159,197-200` — variable local `subtitulo` (texto del PDF de devoluciones).
- `reportes/views_batch.py:81-113`, `reportes/conf.py:31-32` — "subcarpetas" = carpetas de Drive por año para reportes.
- `pedido/README.md` — "subcarpetas" = subdirectorios de templates.
- Scaffold dinámico (`bdd.Armador`/`NavBar`/`Contenedor` y `core_andamios.Nav_Bar`/`Url`/`Contenedor`): **no tienen sub-carpetas**; solo participan indirectamente porque `sub_titulo` está registrado como campo de formulario del Armador de `/buscador/` (ver abajo).

## Current State

### 1. Modelo de datos (`bdd/models.py`)

- `Generica` (abstracta, líneas 41-51): `nombre = CharField(25)` + `__str__` → nombre.
- `Sub_Carpeta(Generica)` — `bdd/models.py:114-115`. Sin campos extra.
- `Sub_Titulo(Generica)` — `bdd/models.py:118-119`. Idem.
- `Item.sub_carpeta` — `bdd/models.py:253-256`: FK → `Sub_Carpeta`, `null=True, blank=True, on_delete=SET_NULL`. Comentario en código: `# Hoja de destino`.
- `Item.sub_titulo` — `bdd/models.py:258-261`: FK → `Sub_Titulo`, `null=True, blank=True, on_delete=SET_NULL`. Comentario: `# Subtitulo`.
- Esquema creado en `bdd/migrations/0001_initial.py:108-127` (tablas) y `:349-358` (FKs). Ninguna migración posterior los toca (0002-0006 no los mencionan).
- Admin: ambos se auto-registran vía `inspect.getmembers` en `bdd/admin.py:88-94` → CRUD completo en `/admin/` sin configuración.

**Semántica real (deducida de código + datos):** son las dos dimensiones de clasificación de items para la **impresión de carteles/listas de precios**: `sub_carpeta` = la "hoja de destino" o sección del listado impreso (valores reales: `Salon`, `Pinturas`, `Mangueras`, `Tornillos Tirafondos`, `Griferia`, `Bombas`...); `sub_titulo` = subdivisión fina dentro de la sección (valores reales: tamaños `1L`, `4L`, `20L`, `1Kg`, `32Kg`, y subcategorías `Espatulas`, `Mechas Ac Rap`, `Lija al agua`...).

**Datos reales en `db.sqlite3` local:** 40 `Sub_Carpeta`, 55 `Sub_Titulo`. De 106.503 items: 7.272 tienen `sub_carpeta` y 1.033 tienen `sub_titulo`.

### 2. Origen de los datos (cómo se crean/editan los valores)

Los valores NO se cargan en la UI de Django: **se escriben en Google Sheets** y el pipeline del actualizador los materializa en la DB:

1. En la planilla-plantilla de cada proveedor (Google Sheets en carpeta `PLANTILLAS` de Drive) existe una pestaña **`BDD`** cuyas columnas incluyen literalmente `sub_carpeta` y `sub_titulo` (verificado en los CSVs volcados en raíz: `Cedica.csv`, `FerriPlast.csv`, etc. — headers: `codigo,descripcion,...,final_rollo_efectivo,sub_carpeta,sub_titulo`).
2. `principal_csv()` (`actualizador/actualizador_csv.py:799-913`) descarga el rango `BDD` de cada plantilla con `hay_csv_pendiente=True` → `{Proveedor}.csv`.
3. `buscar_modificar_registros_lotes()` (`actualizador_csv.py:711`) → `crear_o_actualizar_registros_en_lotes()` (`:308`):
   - `row.pop("sub_carpeta")` → `Sub_Carpeta.objects.get_or_create(nombre=...)` con cache en memoria (`subcarpetas_cache`, `:330-331,357-371`).
   - `row.pop("sub_titulo")` → `Sub_Titulo.objects.get_or_create(nombre=...)` (`subtitulos_cache`, `:374-386`).
   - Asigna ambos FK en `item_data` (`:416-417`) y persiste con `bulk_create`/`bulk_update`.
4. Camino alternativo individual: `crear_o_actualizar_registro()` (`actualizador_csv.py:166-305` y duplicado en `actualizador_main.py:164-253`) — mismo `get_or_create` + `Item.update_or_create`.
5. **Scripts legacy en raíz** `actualizador_csv.py` y `actualizador_main.py` (no los de la app): versiones viejas del mismo pipeline, mismo patrón `get_or_create` pero con `except: pass` desnudo — si corren a mano también crean/actualizan estas tablas.
6. **Django admin**: alta/baja/edición manual posible en `/admin/` (auto-registrado).
7. **UI de edición de item**: el modal del buscador solo permite *reasignar* un `Sub_Titulo` existente (no crear nuevos, no toca `sub_carpeta`).

### 3. Dónde aparecen en la UI / vistas / AJAX

| Superficie | Archivo | Qué hace |
|---|---|---|
| **Buscador `/buscador/`** | config Armador en DB + `bdd/views/base.py` + `bdd/views/forms.py` + `static/templates/plantilla_formulario.html` | `sub_titulo` es un `Formulario_Campos` del Armador `/buscador/` (verificado en DB: M2M `formulario_campos` = `codigo, barras, descripcion, sub_titulo`). `MyForm` lo renderiza como `ModelChoiceField` (`#id_sub_titulo`) y `plantilla_formulario.html:91-112` le aplica Select2. En `MiVista.get()` (`base.py:440-462`) filtra por **coincidencia exacta de FK** (no está en `campos_contiene` ni `campos_empieza`). Feature documentada en CHANGELOG v3.10.0 ("buscador: campo sub_titulo con Select2"). |
| **Impresión `/imprimir/` + `/imprimir/tabla/`** | `bdd/views_old.py:610-701` (**la vista cableada real** — `bdd/urls.py:5,107-109` importa `Imprimir` de `views_old`) | GET `/imprimir/` muestra formulario con exactamente `["sub_carpeta","sub_titulo"]` (ambos opcionales; Select2 aplica también acá). POST filtra `Item.objects.filter(**form_data)` y renderiza `/imprimir/tabla/` con `muro_imprimir.html` → `imprimir_carteles_x6.html` (carteles 6 por hoja, columnas descripcion/final/final_efectivo/final_rollo/final_rollo_efectivo/actualizado). `generic_template.html:92,135` detecta la ruta y omite navbar/carrito para impresión limpia. |
| **`views/main.py` `Imprimir`** | `bdd/views/main.py:165-324` | Refactor de la vista anterior **pero NO cableada** (urls.py importa de `views_old`) → código muerto que documenta el mismo flujo. |
| **Modal "Editar" del buscador** | `bdd/views/ajax.py:349-479` (`editar_item`) + `static/templates/tabla_buscador.html` | GET devuelve `subtitulos` (lista completa `Sub_Titulo` id+nombre) y `modal_sub_titulo_id`. POST acepta `sub_titulo_id`: asigna, limpia (""/null→None) o 400 si no existe. Template: select `#sub_titulo` (`:73-76`), poblado en `:134-140`, enviado en payload `:273,283`. **No existe edición de `sub_carpeta` por AJAX.** |
| **x_articulos (experimental)** | `x_articulos/forms.py:16-31` (`Item_Form` incluye ambos campos), `x_articulos/views.py:60,65` (los omite de la tabla) | CRUD experimental con filtro `codigo__contains="metdh"` hardcodeado; permite editar ambos FK vía POST del ModelForm. |
| **Admin** | `bdd/admin.py` | CRUD directo de `Sub_Carpeta`/`Sub_Titulo`/`Item` (incluye ambos FK en `Item.fields`). |

**Relación con la nav:** `/imprimir/` **no tiene entrada `NavBar`** en la DB (los NavBar reales son: buscador/, actualizar/, descargar_planillas/, pedidos/home/, listar_carteles/, facturacion/) — se accede por URL directa. `sub_titulo` sí toca el Armador como dato (`Formulario_Campos`), no como estructura.

### 4. Quirks / comportamiento relevante

- **El pipeline pisa las ediciones manuales:** en ambos caminos del actualizador, si la celda `sub_titulo`/`sub_carpeta` de la planilla viene vacía → `None` → `update_or_create`/`bulk_update` escribe NULL en el item (en lotes se conservan explícitamente los FK aunque sean None: `actualizador_csv.py:428-432`). Un `sub_titulo` asignado a mano por el modal se **borra** en la próxima actualización del proveedor si la planilla no lo repite.
- **`CharField(25)` no se enforcea en SQLite**: hay nombres de 26+ chars en DB (`Arandelas Tuercas Mariposa`).
- **Duplicados por case-sensitivity**: `Arandelas Tuercas Mariposa` (id 9) vs `Arandelas Tuercas mariposa` (id 38) — `get_or_create(nombre=...)` es case-sensitive.
- **Basura semilla**: existen `Sub_Carpeta` id=2 con `nombre=''` (¡3.339 items apuntan ahí!), id=8 `'Subcarpeta'`, y `Sub_Titulo` id=10 `'Subtitulo'`, id=54 `''` — filas creadas al ingerir headers/placeholders de las planillas (el código nuevo skipea vacíos con `if nombre:`, el legacy no).
- `on_delete=SET_NULL`: borrar una Sub_Carpeta/Sub_Titulo des-asigna items, no los borra.
- `Item.codigo` no es único → el mapeo "primera coincidencia" en lotes puede asignar estos FK al item "equivocado" si hay códigos duplicados.
- Asimetría UI: `sub_titulo` es filtro en buscador + editable en modal; `sub_carpeta` solo es filtro en `/imprimir/` — no hay forma en la UI de reasignarlo item por item.
- `nombre` es la única columna: no hay orden, padre, ni pertenencia de `Sub_Titulo` a `Sub_Carpeta` — la relación "subtítulo dentro de subcarpeta" es implícita por uso combinado en items, no modelada.

## Affected Areas

- `bdd/models.py:41-51,114-119,253-261` — `Generica`, `Sub_Carpeta`, `Sub_Titulo`, FKs en `Item`
- `bdd/migrations/0001_initial.py:108-127,349-358` — esquema
- `bdd/admin.py:88-94` — registro automático en admin
- `bdd/urls.py:5-8,107-109` — `/imprimir/` cableado a `views_old.Imprimir`
- `bdd/views_old.py:610-701` — vista ACTIVA de impresión por sub_carpeta/sub_titulo
- `bdd/views/main.py:165-324` — `Imprimir` refactorizado pero muerto
- `bdd/views/ajax.py:349-479` — `editar_item` (GET lista subtitulos / POST asigna `sub_titulo_id`)
- `bdd/views/base.py:96-107,440-462` + `bdd/views/forms.py:55-134` — Armador + `MyForm` que materializan `sub_titulo` como campo de búsqueda
- `static/templates/plantilla_formulario.html:91-112` — Select2 sobre `#id_sub_titulo`
- `static/templates/tabla_buscador.html:73-76,134-140,273,283` — modal edición con `sub_titulo`
- `static/templates/generic_template.html:92,135` + `muro_imprimir.html` + `imprimir_carteles_x6.html` + `imprimir_tabla.html` — render de impresión
- `actualizador/actualizador_csv.py:166-305,308-530` y `actualizador/actualizador_main.py:164-253,272-318` — `get_or_create` + asignación desde planilla `BDD`
- `actualizador_csv.py` + `actualizador_main.py` (raíz) — duplicados legacy que también escriben estas tablas
- `x_articulos/forms.py:16-31`, `x_articulos/views.py:60-66` — CRUD experimental
- Registros Armador en DB (`bdd_armador*`, `bdd_formulario_campos`): `/buscador/` incluye `sub_titulo` como campo de formulario — **la config vive en la DB, no en el repo**

## Approaches

Esta exploración documenta el as-is; si el change que viene busca modificar el flujo, las direcciones plausibles son:

1. **Mantener planilla como fuente de verdad + arreglar higiene** — normalizar `nombre` (trim/case), eliminar filas `''`/`Subcarpeta`/`Subtitulo`, decidir si el CSV puede NULL-ear asignaciones manuales.
   - Pros: no rompe el flujo que el usuario ya opera en Google Sheets. Cons: el "sistema" sigue viviendo fuera del repo (en Sheets). Effort: Low.
2. **Hacer la clasificación editable en Django** — extender `editar_item` para `sub_carpeta`, alta de subtítulos/carpetas desde UI, y/o modelar `Sub_Titulo.sub_carpeta` como FK padre.
   - Pros: la relación carpeta→subtítulo hoy implícita queda explícita; menos dependencia del formato de la hoja. Cons: requiere migración + cambiar el pipeline para no pisar ediciones (decidir precedencia). Effort: Medium.
3. **Rediseñar como taxonomía real** — modelo `Categoria/Seccion` jerárquico reemplazando ambas `Generica`, con migración de datos desde los nombres actuales.
   - Pros: modelo limpio y queryable (todos los items de una carpeta con sus subtítulos). Cons: blast-radius en `Item` (106k filas), actualizador, imprimir, buscador y admin; hay que migrar datos sucios. Effort: High.

## Recommendation

Para el change siguiente: decidir primero **quién es la fuente de verdad** (planilla `BDD` vs DB). Hoy ambas escriben y el pipeline gana silenciosamente — ese es el comportamiento a confirmar con el usuario antes de diseñar. Documentado el as-is, cualquiera de los 3 approaches es viable; el quick-win es (1) + limpiar datos semilla.

## Risks

- **Pérdida silenciosa de datos**: cualquier refactor debe resolver si el pipeline puede NULL-ear `sub_titulo`/`sub_carpeta` editados a mano (hoy sí puede).
- **Vista muerta vs viva**: `/imprimir/` ejecuta `views_old.Imprimir`, no `views/main.Imprimir` — tocar el flujo exige decidir qué implementación queda.
- **Config en DB**: `sub_titulo` como campo del buscador es un registro `Formulario_Campos` en producción; un cambio de nombre de campo rompe el formulario sin error visible.
- **Datos sucios reales** en prod-local: filas `''`, duplicados por case, nombres >25 chars (SQLite no enforcea; en Postgres sí fallaría el insert).
- La cadena de valor depende de la pestaña `BDD` de las planillas de Drive (fuera del repo): cambiar columnas allí cambia el comportamiento sin deploy.

## Ready for Proposal

**Sí** — hay change claro posible. El orquestador debería confirmar con el usuario: (a) ¿la planilla sigue siendo la fuente de verdad o se migra la edición a Django? (b) ¿`Sub_Titulo` debe colgar de `Sub_Carpeta`? (c) ¿qué hacer con las filas semilla (`''`, `Subcarpeta`, `Subtitulo`) y la vista `Imprimir` duplicada?
