# Exploration: `bdd` — capa de modelos y datos (baseline para refactor)

**Tipo:** exploración standalone — slice "modelos + datos" del deep-dive 4-way sobre la god-app `bdd`.
**Fecha:** 2026-10-08 · **Rama:** `produccion` (v3.10.x)
**Fuentes:** `bdd/models.py` (656 líneas, 28 modelos concretos + 2 abstractos), `bdd/migrations/0001-0006`, `bdd/urls.py`, `bdd/views/{base,main,ajax,forms,utils}.py`, `bdd/admin.py`, `bdd/forms.py`, `bdd/funtions.py`, consumidores cross-app (`facturacion`, `pedido`, `x_cartel`, `x_articulos`, `actualizador`, `administracion_financiera`, `utils/`), `bdd/DOCUMENTATION.md`, `docs/informe_arquitectura.md`, exploraciones previas (arquitectura, subtítulos, pedidos, carteles) y volcado **read-only** de `db.sqlite3` local (`mode=ro&immutable=1`, datos de prod).

---

## Current State

### 1. Inventario completo de modelos (`bdd/models.py`)

28 modelos concretos + 2 abstractos (`GenericaLista`: abreviatura+nombre; `Generica`: nombre). La doc dice "22 modelos" — desactualizada.

| Modelo | Campos | Propósito | Filas en DB | Clasificación |
|---|---|---|---|---|
| `Item` | 39 (+id) | Inventario central | 106.503 | **Dominio — load-bearing** |
| `Proveedor` | 8 | Datos de contacto proveedor | 33 | Dominio — load-bearing |
| `ListaProveedores` | 3 | Abreviatura `XXX/AB` + flag `hay_csv_pendiente` | 35 | Dominio — load-bearing (pipeline) |
| `Sub_Carpeta` | 1 (`Generica`) | Taxonomía impresión (sección) | 40 | Dominio — load-bearing |
| `Sub_Titulo` | 1 (`Generica`) | Taxonomía impresión (subdivisión) | 55 | Dominio — load-bearing |
| `Lista_Pedidos` | 4 | Faltantes (puente ventas↔pedidos) | 4.375 (78 `pedido=True`) | Dominio — load-bearing |
| `Listado_Planillas` | 14 | Estado de planillas Drive del actualizador | 30 | Dominio — load-bearing |
| `Carrito` | 1 (FK user) | Carrito por usuario (1:1 por convención) | 6 | Dominio — load-bearing |
| `Articulo` | 5 | Ítem registrado dentro de un carrito | 9 | Dominio — load-bearing |
| `ArticuloSinRegistro` | 4 | Ítem fuera de inventario en carrito | 0 | Dominio — load-bearing (pero ver §5 landmine CASCADE) |
| `Sector`/`Cajonera`/`Cajon` | 1/2/2 | Ubicación física (jerarquía) | 8/18/39 | Dominio — uso marginal (137 items con cajón) |
| `Marca` | 1 | Marca del item | **0** | **Muerta** (FK `Item.marca` NULL en 106.503 filas) |
| `Cod_Barras` | 2 | Segundo código de barras por item | **0** | **Muerto** (duplica `Item.barras`) |
| `Condiciones` | 9 | Config de columnas CSV por proveedor | **0** | **Muerto** — el doc dice que el pipeline lo usa; **falso**: cero imports |
| `Archivo` | 5 | Upload de archivos a `inbox/` | **0** | **Muerto** (métodos rotos) |
| `Compras` | 6 | Remitos/compras a proveedor | **0** | **Muerto** |
| `Tipo_Cartel` | 1 (`Generica`) | Tipo de cartel | **0** | **Muerto** (FK `Item.tipo_cartel` NULL en todas) |
| `Registros` | 6 | Links a planillas Drive históricas | 36 | **Huérfano con datos** — sin código que lo lea (la URL `/registros` solo existe en el viejo `base.html`) |
| `Tipo_Registro` | 1 | Categoría de Registros | 6 | Huérfano (acompaña a Registros) |
| `NavBar` | 2 | Entrada del menú + generador de rutas | 6 | **UI-metadata — load-bearing** |
| `Armador` | 12 | Registro-maestro de la vista auto-generada | 4 | **UI-metadata — load-bearing** |
| `Muro` | 1 | Nombre del template "muro" | 5 | UI-metadata — load-bearing |
| `Contenedor` | 5 | Lista de hasta 3 plantillas por vista | 11 | UI-metadata — load-bearing |
| `Plantilla` | 1 | Nombre de template parcial | 14 | UI-metadata — load-bearing |
| `Modelo_Campos` | 1 | Columnas a mostrar en la tabla | 29 | UI-metadata — load-bearing |
| `Formulario_Campos` | 1 | Campo del formulario dinámico | 16 | UI-metadata — load-bearing |
| `Formulario_Campos_Contiene` | 1 | Campo con lookup `__icontains` | 1 | UI-metadata — load-bearing |
| `Formulario_Campos_Empieza_Con` | 1 | Campo con lookup `__istartswith` | 1 | UI-metadata — load-bearing |

