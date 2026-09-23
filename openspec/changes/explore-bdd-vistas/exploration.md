# Exploration: `bdd` — vistas, URLs y el motor de vistas autogeneradas por DB (baseline para refactor)

**Tipo:** exploración standalone, refactor-oriented — slice "vista/URL/UI machinery" del deep-dive sobre la god-app `bdd`.
**Fecha:** 2026-10-02 · **Rama:** `produccion` (v3.10.x)
**Fuentes:** verificación directa del código (`bdd/urls.py`, `bdd/views_old.py`, `bdd/views/{__init__,base,main,ajax,forms,utils}.py`, `bdd/models.py`, `core_config/urls.py`, `core_andamios/`, `actualizador/views.py`, `pedido/`, `static/templates/`), `bdd/DOCUMENTATION.md`, `openspec/changes/explore-{arquitectura-monolito,flujo-carteles,subtitulos-subcarpetas}/exploration.md`, y volcado **read-only** de `db.sqlite3` (`mode=ro&immutable=1`).

---

## El límite motor-genérico vs bespoke (respuesta a la pregunta del owner)

El "motor" es: registro `NavBar` + registro `Armador` en DB → `bdd/urls.py` genera la `path()` en import-time → `import_string("bdd.views.<vista>")` → `MiVista.get_context_data` arma el contexto completo (muro + contenedor→plantillas + modelo + MyForm + títulos) → `generic_template.html` hace `{% include muro %}` → el muro hace `{% include lista_html.N %}`.

**Estado real de los 6 NavBar en DB (`bdd_navbar`):**

| NavBar (url_inicial → text_display) | Armador | Resolución real |
|---|---|---|
| `buscador/` → "Buscador" | id=3, vista=`Inicio`, url=`/buscador/` | ✅ **Motor completo**: ruta dinámica + `views.main.Inicio` + muro_doble + contenedor `doble_buscador` (a=plantilla_formulario, b=tabla_buscador), modelo=Item, busqueda=1 |
| `actualizar/` → "Actualizar" | id=8, vista=`Actualizar` | ⚠️ **Híbrido**: `bdd.views.Actualizar` NO existe → `except: pass` mata la ruta dinámica; la URL sale por `actualizador/urls.py:6` → `actualizador.views.Actualizar(MiVista)` que SÍ consume el contexto del Armador (url=`/actualizar/` matchea) pero **pisa `lista_html`** con `["actualizar.html"]` hardcodeado (`actualizador/views.py:62-64`) |
| `descargar_planillas/` → "Descargar Planillas" | id=9, vista=`Inicio`, url=`/descargar_planillas/` | ✅ **Motor**, con twist: el muro apunta a `descargar_planillas.html`, que ya es contenido completo (no wrapper de includes) → el contenedor (a=descargar_planillas) es peso muerto. busqueda=0 → POST crea `Listado_Planillas` via `MyForm.save` (formulario_campos=`__all__`!) |
| `pedidos/home/` → "Pedidos" | id=11, vista=`ListadoPedidos`, url=`/lista_pedidos/` | ❌ **Doblemente muerto**: (a) `path("pedidos/", include("pedido.urls"))` (core_config/urls.py:31) se monta ANTES que `bdd.urls` (línea 34) → `pedidos/home/` lo resuelve `pedido.views.home.HomeView`; (b) aunque ganara, `Armador.url="/lista_pedidos/"` ≠ `request.path="/pedidos/home/"` → `armador=None` → muro `muro_default.html` (inexistente) → 500 |
| `listar_carteles/` → "Listar Carteles" | (sin Armador) | 🚪 **Escaped**: `Armador.DoesNotExist` → `except: pass` → sin ruta dinámica; la sirve la ruta estática `urls.py:110` → `views_old.ListarCarteles` (muro/plantillas hardcodeadas en la vista) |
| `facturacion/` → "Planilla Diaria" | (sin Armador) | 🚪 **Escaped total**: sin Armador ni ruta en `bdd`; `facturacion/urls.py:83` → `Facturacion` con `facturacion/facturacion.html` propio |

