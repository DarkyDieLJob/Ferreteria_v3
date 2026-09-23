# Exploration: `bdd` — mapa de acoplamiento (baseline para refactor)

**Tipo:** exploración standalone — slice "dependency web" del deep-dive sobre la god-app `bdd`.
**Fecha:** 2026-09-23 · **Rama:** `produccion`
**Método:** análisis exhaustivo de imports (`from bdd|import bdd`), FKs cruzados (`to='bdd.*'` en migraciones y modelos), `apps.get_model`, acoplamiento por templates (`extends`/`load custom_filters`), acoplamiento por metadata en DB (Armador/NavBar) y acoplamiento por settings. Todo verificado contra código real.
**Contexto previo:** `openspec/changes/explore-arquitectura-monolito/exploration.md`, `bdd/DOCUMENTATION.md`, `openspec/config.yaml`.

---

## Current State

### Inventario de `bdd` (lo que se expone)

`bdd/models.py` (656 líneas) define **32 clases** (docs dicen 22 — hay ~5 modelos muertos no documentados: `MetodoPago`, `Ticket`, `Tipo`, `Estructura`, más las abstractas `GenericaLista`/`Generica`). Agrupados por subdominio:

| Subdominio | Modelos |
|---|---|
| Inventario/precios | `Item` (40+ campos), `Marca`, `Cod_Barras`, `Sector`→`Cajonera`→`Cajon`, `Sub_Carpeta`, `Sub_Titulo`, `Tipo_Cartel` |
| Proveedores/planillas | `ListaProveedores`, `Proveedor`, `Condiciones`, `Archivo`, `Compras`, `Listado_Planillas` |
| Pedidos-support | `Lista_Pedidos` |
| Carrito | `Carrito`, `Articulo`, `ArticuloSinRegistro` |
| UI-metadata (andamio) | `NavBar`, `Muro`, `Estructura`, `Plantilla`, `Contenedor`, `Modelo_Campos`, `Formulario_Campos`, `Formulario_Campos_Contiene`, `Formulario_Campos_Empieza_Con`, `Armador` |
| Registros | `Tipo_Registro`, `Registros` |
| Integración Google | `classes.py:Patoba` (870 líneas), `funtions.py:get_emails`/`armar_tabla` (307 líneas) |
| Vistas/scaffold | `MiVista` (views/base.py), `MyForm` (views/forms.py), vistas main/ajax, `views_old.py` (1242 líneas, duplicado completo aún vivo) |
| Template tags | `templatetags/custom_filters.py`: `zip_lists`, `to_float` (**hardcodea `*1.15`**), `en_lista` (**hardcodea abreviaturas `/Nc,/Dx,/B,/Cb,/3D,/F`**) |

**`bdd` no tiene FKs hacia otras apps** (todos los FKs son internos o a `settings.AUTH_USER_MODEL`) — es autocontenida a nivel de schema; el acoplamiento es todo entrante + 3 aristas salientes por código (pedido, x_cartel, utils).

### OUTBOUND — matriz app → símbolos `bdd` consumidos