**Tablas huérfanas en DB sin modelo** (restos de la era pre-squash — `0001_initial.py` fue regenerado con Django 5.2.1 el 2025-07-05 aunque el runtime pinnea 4.0.6): `bdd_buleta` (2 filas, una sola columna `hay`), `bdd_metodopago` (0), `bdd_ticket` (0), `bdd_tipo` (0) — corresponden a los modelos comentados en `models.py:22-30`.

### 2. `Item` — 39 campos categorizados

| Categoría | Campos | Uso real (106.503 filas) |
|---|---|---|
| Identidad | `codigo`, `barras`, `descripcion` | codigo: 0 NULL pero **6 códigos duplicados** (sin unique ni index); barras: 55.851 poblados; `barras` es `IntegerField` (pierde ceros a la izquierda) |
| Ubicación | `cajon` (→Cajon→Cajonera→Sector) | Solo 137 items (0,1%) — feature apenas adoptada |
| Taxonomía | `proveedor` (91.537), `sub_carpeta` (7.272), `sub_titulo` (1.033), `marca` (**0** — muerto), `tipo_cartel` (**0** — muerto) | La clasificación viva llega por la hoja `BDD` del pipeline |
| Inputs de pricing (escritos por CSV) | `precio_base`, `porcentaje` (85.541≠1), `porcentaje_efectivo` (97.502≠1), `pack_cantidad` (4.151≠1), `cantidad_rollo_caja` (2.325≠1), `precio_rollo_caja` (6.487=True), `venta_rollo_caja` (2.439=True) | Vivos — la pestaña `BDD` de cada planilla los escribe vía `update_or_create`/`bulk_update` |
| Inputs de pricing **muertos** | `oferta`, `porcentaje_oferta`, `porcentaje_oferta_efectivo`, `porcentaje_metro`, `descuento_rollo_caja`, `descuento_rollo_caja_efectivo` | **0 filas** con valor ≠ default en los 6 |
| Precios derivados | `final_base`, `final_efectivo_base`, `final_rollo_base`, `final_rollo_efectivo_base` → `final`, `final_efectivo`, `final_rollo`, `final_rollo_efectivo` | Convención `*_base` (migración 0003 con backfill F()): el pipeline escribe `*_base`, `recompute_finales()` deriva los `final*` aplicando `factor_division` (>1) + `round_price()`. Consistencia verificada: solo 4 filas con `final≠final_base` = las 4 con `factor_division` |
| Flags/UI | `trabajado` (2.871), `actualizado` (80.145), `tiene_cartel` (144), `p_c_efectivo`/`p_c_debito`/`p_c_credito` (**0** — muertos, solo omitidos por `x_articulos`) | |
| Stock | `stock` | Solo 281 ≠ 0 — el negocio casi no usa stock en DB |
| Auditoría | `fecha` (`auto_now_add`) | **54.905 filas NULL (52%)** — la mitad de los items entró por caminos que no setean fecha (import/squash) → campo no confiable |
| Divisor UI | `factor_division` | 4 items — feature nuevo (migración 0002), uso mínimo |