**Resumen del límite:** el motor solo sobrevive íntegro en **2 pantallas** (`/buscador/`, `/descargar_planillas/`); `/actualizar/` usa el motor como proveedor de contexto pero con URL y contenido bespoke; `/listar_carteles/` e `/imprimir*/` escaparon a vistas hardcodeadas que solo reutilizan `generic_template.html` + `MyForm`; `pedidos/home` y `facturacion/` son apps propias. Además hay configuración Armador/Contenedor vestigial en DB (muros `imprimir_tabla`, `simple`; contenedores `prueba`, `simple`, `registros`, `imprimir-tabla`, `tabla_mp`, `contenedor_listar_carteles`, `caja_doble`) sin efecto.

## Current State

### 1. `bdd/urls.py` (124 líneas) — rutas y quirks

- **Import-time DB query** (líneas 34-67): `NavBar.objects.all()` se evalúa al importar el módulo (incluso dos veces: línea 38 `dos = ...` es variable muerta, línea 41 el loop real). Por cada NavBar: `Armador.objects.get(nav_bar=nav_bar)` + `import_string(f"bdd.views.{armador.vista}")`. **Inner `except: pass` desnudo (línea 53)** traga `Armador.DoesNotExist`, `Armador.MultipleObjectsReturned` (FK no es unique) e `ImportError` de vista inexistente — sin logging. El `try/except Exception` exterior (34/65) deja `armador_paths=[]` si la DB no responde al import (ej. durante `migrate` en DB vacía) — las rutas dinámicas desaparecen silenciosamente.
- **Resultado verificado en DB:** se generan 3 rutas dinámicas (`buscador/`, `descargar_planillas/`, `pedidos/home/`); `actualizar/` falla por vista inexistente; `listar_carteles/` y `facturacion/` fallan por falta de Armador.
- **15 rutas estáticas** (líneas 76-116): mix de `views_old` (`ItemsView`, `Imprimir`×3, `ListarCarteles`), `views.ajax` (10 funciones) y `pedido.views.externo.agregar_al_pedido` importada en el espacio de URLs de bdd (`agregar_articulo_a_pedido/<int:articulo_id>/`).
- **Namespacing:** `bdd/urls.py` NO tiene `app_name` → nombres globales. Quirks: nombres con espacios (`"imprimir tabla"`, `"imprimir 1 cartel"`), nombres dinámicos = `nav_bar.text_display` ("Descargar Planillas", "Planilla Diaria"), duplicado semántico `mi_vista_ajax`/`mi_vista_ajax_get` para el mismo endpoint. `items/<int:cajon_id>` sin barra final.
- **`reportar_item` y `enviar_reporte`** están exportados en `views/__init__.py` pero **no tienen `path()`** en ningún urls.py → endpoints muertos (el `enviar_reporte` es `@csrf_exempt`, o sea que si se cableara sería un POST sin CSRF ni auth).

### 2. `bdd/views_old.py` (1242 líneas) — inventario alcanzable vs muerto