| App consumidora | Símbolos `bdd` usados | Archivos | Propósito / tipo de acople |
|---|---|---|---|
| **actualizador** | `Patoba`, `Listado_Planillas`, `Proveedor`, `Item`, `Sub_Carpeta`, `Sub_Titulo`, `ListaProveedores`, `get_emails` (funtions), `MiVista`, `MyForm` | `views.py:23-29`, `actualizador_main.py:71-73`, `actualizador_csv.py:57-60`, `sincronizador.py:5`, `management/commands/detectar_planillas.py:3-5` | **Máximo acople.** No tiene modelos propios (`models.py` vacío): `Listado_Planillas` ES su persistencia. Escribe `Item.final_base/final_efectivo_base/final_rollo_base/final_rollo_efectivo_base`, `trabajado`, `actualizado`; llama `recompute_finales()`. Usa internals de Patoba (`drive_service`, `gmail_service`, `sheet_service`, `obtener_id_por_nombre`, `copiar_reemplazable`, `actualizar_plantilla`, `borrar_por_id`, `listar`, `subir/descargar_sqlite3_a_drive`). `Actualizar(MiVista)` (views.py:59) **requiere fila `Armador` en DB para `/actualizar/`**. `task.py` carga todo lazy dentro de funciones. |
| **pedido** | `Item`, `Proveedor`, `Lista_Pedidos` | `models.py:4` (FKs), `views/base.py:3`, `views/home.py:3`, `views/editar.py:5`, `views/controlar.py:5`, `views/faltantes.py:1`, `views/devoluciones.py:5`, `views/externo.py:3`, `forms.py:5` | **FKs de schema:** `Vendido.item/proveedor`, `ArticuloPedido.item/proveedor`, `Pedido.proveedor` + M2M, `ArticuloDevolucion.item/proveedor` (7 aristas). Toda su lógica lee/escribe `Lista_Pedidos` (faltantes, controlar, devoluciones, externo). |
| **facturacion** | `Item`, `ArticuloSinRegistro` (FKs), `Carrito`, `Articulo`, `Lista_Pedidos`, `NavBar`, `Inicio` | `models.py:2`, `views.py:5-14`, `funtions.py:3`, `classes.py:6` | `ArticuloVendido.item` FK→Item y `sin_registrar` FK→ArticuloSinRegistro; `get_item()` lee `item.final/final_efectivo` (acople a campos de precio). `registrar_articulos_vendidos` consume el schema de carrito completo. `views.py` escribe `Lista_Pedidos` al modificar/eliminar artículos del carrito (write-through duplicado con `bdd/ajax.py`). 3 `TemplateView` inyectan `NavBar.objects.all()` → `barra_de_navegacion` (acople a UI-metadata). Import muerto: `views.py:5` `from bdd.views_old import Inicio` (pisado por línea 6). |
| **administracion_financiera** | `Proveedor` | `models.py:6` (4 FKs/O2O), `views.py:16,141-155` | `ProveedorFinanciero.proveedor` OneToOne + 3 FK PROTECT (Boleta línea 107, `CtaCteProveedor` línea 183, línea 221). Vistas: `Proveedor.objects.all().select_related("financiero")`. Acople solo a `Proveedor` — el más sano de los grandes. |
| **x_cartel** | `Item`, `Proveedor` | `models.py:2`, `views.py:154` | 6 aristas FK: `Cartelitos.item` (O2O)+`proveedor`, `Carteles.item/proveedor`, `CartelesCajon.item/proveedor`. `precios_articulos*` JSON lee `Item.final*` (views.py:154+). |
| **x_articulos** | `Item` | `views.py:5`, `forms.py:3` | CRUD experimental sobre `Item` (filtro `codigo__contains="metdh"` hardcodeado). Además `x_articulos/admin.py` es un **clon de `bdd/admin.py`** con nombres de modelos bdd como strings (`Armador`, `Modelo_Campos`...). |
| **reportes** | `Patoba` | `adapters_patoba.py:4` | Único consumidor limpio: `PatobaDriveAdapter` envuelve Patoba detrás de un port hexagonal. Migraciones 0002-0004 tuvieron FK a `bdd.item/proveedor` (WeeklySalesSnapshot) — **modelo borrado en 0005**, acople de schema ya eliminado. |
| **utils** (módulo raíz) | `Lista_Pedidos`, `Proveedor` | `queryset_to_xlsx.py:141` | `ejecutar()` exporta pedidos a xlsx; también importa `facturacion.models.ArticuloVendido`. |
| **scripts raíz** | `Item`, `Lista_Pedidos`, `Proveedor`, `ListaProveedores`, `Listado_Planillas`, `Patoba`, `get_emails` | `script.py:9,34,96`, `fix_proveedores.py:1`, `script_seteado_false_lista_faltantes.py:8`, `recrear_descargables.py:6-7`, **`actualizador_main.py` y `actualizador_csv.py` raíz (duplicados completos de la app)**, `cargar_datos_csv.py` (genérico `apps.get_model`) | Mantenimiento manual. Los duplicados raíz del pipeline del actualizador importan los mismos símbolos. |
| **scripts shell** | `Item` | `scripts/migrate_sqlite_to_pg.sh:64`, `scripts/deploy.sh:92` | Python embebido en deploy/migración toca `Item` directo. |
| **tests/** | — | — | **Cero referencias a `bdd`**: la suite no toca la god-app (los 45 tests cubren `utils.rounding` y la app abandonada `articulos`). |
| **boletas, cajas (código), carga_archivo, articulos, core_docs, core_index, core_elementos, x_widgets, core_testing** | — | — | Sin acople de código a `bdd`. `cajas` solo tiene templates muertos que llaman endpoints AJAX de bdd (7 refs en `caja_tabla_resultado.html`). `articulos` duplica conceptos (`Articulo`, `Marca` propios) sin importar bdd. |

### INBOUND — qué importa `bdd` de otras apps

| Arista | Ubicación | Naturaleza |
|---|---|---|
| `bdd → pedido` | `bdd/urls.py:29`: `from pedido.views.externo import agregar_al_pedido` | Monta una vista de pedido en URL raíz `/agregar_articulo_a_pedido/`. **Razón estructural:** el router dinámico hace `import_string(f"bdd.views.{armador.vista}")` — solo puede montar clases de `bdd.views`, así que vistas de otras apps se enchufan "a mano" en `bdd/urls.py`. |
| `bdd → x_cartel` | `bdd/views/main.py:14`, `bdd/views_old.py:39`: `from x_cartel.models import CartelesCajon, Carteles` | `ListarCarteles`/`Imprimir` **crean filas en tablas de x_cartel** (`CartelesCajon.objects.get_or_create`). Escritura cross-app. |
| `bdd → utils` | `bdd/models.py:362`: `from utils.rounding import round_price` (lazy, dentro de `recompute_finales`); `bdd/management/commands/apply_rounding.py:4` | Precio unificado vive en `utils/` — dependencia correcta pero crea ciclo a nivel paquete. |
| `bdd → settings` | `INTEGRATE_MERCADOPAGO`, `INTERNET`, `MP_TOKEN_FILE`, `TABLA_LINK_PEDIDOS` (getattr con defaults), `BASE_DIR`, `MEDIA_ROOT`, `AUTH_USER_MODEL` | Acople por contrato de settings implícito (todas con `getattr` salvo `views_old.py:288` que usa `settings.INTERNET` directo). |

### Ciclos concretos (verificados)

1. **bdd ↔ pedido** — `bdd/urls.py:29` → `pedido.views.externo` → `pedido.models` → `bdd.models` (línea 4). Ciclo a nivel app: `bdd.urls` no carga sin `pedido`; `pedido` no migra sin `bdd`. No rompe imports porque `bdd.models` no importa `pedido`, pero el acople es real y bidireccional. Extra: existen **dos funciones `agregar_al_pedido`** distintas (`pedido/views/externo.py` montada por bdd en raíz; `pedido/views/editar.py` montada en `/pedidos/`).
2. **bdd ↔ x_cartel** — `bdd.views.main:14` y `views_old.py:39` importan `x_cartel.models` (y crean `CartelesCajon`); `x_cartel/models.py:2` importa `bdd.models` (FKs). Además `actualizador` también escribe `x_cartel` (`actualizador_main.py:74`, `actualizador_csv.py:58` — marca carteles `revisar`) → triángulo bdd↔x_cartel←actualizador→bdd.
3. **bdd ↔ utils** — `bdd/models.py:362` (lazy) → `utils.rounding`; `utils/queryset_to_xlsx.py:141` → `bdd.models`. Ciclo de paquete, mitigado por lazy import en bdd.
4. **bdd ↔ actualizador: NO es ciclo de imports** (hipótesis del brief refutada) — `bdd` nunca importa `actualizador`. Es acople unidireccional masivo actualizador→bdd + cadena `facturacion → actualizador.task → (lazy) actualizador_main → bdd`. `actualizador_csv.py:936` importa `boletas` lazy (otra arista).
5. **bdd ↔ facturacion: NO es ciclo** — solo facturacion→bdd. Pero hay duplicación de lógica: `bdd/ajax.py` y `facturacion/views.py` ambos escriben `Lista_Pedidos` al tocar el carrito.
6. **Interno:** `bdd/urls.py` importa vistas de `views_old.py` (Imprimir, ItemsView, ListarCarteles — líneas 5-8, 23) Y de `views/` — dos implementaciones completas conviven; `facturacion` importa `Inicio` de ambos (el de views_old queda muerto).

### Acoplamiento por metadata en DB (DB-driven views)

- **`bdd/urls.py:38-54`**: en import-time itera `NavBar.objects.all()` → `Armador.objects.get(nav_bar=...)` → `import_string("bdd.views." + armador.vista)`. Todo envuelto en `try/except: pass` — una fila rota = URL que desaparece en silencio. **Ninguna migración seedea Armador/NavBar** (único RunPython es `bdd/migrations/0003` que backfill `Item.*_base`); las filas solo existen en la DB de prod → una instalación fresca no tiene rutas dinámicas.
- **`MiVista.get_context_data`** (`views/base.py:66`): `Armador.objects.filter(url=self.request.path)` — toda subclase (incl. `actualizador.Actualizar`) depende de una fila DB que coincida con su path.
- **`apps.get_model` hardcodeado a `("bdd","x_cartel")`** en 3 lugares: `views/base.py:82-88`, `views/forms.py:69-76`, `views_old.py:113-200,440-444` → `Armador.modelo`/`formulario` pueden apuntar a modelos de `x_cartel`: la metadata DB de bdd **alcanza el schema de otra app**. Agregar una tercera app requiere tocar 3 archivos.
- **`core_andamios.context_processors.mi_procesador_de_contexto`** (settings.py:350) inyecta `barra_de_navegacion` con su propio `Nav_Bar` en TODA request; `MiVista` lo pisa con `bdd.NavBar` (misma key de contexto — colisión de andamios).
- **`admin.py` de bdd** auto-registra los 30 modelos vía `inspect`; los admin de `x_articulos`, `core_elementos`, `core_andamios` son clones con nombres de modelos bdd embebidos como strings.
- **Nadie fuera de bdd escribe `Armador`/`NavBar`/`Formulario_Campos`** — solo lectura (`facturacion` lee NavBar; `actualizador` requiere la fila Armador de `/actualizar/`).

### Acoplamiento por templates

- `static/templates/` es DIR global (`settings.TEMPLATES[0].DIRS`). `generic_template.html`, `base.html`, `base2.html`, muros y plantillas del Armador viven ahí.
- **`facturacion`** (4 templates) extiende `base2.html`, que itera `barra_de_navegacion` con campos **`nav.url_inicial`/`nav.text_display` de `bdd.NavBar`** y badges `nuevas_planillas`/`nuevas_planillas_descarga` (context keys que solo `MiVista` produce — en las TemplateView de facturacion quedan vacíos).
- **`reportes`** extiende `base.html` — navbar con URLs Armador hardcodeadas (`/carrito/0`, `/planilla_diaria/0`, `/registros`, `/index_actualizador`).
- **`actualizador/templates/actualizar.html`** hace `{% load custom_filters %}` (filtros de bdd con lógica de negocio hardcodeada: `*1.15`, abreviaturas de proveedores).
- **`pedido`** tiene `base_pedido.html` propio (UI desacoplada; solo modelos). **`administracion_financiera`** idem (base propia Tailwind). **`x_articulos`/`core_index`** usan `core_andamios` (andamio paralelo).
- **Templates muertos de `cajas`** llaman endpoints AJAX de bdd (7 refs).

### Blast radius por subdominio (consumidores ordenados por "pegamento")

| Subdominio bdd | Consumidores (de más a menos pegado) | Tipo de pegamento |
|---|---|---|
| **Patoba + funtions** | actualizador (5 archivos, internals filtrados: `*_service`, `obtener_id_por_nombre`, `copiar_reemplazable`, `actualizar_plantilla`, `borrar_por_id`, `subir/descargar_sqlite3_a_drive`, `listar`, `download_and_zip_files`) → scripts raíz → `bdd.management.commands.procesar_emails` → `views_old` → **reportes (solo vía adapter, mínimo)** | API surface enorme sin interfaz; credenciales user id=1 implícitas |
| **Inventario/precios (Item et al.)** | actualizador (escribe `*_base`, `recompute_finales`) → facturacion (FK + lee `final/final_efectivo` en runtime) → pedido (3 FKs + lectura de campos) → x_cartel (3 modelos FK + JSON de precios) → x_articulos → utils/scripts | Schema + semántica de precios compartida |
| **Lista_Pedidos** | pedido (7 archivos + transiciones de estado) → facturacion (write-through al editar carrito) → bdd ajax (escribe) → utils/scripts | Tabla pivot compartida bdd↔pedido↔facturacion, escrita desde 3 apps |
| **Carrito (Carrito/Articulo/ArticuloSinRegistro)** | facturacion (4 archivos + 2 FKs en ArticuloVendido) → bdd ajax (dueño de endpoints) | Monopolio de lectura de facturacion; escritura dividida |
| **Proveedor/ListaProveedores/Listado_Planillas** | administracion_financiera (4 FKs + O2O) → pedido (4 FKs) → x_cartel (3 FKs) → actualizador (Listado_Planillas = su persistencia) → utils/scripts | FKs de schema en 4 apps |
| **UI-metadata (NavBar/Armador/Muro/Contenedor/*_Campos)** | bdd (dueño) → facturacion (lee NavBar + base2.html) → actualizador (requiere fila Armador) → templates compartidos | Metadata en DB + context keys + template dir global |
| **MiVista/MyForm** | actualizador (única subclase externa) | Herencia de vista base |
| **Registros/Tipo_Registro + modelos muertos (MetodoPago, Ticket, Tipo, Estructura)** | nadie fuera de bdd | Libre |
| **views_old.py** | urls propias (3 rutas activas) + import muerto en facturacion | Duplicación interna |

## Affected Areas

- `bdd/models.py` — 32 clases; cualquier cambio de schema es blast-radius a 5 apps con FKs.
- `bdd/urls.py` — import-time DB + `import_string` + import cross-app de pedido.
- `bdd/views/base.py`, `bdd/views/forms.py`, `bdd/views_old.py` — `apps.get_model` hardcodeado bdd/x_cartel; MiVista heredada por actualizador.
- `bdd/classes.py` (Patoba) + `bdd/funtions.py` — integración Google consumida por 4 archivos de actualizador + reportes + scripts.
- `bdd/templatetags/custom_filters.py` — lógica de negocio (`*1.15`, abreviaturas) en filtros de template.
- `actualizador/` — consumidor más profundo (sin modelos propios); duplicados raíz `actualizador_main.py`/`actualizador_csv.py`.
- `facturacion/` — models.py (FKs), funtions/classes (schema carrito), views (NavBar + write-through a Lista_Pedidos), templates (base2.html).
- `pedido/` — models.py (7 aristas FK), views/* (Lista_Pedidos), `views/externo.py` (importado por bdd.urls).
- `x_cartel/models.py` — 6 aristas FK; bdd escribe sus tablas.
- `administracion_financiera/models.py` — 4 FKs a Proveedor.
- `static/templates/base.html`, `base2.html`, `generic_template.html`, muros/plantillas — template dir global.
- `core_config/urls.py:34` — `include("bdd.urls")` en `""`.
- `core_config/settings.py` — context processor de core_andamios (colisión `barra_de_navegacion`), handlers de log por app, keys consumidas por bdd.
- `utils/queryset_to_xlsx.py` — ciclo utils↔bdd.
- `scripts/deploy.sh`, `scripts/migrate_sqlite_to_pg.sh`, `recrear_descargables.py`, `script.py`, `fix_proveedores.py`, `script_seteado_false_lista_faltantes.py`, `ejecutar_utils.py` — tooling acoplado.

## Approaches

1. **Extracción por capas con shims de compatibilidad (recomendado)** — orden sugerido por menor blast radius:
   1. Modelos muertos + `Registros`/`Tipo_Registro` (cero consumidores externos).
   2. Romper ciclos baratos: mover `agregar_al_pedido` de `bdd/urls.py` a `pedido/urls.py` (corta bdd→pedido); `views_old` → consolidar las 3 vistas vivas en `views/` y borrar.
   3. `Patoba`+`funtions` → paquete `integraciones/` propio (reportes ya demuestra el patrón adapter; actualizador migra último por su uso de internals).
   4. UI-metadata (NavBar/Armador/muros/MyForm) → `core_andamios` o app `scaffold` propia, con `bdd` re-exportando temporalmente.
   5. Carrito → mover `Carrito/Articulo/ArticuloSinRegistro` a `facturacion` (único consumidor fuera de bdd) con `db_table` preservado.
   6. `Lista_Pedidos` → `pedido` (la mayoría de escrituras ya son de pedido; bdd.ajax y facturacion quedarían como consumidores).
   7. Proveedores (`Proveedor/ListaProveedores/Condiciones/Archivo/Compras/Listado_Planillas`) → app `proveedores` consumida por pedido+af+x_cartel+actualizador.
   8. `Item`+inventario — último, lo más pegado (4 apps con FK, semántica de precios en modelos + filtros + actualizador).
   - Pros: cada paso es revertible, shims mantienen `from bdd.models import X` funcionando durante la transición. Cons: largo; requiere `SeparateDatabaseAndState`/db_table para no tocar migraciones históricas (`to='bdd.item'` queda congelado en migraciones ajenas — eso es OK mientras la tabla no se mueva).
   - Effort: High (pero incremental).

2. **Big-bang: congelar `bdd` como "legacy kernel" y construir apps nuevas alrededor** — dejar bdd intacto, prohibir nuevos imports directos, reexportar vía fachada.
   - Pros: cero riesgo inmediato. Cons: no reduce acoplamiento real; la god-app sigue creciendo.
   - Effort: Low-Medium.

3. **Solo romper ciclos + documentar fronteras (quick wins)** — ejecutar los pasos 1-3 del approach 1 como change acotado.
   - Pros: alto valor/esfuerzo; elimina las 3 aristas entrantes de bdd y la duplicación views_old. Cons: no toca el problema estructural mayor.
   - Effort: Medium.

## Recommendation

Empezar por el **Approach 3** como primer change concreto: (a) mover el path `agregar_articulo_a_pedido` a `pedido/urls.py`, (b) consolidar `Imprimir/ItemsView/ListarCarteles` fuera de `views_old.py` y borrar el archivo + el import muerto en `facturacion/views.py:5`, (c) extraer `Patoba`/`funtions` a un módulo de integración con `bdd.classes` re-exportando (shim de 2 líneas). Esto elimina los 3 ciclos reales y baja el bus factor sin tocar un solo FK. Después, Approach 1 en el orden de la tabla de blast radius — la evidencia dice que `Registros`/modelos muertos y la UI-metadata son lo más seguro, y `Item` es lo último que se debe tocar.

## Risks

- `bdd/urls.py` consulta DB en import-time: cualquier refactor de urls/models puede eliminar rutas silenciosamente (el `except: pass` traga todo). Tests actuales: **cero cobertura sobre bdd** — no hay red de seguridad.
- Migraciones históricas de 5 apps referencian `to='bdd.item'/'bdd.proveedor'/'bdd.articulosinregistro'` — renombrar el app_label requiere cirugía de migraciones o mantener el label.
- Las filas `Armador`/`NavBar` solo existen en prod (sin seed/fixture): un error de refactor puede dejar el sistema sin rutas y no se detecta en un entorno fresco (que ya nace sin rutas).
- `actualizador` usa internals de Patoba (`*_service` expuestos) — extraer Patoba sin adapter intermedio rompe 5 archivos a la vez.
- `base2.html`/`base.html` acoplan templates de facturacion/reportes a campos de `bdd.NavBar` y context keys de `MiVista` — mover la UI-metadata rompe el navbar en 2 apps.
- `facturacion/classes.py` `ComandoFiscal` hace `prefetch_related("articulo_set__item")` — related_name incorrecto (bdd usa `related_name="articulos"`): código legacy probablemente roto/muerto, cuidado al tocar `Articulo`.
- Scripts raíz duplicados del actualizador importan los mismos símbolos — un rename requiere tocar copias que no están en el app dir.
- `apps.get_model` hardcodeado a `bdd`/`x_cartel` en 3 archivos: la metadata Armador puede referenciar modelos de x_cartel; extraer modelos sin migrar esas filas rompe vistas enteras.

## Ready for Proposal

**Sí — para un change acotado de desacoplamiento inicial** (Approach 3: romper los 3 ciclos + eliminar views_old + shim de Patoba). La extracción completa (Approach 1) requiere su propia cadena de changes por subdominio; esta exploración provee el baseline y el orden seguro de extracción.