**Métodos:** `recompute_finales()` es el único vivo y correcto (llamado por `actualizador_csv` y `editar_item`; NO guarda, el caller hace `save(update_fields=...)`). `calcular_precio_final/efectivo_final/rollo_final/rollo_efectivo_final` son **código muerto roto**: referencian `self.constante` y `self.venta_metro`, campos inexistentes (`models.py:307-347`). `marcar_actualizado/desactualizado` setean el flag sin save (los usa el pipeline indirectamente; también existen en código muerto).

**Contrato implícito CSV→Item (riesgo de refactor):** el camino individual del pipeline hace `defaults = {k:v for k,v in row.items() if k != "codigo"}` y `update_or_create(defaults=defaults)` (`actualizador_csv.py:228-264`) — **toda columna de la hoja `BDD` que coincida con un campo de Item se escribe; un campo eliminado del modelo que siga como columna en la planilla provoca `FieldError` por fila** (cae a `errores_importacion.csv`). El camino por lotes (`:414-426`) escribe un subset fijo: `codigo, sub_carpeta, sub_titulo, descripcion, actualizado, proveedor, precio_base, final_base, final_efectivo_base`.

### 3. Jerarquía `Generica` (taxonomía)

`Generica` abstracta (`nombre` CharField 25) → `Sub_Carpeta`, `Sub_Titulo`, `Tipo_Cartel`. Las dos primeras son la clasificación de impresión (ver `explore-subtitulos-subcarpetas`); `Tipo_Cartel` está muerta (0 filas). `GenericaLista` abstracta (`abreviatura`+`nombre`) → solo `ListaProveedores` (los otros tres herederos — `MetodoPago`, `Ticket`, `Tipo` — están comentados en `models.py:22-30` pero sus tablas siguen en la DB).

### 4. Modelos de dominio restantes

- **`ListaProveedores`**: la `abreviatura` (`/3D`, `/B`…) es el mecanismo de ruteo código→proveedor en `crear_modificar_lista_pedidos` y `en_lista` (templatetag). `hay_csv_pendiente` es el flag que consume `principal_csv` (`actualizador_csv.py:805`) + acciones del admin. Load-bearing aunque el nombre confunde (es "lista de proveedores que tienen planilla", no la lista canónica — `Proveedor` tiene 33 filas vs 35 acá).
- **`Lista_Pedidos`**: `(proveedor, item, cantidad, pedido)` — corazón compartido ventas↔pedidos. Escritores: `agregar_articulo_a_carrito`, `crear_modificar_lista_pedidos`, `eliminar_articulo_pedido`, `cambiar_cantidad_pedido` (bdd), `facturacion/views.py:300-395` (descuenta al vender), todo `pedido/views/*`. Sin `unique_together(item, proveedor)` — hoy 0 duplicados por suerte de `get_or_create`. `cantidad` Float (cantidades fraccionarias reales).
- **`Listado_Planillas`**: máquina de estados del pipeline Drive (`listo`, `descargar`, `descargado`, `fecha_descarga`, `usuario_descarga`, `error_columnas`, `file_hash`, `identificador` unique). En prod: 30 filas, 29 `descargar=True`, 0 `descargado` — el flag de descarga por usuario nunca se marcó o se resetea.
- **`Carrito`/`Articulo`/`ArticuloSinRegistro`**: carrito por usuario (6 carritos = 6 usuarios; sin `unique` en `usuario` — 1:1 solo por convención de `get_or_create`). `Articulo.precio`/`precio_efectivo` son `DecimalField(10,2)` — snapshot de precio al agregar (inconsistente con `Item.final` Float). `ArticuloSinRegistro` 0 filas.
- **`Condiciones`** (muerto): el diseño original era "config declarativa del CSV por proveedor" (letra de columna, fila inicial, porcentajes IVA, dólar) — el pipeline actual no lo consulta: las columnas llegan ya normalizadas desde la hoja `BDD` de Google Sheets. Métodos rotos (`self.descripcion` inexistente, `:86-111`).
- **`Archivo`** (muerto): upload a `media/inbox`, `descargar()`/`basename()` referencian `self.descarga` inexistente y `__str__` hace `self.proveedor.id.nombre` (int no tiene `.nombre`) — triple bug.
- **`Compras`** (muerto): modelo de cuentas con proveedor nunca usado — su función real vive en `administracion_financiera`.
- **`Registros`/`Tipo_Registro`** (huérfanos con datos): 36 links a planillas históricas de Drive (Ventas por mes, Compras, Etiquetado). No hay vista que los sirva (el `Contenedor` "registros/" existe pero ningún `Armador` lo referencia). Campo con typo horneado: `automatioco`.