| Bloque | Líneas | Estado |
|---|---|---|
| Widgets `DateInput/TimeInput/DateTimeInput/EmailInput` | 51-85 | Muertos (dup en `views/forms.py:15-52`) |
| `MyForm` | 87-153 | Muerto (dup en `views/forms.py:55-171`; además esta versión tiene bug: los dos `try/except` de `get_model` dejan `model` posiblemente indefinido) |
| `MiVista` | 156-491 | Muerta (la activa es `views/base.py`); incluye llamada BCRA por-request (líneas 269-285) que el refactor eliminó |
| `Inicio`, `Prueba` | 494-527 | Muertas |
| `BusquedaForm` | 533-541 | Muerto |
| `BusquedaView` | 544-583 | Muerto (sin URL) |
| **`ItemsView`** | 586-604 | **Cableado** (`items/<int:cajon_id>`) pero su único caller es `plantilla_prueba_respaldo.html` (template muerto) → endpoint dormido, devuelve items por cajón sin auth |
| **`Imprimir`** | 610-701 | **ACTIVO** — 3 URLs (`imprimir/`, `imprimir/tabla/`, `imprimir/carteles/1/`); la 3ª cae sin `muro` (get_context_data solo maneja las 2 primeras) |
| `crear_modificar_lista_pedidos` | 707-771 | Muerto (dup; además `proveedor_id=1` por defecto difiere del refactor `None`) |
| `seleccionar_proveedor` | 774-776 | Muerto (dup) |
| `cambiar_cantidad_pedido` | 779-793 | Muerto (dup) |
| `editar_item` | 799-855 | Muerto (dup) |
| `agregar_articulo_a_carrito` | 858-900 | Muerto (dup; esta versión no chequea `is_authenticated` para responder — retorna `{"status":"ok"}` igual) |
| `carrito_to_dict`, `carrito` | 903-918 | Muertos |
| `ListadoPedidos` | 921-986 | Muerto |
| `articulo_to_dict`, `calcular_total` | 989-1019 | Muertos (float en vez de Decimal en la versión vieja) |
| `consultar_carrito` | 1022-1078 | Muerto (con hardcodeo `str(request.user)=="darkydiel"` + carrito ids 2/3 — la versión refactor usa grupos `cajeros`/`caja_general`) |
| `usuarios_caja` | 1081-1089 | Muerto (lista hardcodeada Mati/Carlos) |
| `eliminar_articulo_pedido` | 1092-1104 | Muerto |
| **`ListarCarteles`** | 1110-1195 | **ACTIVO** (`listar_carteles/`) — GET con side-effect `CartelesCajon.get_or_create` por cada cajón (mutación en GET, sin auth) |
| `descargar_archivo` | 1198-1205 | Muerto (dup; urls usa la de `views/ajax.py`) |
| `reportar_item`, `enviar_reporte` | 1208-1242 | Muertos (sin URL siquiera en la versión nueva) |
| Imports `Patoba` (l.16), `get_emails` (l.18), `ast`, `pandas`, `MediaIoBaseDownload` | — | Importados pero no usados en el archivo |

**Superficie activa de `views_old` = 3 clases (~270 líneas). ~970 líneas son duplicado muerto.**

### 3. `bdd/views/` — el refactor abandonado (qué es dup vs único)

- `__init__.py` (24 l.): re-exporta 7 vistas de `main` + 12 funciones de `ajax`. **Es lo que `import_string("bdd.views.X")` resuelve** — o sea que las rutas dinámicas ya usan el código nuevo.
- `base.py` `MiVista` (528 l.): **ACTIVA** — la ejecutan `Inicio` (buscador + descargar_planillas) y `actualizador.Actualizar` por herencia. Única vs views_old: logging, `armador=None` con defaults (muro_default.html **inexistente** → 500 si ocurriera), `LookupError` en vez de `except:`, MP extraído a `buscar_pagos_mp()`, `tabla_link_pedidos` desde settings (el default hardcodeado de Poxipol quedó en views_old), **eliminó la llamada BCRA**. Bug latente: línea 139 loguea `armador.nombre` — `Armador` no tiene campo `nombre` → AttributeError si se dispara esa rama (tragada por el `except Exception` de línea 197, que deja `muro_error.html` inexistente → 500).
- `main.py` (631 l.): `Inicio` **ACTIVO** vía rutas dinámicas. `Prueba`, `BusquedaView`, `ItemsView`, `Imprimir`, `ListadoPedidos`, `ListarCarteles` = **muertos** (urls importan de `views_old` o no hay ruta). El `Imprimir` refactor tiene bugs: `campos_tabla`/`titulos_tabla` (keys distintas a las `campos`/`titulos` que espera el flujo viejo), `self.request.path = "/imprimir/tabla/"` mutando el request (línea 319), doble llamada a `get_context_data`. `ListarCarteles` refactor es semánticamente distinto (filtro `revisar` distinto, prefetch, `items_filtrados`) — NO es drop-in replacement.
- `ajax.py` (826 l.): **ACTIVO** salvo `reportar_item`/`enviar_reporte` (sin URL). Único vs views_old: `_is_caja_general`, `_get_cajeros_queryset` (grupo `cajeros`), `_user_color`/paleta, `_item_base_price_columns_exist`/`_item_factor_division_column_exists`/`_item_queryset_runtime_safe` (introspección de columnas para compat hotfix), validaciones (cantidad>0, coma decimal, FKs inexistentes → 400), respuestas 401/404/405.
- `forms.py` (183 l.): **ACTIVO** (`MyForm` usado por MiVista y por `actualizador.views`; `BusquedaForm` muerto con BusquedaView).
- `utils.py` (168 l.): **ACTIVO** (`articulo_to_dict`, `calcular_total` con Decimal, `carrito_to_dict` — importados por ajax.py).