### 5. Modelos de UI-metadata (el experimento de vistas auto-generadas)

Cadena: `NavBar(url_inicial, text_display)` → `Armador` (1:1 por convención con NavBar, apunta a `Muro` + `Contenedor`→3×`Plantilla`, `modelo` nombre-de-modelo string, `vista` nombre-de-clase string, `formulario_campos*` M2M) → `bdd/urls.py:34-67` consulta la DB **en import-time** y genera `path()` por cada NavBar (con `except: pass` que traga errores); `MiVista.get_context_data()` (`base.py:60-206`) resuelve `Armador` por `request.path`, `apps.get_model("bdd"|"x_cartel", modelo)`, arma `MyForm` dinámico y la lista de templates. Todo renderiza `generic_template.html`.

**Estado real de la maquinaria (DB local):**
- 6 `NavBar`, solo **4 con `Armador`** → `listar_carteles/` y `facturacion/` no generan ruta dinámica (caen en el `except: pass` silencioso; existen como rutas estáticas/de otra app).
- `Armador` filas: `/buscador/`→`Item`+vista `Inicio`; `/actualizar/`→`Item`+`Actualizar`; `/descargar_planillas/`→`Listado_planillas`+`Inicio`; `/lista_pedidos/`→`Lista_Pedidos`+`ListadoPedidos` **pero su `nav_bar.url_inicial` es `pedidos/home/`** — divergencia url↔url_inicial: la ruta generada choca con `pedido.urls` montado antes (`core_config/urls.py:31` vs `:34`) y además `MiVista` no encontraría el Armador por path → **armador 11 es config muerta**; la pantalla real de pedidos la sirve `pedido.HomeView`.
- Config con **typos silenciosos**: `modelo_campos` contiene `escargar` (sic), `item__descipcion` (sic), `automatico` (el campo real es `automatioco`) → el filtro de `titulos` en `base.py:115-135` los descarta sin error; el formulario_campos `item__cajon`/`item.cajon`/`item_id__descripcion`/`cajon__item` (ids 10-16) son intentos fallidos de sintaxis FK que quedaron como basura.
- `Contenedor` tiene 11 filas pero solo 4 referenciadas por Armador (ids 2,6,8,9); `Plantilla` 14 filas con 5 no referenciadas; `Muro` 5 filas, 3 usados.
- El experimento **sirve efectivamente 3 pantallas** (`/buscador/`, `/actualizar/`, `/descargar_planillas/`); todo lo demás fue "des-generalizado" a rutas estáticas — el modelo quedó a medio desarmar, mezclado con dominio.
- Existe además el sistema de andamio ORIGINAL en `core_andamios` (`Nav_Bar`/`Url`/`Contenedor`/`Script`/`Pie`/`Contexto`) — paralelo, semimuerto; solo `core_index` lo usa y su context processor corre en todas las requests.

### 6. Problemas de capa de modelos (catálogo para refactor)