### 4. Endpoints AJAX — auth / CSRF / mutaciones (verificado)

Ninguna URL de `bdd` tiene `login_required`/`LoginRequiredMixin`; no hay middleware de auth global (`core_config/settings.py:293-302`).

| Endpoint (ruta) | Función | Auth | CSRF | Muta | Caller real |
|---|---|---|---|---|---|
| `items/<int:cajon_id>` | `views_old.ItemsView` | ❌ | GET | No | Solo `plantilla_prueba_respaldo.html` (muerto) |
| `seleccionar_proveedor/` | ajax | ❌ | n/a (sin check de método) | No | Ningún link (URL manual) |
| `carrito/` | ajax | ✅ 401 | GET | `Carrito.get_or_create` | tabla_lateral_carritos |
| `editar_item/<id>/` | ajax | ❌ | POST con token | **Item** (stock, barras, tiene_cartel, cajon, proveedor, sub_titulo, factor_division + recompute_finales) | modal `tabla_buscador.html` |
| `agregar_articulo_a_carrito/<id>/` | ajax | ✅ 401 | POST token | `Carrito`/`Articulo`/`Lista_Pedidos` | `tabla_buscador.html` |
| `cambiar_cantidad_pedido/<id>/<cant>/` | ajax | ❌ | POST token | `Lista_Pedidos` (update/delete) | `seleccionar_proveedor.html` (template huérfano) |
| `crear_modificar_lista_pedidos/` (+`/<prov>`) | ajax | ❌ | POST token | `Lista_Pedidos` + `Item.trabajado/proveedor` | `seleccionar_proveedor.html` |
| `consultar_carrito/` | ajax | ✅ 401 | GET | `Carrito.get_or_create` (side-effect) | polling 3s `tabla_lateral_carritos` |
| `usuarios_caja/` | ajax | ❌ | GET | No (expone lista de usuarios cajeros) | `tabla_lateral_carritos`, `tabla_buscador` |
| `eliminar_articulo_pedido/` | ajax | ❌ | POST `csrfmiddlewaretoken` | `Lista_Pedidos` (confirm/delete) | `tabla_pedidos.html` (¡template solo alcanzable vía ruta shadowed!) |
| `imprimir/` + `imprimir/tabla/` + `imprimir/carteles/1/` | `views_old.Imprimir` | ❌ | POST token | No (solo filtra) | URL manual (sin NavBar) |
| `listar_carteles/` | `views_old.ListarCarteles` | ❌ | GET | **Sí: `CartelesCajon.get_or_create` ×39 en GET** | NavBar "Listar Carteles" |
| `descargar_archivo/` | ajax | ❌ | GET | No (sirve `MEDIA_ROOT/script_pyinstaller.py`) | Sin link |
| `agregar_articulo_a_pedido/<id>/` | `pedido.views.externo.agregar_al_pedido` | ❌ | **ni siquiera chequea método** | **Sí en GET**: crea `ArticuloPedido`+`Pedido`, decrementa `Lista_Pedidos.cantidad` | `tabla_buscador.html` (botón "Agregar al pedido") |
| Rutas Armador (`buscador/`, `descargar_planillas/`, `pedidos/home/` muerta) | `views.main.Inicio/ListadoPedidos` | ❌ | POST token | **`MiVista.post` → `MyForm.save` crea una instancia del modelo del Armador** (en descargar_planillas: `Listado_Planillas` con `__all__` los campos) | navbar |

**Huecos de auth (mutaciones sin login):** `editar_item` (el más grave: edita cualquier Item por id), `eliminar_articulo_pedido`, `cambiar_cantidad_pedido`, `crear_modificar_lista_pedidos`, `ListarCarteles` (GET), `agregar_articulo_a_pedido` (GET!), `MiVista.post` en armadors con `busqueda=False`. Lecturas sin auth: `usuarios_caja` (user list), `seleccionar_proveedor`, `ItemsView`, `descargar_archivo`, todas las páginas.

### 5. Templates — motor vs bespoke (`static/templates/`)

- **Shell del motor:** `generic_template.html` (196 l.) — navbar desde `barra_de_navegacion`, `tabla_lateral_carritos.html` **siempre incluida** (1001 l., polling 3s a `/consultar_carrito/` y endpoints de facturacion), `{% include muro %}` salvo en `/imprimir/tabla/` (impresión limpia), `{{ payments|safe }}` → si una vista no setea `payments` renderiza `var payments = ;` → SyntaxError JS (ej. `views_old.ListarCarteles` no lo setea).
- **Muros vivos:** `muro_doble.html` (buscador, listar_carteles), `muro_simple.html` (actualizar vía Armador 8 — aunque el contenido se pisa), `muro_imprimir.html` (`/imprimir/tabla/`), `descargar_planillas.html` usado *como muro* (contenido completo, no wrapper).
- **Plantillas vivas (contenido):** `plantilla_formulario.html` (form dinámico + Select2 + `tabla_link_pedidos`), `tabla_buscador.html` (401 l., buscador), `descargar_planillas.html` (JS → `/actualizador/marcar_descargado/`), `imprimir_carteles_x6.html` (grilla x6, bug `{{ dato.descripcion }}}` l.9), `tabla_listado_carteles_prueva.html`, `plantilla_formulario.html`+`muro_*` usados también por las vistas escaped (`Imprimir`, `ListarCarteles` hardcodean los mismos nombres).
- **Muertos/huérfanos:** `base.html`+`base2.html`+`base_{buscador,buscando,carrito,inicio,registros,usuario,actualizador}.html` (cadena extends sin consumidores), `plantilla_prueba.html`/`plantilla_prueba_respaldo.html` (BusquedaView muerto), `tabla_pedidos.html` (ruta shadowed), `tabla_listado_carteles.html` (la viva es `_prueva`), `imprimir_tabla.html`, `tabla_registros.html`, `mp.html`, `tabla_mp.html` (MP off: `INTEGRATE_MERCADOPAGO` ni existe en settings → siempre `[]`), `parrafo.html`, `seleccionar_proveedor.html` (vista sin link), `tabla_link_pedidos.html` (sí se incluye, pero con 1 link hardcodeado).
- `bdd/templates/` está **vacío**; todo vive en `static/templates/` (DIR global) → cero encapsulación.

### 6. `core_andamios` — el scaffold paralelo

- Modelos propios (`Nav_Bar`→`Url`→`Contenedor`/`Script`/`Pie`, `Contexto` JSON): el diseño original "todo por DB"; en DB hay apenas 2 Nav_Bar + 4 Url (bienvenida, docs, articulos, facturacion).
- `context_processors.mi_procesador_de_contexto` (`settings.py:350`) corre en **toda** request e inyecta `barra_de_navegacion = Nav_Bar.objects.all()` — **pisado por `MiVista`/`Imprimir`/`ListarCarteles`** que lo reescriben con `bdd.NavBar`. En páginas de otras apps que usan `generic_template` no hay conflicto porque ninguna otra la usa; en templates que sí consumen `barra_de_navegacion` del processor (ej. `core_andamios/core_navbar.html`, usado por `core_index/index.html`) muestra las entradas core_andamios.
- Solapamiento real: dos tablas navbar (bdd_navbar ↔ core_andamios_nav_bar), dos conceptos contenedor (bdd.Contenedor a/b/c→Plantilla vs core_andamios.Url→Contenedor html string), una query desperdiciada por request y una fuente de confusión de nombres de contexto (`barra_de_navegacion` tiene dos productores).
- `ContextoAndamio` (core_andamios/views.py) solo la usa `core_index.Vista_Index` (`/bienbenida/`).

### 7. Clasificación para refactor