1. **Dinero en `FloatField`**: ~30 floats en `Item`, `Lista_Pedidos.cantidad`, `Compras.*`, `Articulo.cantidad`, `ArticuloSinRegistro.cantidad` — mientras `Articulo.precio`, `ArticuloSinRegistro.precio` y `facturacion` usan `DecimalField` → mezcla Float/Decimal en el mismo flujo de venta (se convierte al serializar; `ArticuloVendido.get_item` hace `round()` sobre floats).
2. **CASCADE destructivos**: `ArticuloVendido.sin_registrar`→`ArticuloSinRegistro` y `.item`→`Item` son CASCADE — el cleanup post-venta `articulos_sin_registro.delete()` (`facturacion/views.py:140-142`) **borra en cascada los ArticuloVendido de items sin registro**. Dato que lo confirma: 40.667 `ArticuloVendido` y **0 con `sin_registrar_id`** — la historia de ventas de items sin registro se pierde silenciosamente. Borrar un `Item`/`Proveedor`/`Cajon`/`Marca` también borra pedidos, ventas y carteles en cascada.
3. **Sin constraints**: `Item.codigo` ni unique ni index (6 dupes reales; búsquedas full-scan en 106k filas), `Carrito.usuario` no unique, `Lista_Pedidos(item,proveedor)` no unique, `Registros.automatioco` typo persistido.
4. **`auto_now_add` poco confiable**: `Item.fecha` NULL en 52% de filas; `pedido.ArticuloPedido.fecha` tiene `auto_created=True` + `default="2021-01-01"` → todas las filas con fecha constante (ya documentado).
5. **Campos escritos por pipeline externo**: la hoja `BDD` de Google Sheets es schema implícito — renombrar/borrar un campo de `Item` rompe filas en import (ver §2 contrato). `factor_division` está protegido explícitamente (`defaults.pop`, `:260`).
6. **Basura semilla en datos** (verificado en `explore-subtitulos-subcarpetas`): `Sub_Carpeta` `''` (id 2, **3.339 items apuntan ahí**), `'Subcarpeta'`; `Sub_Titulo` `'Subtitulo'`, `''`; duplicados por case (`Arandelas Tuercas mariposa`); nombres >25 chars que SQLite no enforcea pero **PostgreSQL rechazaría** en un insert futuro.
7. **Basura semilla en metadata**: `Plantilla` 'buscador.html' (nombre con extensión que rompe el patrón `f"{valor}.html"` → genera `buscador.html.html`), contenedores sin armador, `modelo_campos` con typos.
8. **`bdd/forms.py` muerto y roto**: `from .models import Planilla` — modelo inexistente; importarlo crashea. Nadie lo importa (las forms vivas están en `bdd/views/forms.py`).
9. **`bdd/funtions.py`**: `armar_tabla` (legacy Google API) sin callers excepto `get_emails` (usado por `views_old`, `procesar_emails`, scripts de raíz).
10. **`ManyToManyField(null=True)`** en Armador — kwarg no-op que delata la época del experimento.
11. **`Armador`/`NavBar` consultados en import-time** en `urls.py` — una migración pendiente rompe el arranque; tests que importen urls contra DB vacía generan 0 rutas dinámicas.
12. **Duplicación de conceptos cross-app**: `articulos` app define sus propios `Marca/Proveedor/Articulo/CodigoBarras/Cartel/ArticuloProveedor` (app abandonada), `x_articulos` define otro `Articulo` — 3 modelos "Articulo" distintos en el proyecto.
13. `Item.barras` IntegerField para EAN — pierde ceros iniciales; debería ser CharField.
14. Tablas huérfanas (`bdd_buleta`, `bdd_metodopago`, `bdd_ticket`, `bdd_tipo`) — no hay migración que las borre; un `sqlmigrate`/fresh-install no las recrea pero la DB real las arrastra.

## Affected Areas