- **Extraíbles tal cual (independientes del motor):** `views/ajax.py` completo (12 funciones, no tocan Armador) — solo necesitan auth; `views/utils.py`; `pedido.agregar_al_pedido` (re-montar en pedido.urls); `views_old.ItemsView`/`Imprimir`/`ListarCarteles` (autocontenidas, hardcodean contexto — extraer y migrar a las versiones de `views/main.py` corrigiendo sus bugs, o consolidar).
- **Pegadas al motor (no mover sin decidir suerte del Armador):** `views/base.MiVista`, `views/main.Inicio` (y por herencia `actualizador.Actualizar`), `views/forms.MyForm`, `generic_template.html` + muros + `plantilla_formulario`/`tabla_buscador`/`descargar_planillas`, modelos NavBar/Muro/Plantilla/Contenedor/*_Campos/Armador.
- **Muerto confirmado (borrable):** todo `views_old.py` menos las 3 clases activas; `views/main.py` `{Prueba, BusquedaView, ItemsView, Imprimir, ListadoPedidos, ListarCarteles}` (las 5 no-Inicio); `ajax.{reportar_item, enviar_reporte}`; `BusquedaForm`; los base_*.html; plantillas huérfanas listadas arriba; Armador 8 y 11 en DB (inertes) + config vestigial de contenedores/muros.

## Affected Areas

- `bdd/urls.py` — generación dinámica + 15 estáticas + import de `pedido.views.externo`
- `bdd/views_old.py` — 3 vistas activas + ~970 líneas muertas
- `bdd/views/{__init__,base,main,ajax,forms,utils}.py` — refactor parcialmente activo
- `bdd/models.py:404-541` — NavBar/Muro/Plantilla/Contenedor/Modelo_Campos/Formulario_Campos*/Armador (config en DB: `bdd_navbar` 6 filas, `bdd_armador` 4, `bdd_contenedor` 11, `bdd_plantilla` 14, `bdd_muro` 5, tablas `*_campos`)
- `static/templates/` — generic_template + muros + plantillas del motor + huérfanas
- `core_andamios/` — scaffold paralelo (models, context_processors, views, templates) + registro en `settings.py:242,350`
- `actualizador/views.py:59+` — `Actualizar(MiVista)`: consumidor externo del motor
- `facturacion/views.py:5` — import muerto `from bdd.views_old import Inicio`
- `pedido/views/externo.py:9` — `agregar_al_pedido` montado en el espacio de URLs de bdd
- `core_config/urls.py:27-40` — orden de includes (pedido antes que bdd → shadowing) + ausencia de prefijos

## Approaches

1. **Matar el motor, explotar las vistas (recomendado si el owner ya no agrega pantallas por DB)** — convertir `buscador/` y `descargar_planillas/` en rutas estáticas explícitas; `MiVista` → mixin/context-builder explícito (`build_chrome_context()`); las 3 vistas activas de views_old → port a `views/main` corrigiendo bugs; borrar views_old + modelos Armador\* + templates huérfanos.
   - Pros: elimina la DB→import-time coupling, el `except: pass`, la doble navbar, y ~1000 líneas muertas; URLs declarativas. Cons: pierde la "agregar pantalla sin deploy" (feature ya no usada: últimos Armadors son de pantallas viejas); requiere data migration para borrar/backup de las tablas de config. Effort: Medium.

2. **Conservar el motor, endurecerlo** — quitar `except: pass` (log + fallback), caché del armador_paths o regeneración lazy (`get_pagina_urlpatterns` tipo feincms/ wagtail-style resolver), `app_name`/`namespace`, auth en AJAX.
   - Pros: mínima disrupción funcional. Cons: sostiene un framework casero para 2 pantallas; sigue el acople bdd↔DB↔import_string. Effort: Low-Medium.

3. **Solo higiene** — apuntar los 3 imports de urls.py a `views/main` (hay que arreglar los bugs del refactor antes), borrar lo muerto, no tocar el motor.
   - Pros: trivial y reversible. Cons: no resuelve nada estructural; `views/main.ListarCarteles` difiere semánticamente (hay que reconciliar). Effort: Low.

## Recommendation

Baseline ya mapeado. Si el change es "eliminar el motor": Approach 1, con orden (a) cablear `buscador`/`descargar_planillas` estático, (b) portar `Imprimir`/`ListarCarteles`/`ItemsView` a views (o dejar views_old solo con esas 3 clases), (c) auth en mutaciones, (d) borrar. Si el motor queda (decisión del owner, que lo construyó para ahorrar código): Approach 2 + quitar la rama muerta `pedidos/home`/`Actualizar` del Armador en DB. En ambos casos **primero cerrar los huecos de auth** (editar_item, eliminar/cambiar pedidos, agregar_al_pedido en GET) — eso es orthogonal y urgente.

## Risks