- `bdd/models.py` — los 28 modelos (este archivo es el artefacto a refactorizar)
- `bdd/migrations/0001-0006` — 0001 es squash regenerado (Django 5.2.1) con el esquema completo; 0002-0003 añaden `factor_division` + `*_base` con backfill; 0004-0006 extienden `Listado_Planillas`
- `bdd/urls.py:26-67` — consumo import-time de `NavBar`/`Armador` con `except: pass`
- `bdd/views/base.py:60-206,391-528` — `MiVista`: resolución de Armador→modelo→MyForm→titulos→templates; POST genérico `form.save(model_name)` que **crea instancias de cualquier modelo por nombre**
- `bdd/views/forms.py` — `MyForm` dinámico (lookup en apps `bdd`/`x_cartel`); `BusquedaForm`/`BusquedaView` (sin ruta — muerto)
- `bdd/forms.py` — muerto, roto (`Planilla` inexistente)
- `bdd/views/ajax.py` — escritores de `Item` (editar_item: stock/barras/tiene_cartel/cajon/proveedor/sub_titulo/factor_division), `Lista_Pedidos`, `Carrito`/`Articulo`/`ArticuloSinRegistro`
- `bdd/admin.py:85-94` — auto-registro de TODOS los modelos (expone los muertos en `/admin/`)
- `bdd/management/commands/{apply_rounding,procesar_emails}.py` — usan `Item`/`get_emails`
- `actualizador/actualizador_csv.py:166-530` — escritor principal de `Item`/`Sub_*`/`ListaProveedores`
- `actualizador/{views,actualizador_main}.py` + `management/commands/` — `Listado_Planillas`
- `facturacion/{models,views,funtions,classes}.py` — `Item`, `Carrito`, `Articulo`, `ArticuloSinRegistro`, `NavBar`, `Lista_Pedidos`
- `pedido/{models,views/*}.py` — `Item`, `Proveedor`, `Lista_Pedidos`
- `x_cartel/models.py` — FKs a `Item`/`Proveedor`; `x_articulos/` — `Item_Form` + `Articulo` propio
- `administracion_financiera/` — solo `Proveedor` (la más aislada)
- `utils/queryset_to_xlsx.py` + scripts de raíz (`script.py`, `fix_proveedores.py`, `recrear_descargables.py`, `actualizador_*.py` legacy) — lectores/escritores sueltos de `Item`, `Lista_Pedidos`, `Proveedor`, `Listado_Planillas`
- `db.sqlite3` (40MB, datos de prod en el working dir) — fuente de todas las métricas de este documento

## Approaches

1. **Limpieza de muertos en dos pasos (código → tablas)** — primero borrar modelos/archivos sin uso (ver lista de extracción abajo) con migraciones `DeleteModel`/`DROP TABLE`, luego datos semilla.
   - Pros: reduce la superficie antes de tocar lo vivo; cada paso es un PR chico. Cons: no mejora lo que queda. Effort: Low.

2. **Extraer la UI-metadata a app propia o eliminarla** — mover `NavBar/Armador/Muro/Plantilla/Contenedor/*_Campos` a `core_andamios` (o una `core_scaffold` nueva) con re-exports temporales, o reemplazar las 3 rutas dinámicas por `path()` estáticos + config en código y matar la maquinaria.
   - Pros: corta el cordón dominio↔andamio, elimina queries en import-time, saca ~10 tablas de `bdd`. Cons: la config vive en la DB de prod — requiere volcado/migración de datos y tocar `MiVista`+`urls.py`. Effort: Medium-High.

3. **Hardening del modelo `Item`+carrito** — `FloatField`→`DecimalField` con `RunPython`, constraints (unique `codigo`+`proveedor`, unique `Carrito.usuario`), `SET_NULL/PROTECT` en `ArticuloVendido`, índice en `codigo`, `barras`→CharField.
   - Pros: cierra pérdida de datos real (ventas sin registro) y prepara para Postgres. Cons: migración de datos en tabla de 106k filas + verificar el contrato CSV (la hoja `BDD` puede traer columnas-fantasma que hoy mapean a campos). Effort: Medium.

## Recommendation

Orden sugerido: **(1) quick wins de muertos** (riesgo casi nulo, datos lo confirman), **(2) constraints/integridad** (CASCADE de `ArticuloVendido` es pérdida de datos ACTIVA — priorizar), **(3) extracción UI-metadata** una vez decidido el destino de la maquinaria (reemplazar vs extraer), **(4) Float→Decimal** como change propio con migración ensayada. Antes de borrar CUALQUIER campo de `Item`, auditar los headers reales de las hojas `BDD` en Drive (están fuera del repo): el pipeline hace spread de todas las columnas.

## Risks

- **Pérdida de datos activa**: cada venta con `ArticuloSinRegistro` borra su `ArticuloVendido` por CASCADE en el cleanup del carrito (0/40.667 con `sin_registrar` lo prueba).
- **Config en DB = schema oculto**: nombres de modelo/vista/template/campos viven en filas `Armador`; un rename de campo de `Item` puede degradar una pantalla sin error (filtro silencioso de `titulos`).
- **Contrato CSV implícito**: eliminar campos "muertos" de `Item` sin limpiar la hoja `BDD` genera `FieldError` por fila en el pipeline nocturno.
- **db.sqlite3 ≠ prod necesariamente**: las métricas son del dump local (prod-real); verificar counts contra la DB de Docker/Postgres si difiere.
- **Borrar tablas huérfanas** (`bdd_buleta` etc.): seguras a nivel ORM pero conviene `DROP TABLE` manual/migración cruda verificando que ninguna app las referencia por SQL crudo (no se encontró ninguna).
- `bdd/urls.py` consulta DB en import → cualquier refactor de modelos metadata puede dejar el sitio sin rutas dinámicas en arranque frío (migraciones pendientes → `armador_paths=[]`).

## Refactor extraction candidates (easiest-first)

1. **`bdd/forms.py`** — borrar archivo (import roto a `Planilla`, sin callers). Sin migración.
2. **Métodos muertos rotos** — `Item.calcular_*` (4), `Condiciones.detectar_columna/ordenar_columnas`, `Archivo.descargar/basename`, `Condiciones`/`Archivo`/`Compras`/`Cod_Barras`/`Tipo_Cartel`/`Marca` **modelos completos** (0 filas, 0 imports). Una migración `DeleteModel` por lote. Ojo: `Marca`/`Tipo_Cartel` requieren quitar antes el FK en `Item`.
3. **Tablas huérfanas** `bdd_buleta`, `bdd_metodopago`, `bdd_ticket`, `bdd_tipo` + bloques comentados en `models.py` — `DROP TABLE` vía `RunSQL` (verificar FK: ninguna encontrada).
4. **`Registros`/`Tipo_Registro`** — tienen datos (36 links Drive): decidir exportar a doc/fixture y luego `DeleteModel`. Código muerto confirmado.
5. **Campos muertos de `Item`** — `marca`, `tipo_cartel`, `p_c_efectivo/debito/credito`, `oferta`, `porcentaje_oferta*`, `porcentaje_metro`, `descuento_rollo_caja*` (0 filas no-default en todos) — requiere primero allowlist de columnas en `actualizador_csv` (contrato CSV).
6. **Fix CASCADE `ArticuloVendido`** — `sin_registrar`/`item` → `PROTECT` o snapshot denormalizado (descripcion+precio). Pérdida activa de datos; prioridad alta aunque no es "extract".
7. **`Carrito`/`Articulo`/`ArticuloSinRegistro` → `facturacion`** — extraer a la app que los consume (bdd solo los toca en ajax de carrito; mover también esos endpoints). Blast radius medio.
8. **`Lista_Pedidos` → `pedido`** — el modelo vive conceptualmente en pedidos (bdd solo lo alimenta). Cross-imports con facturacion complican; hacerlo junto con (7) o después.
9. **Cluster UI-metadata** (`NavBar`,`Armador`,`Muro`,`Plantilla`,`Contenedor`,`Modelo_Campos`,`Formulario_Campos*`) → app `core_scaffold` o reemplazo por config estática. El más grande: define el destino antes de mover.
10. **`Sector`/`Cajonera`/`Cajon`** — quedan en `bdd` si `bdd` sigue siendo inventario (137 items los usan, `ListarCarteles` y el modal de edición los consumen); no extraer.

## Ready for Proposal

**Sí — como baseline, no como change único.** Hay material para varios changes SDD chicos; el orquestador debería confirmar con el usuario: (a) ¿empezar por la limpieza de muertos (candidates 1-4) o por el fix de CASCADE de `ArticuloVendido` (pérdida activa)?; (b) ¿la maquinaria Armador se extrae a app propia o se reemplaza por rutas/config estáticas?; (c) ¿el contrato CSV se congela con allowlist antes de tocar campos de `Item`? (recomendado: sí).