- `bdd/urls.py` consulta la DB en import-time: un `Armador` inválido borra rutas en silencio (`except: pass` sin log); en `migrate` sobre DB vacía las rutas dinámicas no existen.
- La UI depende de registros DB que no están en el repo ni en fixtures: cualquier refactor de nombres de vista/modelo/campo rompe pantallas sin error de deploy (el contrato `Armador.vista → import_string` y `formulario_campos → model._meta.get_field` es frágil a renombres).
- Mutaciones sin auth + `agregar_al_pedido` mutando en GET (crawlable) + `enviar_reporte` csrf_exempt (hoy sin ruta, pero un registro Armador/una línea de urls lo activaría).
- `views/main.py` NO es drop-in de views_old para `ListarCarteles` (semántica de filtro distinta) ni `Imprimir` (keys de contexto distintas, hack de `request.path`); un swap naíf rompe la pantalla de trabajo diaria de carteles.
- `tabla_lateral_carritos.html` se incluye en TODA página genérica (polling 3s); quitarla o cambiar sus endpoints requiere revisar todas las pantallas del motor.
- `actualizador.Actualizar` hereda `MiVista`: tocar `base.py` tiene blast-radius fuera de bdd.
- `generic_template.html` depende de `payments` siempre presente en contexto (SyntaxError JS si falta) y de `barra_de_navegacion` que dos productores distintos escriben.

## Tabla resumen: vista → motor? / activa? / auth? / extraíble?

| Vista | ¿Motor? | ¿Activa? | ¿Auth? | ¿Extraíble? |
|---|---|---|---|---|
| `views/base.MiVista` | ES el motor | Sí (Inicio×2, Actualizar hereda) | ❌ | Pegada — es lo que habría que desarmar |
| `views/main.Inicio` | Sí | Sí (`buscador/`, `descargar_planillas/`) | ❌ | Pegada (trivial: es MiVista) |
| `views/main.Prueba` | Sí | No (sin Armador `vista=Prueba`) | ❌ | Muerta — borrar |
| `views/main.BusquedaView` | No (FormView propio) | No (sin URL) | ❌ | Muerta — borrar |
| `views/main.ItemsView` | No | No (urls usan views_old) | ❌ | Muerta |
| `views/main.Imprimir` | Usa generic_template, no Armador | No (urls usan views_old) | ❌ | Muerta (con bugs) — portar o borrar |
| `views/main.ListadoPedidos` | Sí (Armador 11) | No (shadowed por pedido.urls + url mismatch) | ❌ | Muerta — borrar + limpiar Armador 11 |
| `views/main.ListarCarteles` | No | No (urls usan views_old) | ❌ | Muerta, semántica distinta — reconciliar |
| `views_old.Imprimir` | No (hardcodea) | **Sí** (`/imprimir/*`) | ❌ | Extraíble (autocontenida) |
| `views_old.ListarCarteles` | No (hardcodea) | **Sí** (`/listar_carteles/`) | ❌ + muta en GET | Extraíble |
| `views_old.ItemsView` | No | Cableada, caller muerto | ❌ | Extraíble/dormida |
| `views_old` resto (MiVista/Inicio/Prueba/Busqueda*/ListadoPedidos/AJAX/helpers) | — | **No** | — | Muerto — borrar ~970 l. |
| `views/ajax.*` (10 cableadas) | No | Sí | Parcial (3 con 401) | Extraíbles tal cual |
| `views/ajax.{reportar_item,enviar_reporte}` | No | No (sin URL) | ❌ + csrf_exempt | Muertas |
| `pedido.agregar_al_pedido` (montada en bdd.urls) | No | Sí | ❌ muta en GET | Mover a pedido.urls |
| `actualizador.Actualizar(MiVista)` | Consume contexto Armador, URL propia | Sí | ❌ | Pegada al motor vía herencia |

## Ready for Proposal

**Sí** — hay al menos 3 changes claros posibles: (1) hardening de auth en endpoints mutantes (independiente del motor), (2) eliminación del motor Armador con las 2 pantallas vivas cableadas a mano, (3) limpieza views_old/views (solo después de decidir 1↔2). El orquestador debería confirmar con el usuario si el motor "agregar pantallas por DB" sigue siendo una feature deseada — hoy sirve a 2 URLs efectivas.
