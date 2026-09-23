# Exploration: Flujo de trabajo ACTUAL de carteles (as-is)

**Tipo:** exploración standalone (sin change asociado) — baseline de seguridad antes de tocar carteles. No propone cambios.
**Fecha:** 2026-09-23 · **Rama:** `produccion` (v3.10.x, HEAD `e0c70f1`)
**Fuentes:** verificación directa del código (`x_cartel/`, `bdd/views_old.py`, `bdd/views/`, `bdd/models.py`, `bdd/urls.py`, `core_config/urls.py`, `static/templates/`, `actualizador/`, `utils/rounding.py`, `core_index/`), `bdd/DOCUMENTATION.md`, `docs/auditoria_documentacion.md`, `openspec/changes/explore-arquitectura-monolito/exploration.md` y volcado **read-only** de `db.sqlite3` local (`mode=ro`).

---

## Mapeo de vocabulario (tres conceptos distintos llamados "cartel")

| Concepto | Modelo | Tabla | Formato impreso | Cardinalidad real |
|---|---|---|---|---|
| **Cartel A4 por ítem** | `x_cartel.Carteles` | `x_cartel_carteles` (200 filas) | A4 completo 20.95×29.6 cm, fuente Anton | **vinculado por convención `Carteles.id == Item.id`** (NO por la FK `item`: 48/200 filas tienen `item_id NULL`) |
| **Cartel A4 por cajón** | `x_cartel.CartelesCajon` | `x_cartel_cartelescajon` (39 filas = una por `Cajon`) | A4 con placeholders multi-ítem `[[ dato_N.* ]]` | `id == cajon.id` por convención (`get_or_create(id=cajon.id)`); FK `item` sin uso real |
| **Cartelito (góndola chico)** | `x_cartel.Cartelitos` | `x_cartel_cartelitos` (35 filas) | 105×99 mm en grilla de 6 por hoja | OneToOne real a `Item` (`item_id` poblado); `habilitado` marca los que se imprimen |

Conceptos de cartel **fuera** del flujo vivo: `bdd.Tipo_Cartel` (tabla vacía), `Item.tipo_cartel` y `Item.p_c_efectivo/p_c_debito/p_c_credito` (campos muertos — solo los *omite* `x_articulos/views.py:53-56`), `articulos.Cartel` + `ArticuloProveedor.cartel` (app abandonada, 0 views/URLs), `static/templates/tabla_listado_carteles.html`, `static/templates/imprimir_tabla.html`, `x_cartel/templates/x_cartel/cartel.html` (templates muertos), `bdd/views/main.py` `Imprimir`/`ListarCarteles`/`ItemsView` (refactors **no cableados** — `bdd/urls.py:5,23` importa desde `views_old`).

## Current State

### 1. Puntos de entrada (quién hace click dónde)

1. **Navbar → "Listar Carteles"** (`bdd_navbar` id=12, `url_inicial='listar_carteles/'`): ruta estática `bdd/urls.py:110` → **`views_old.ListarCarteles`** (la versión de `views/main.py` está muerta). Es la pantalla de trabajo diaria.
2. **Buscador** (`/buscador/`, vista `Inicio`/Armador → `tabla_buscador.html`): cada fila tiene botón **"Cartel"** → `/x_cartel/imprimir/<item.id>`; visible solo si `item.tiene_cartel` (`tabla_buscador.html:30-34`). El modal **"Editar"** de la misma tabla tiene checkbox `tiene_cartel` que pega al AJAX `editar_item` (`bdd/views/ajax.py:386,412-423`).
3. **Página de bienvenida** `/bienbenida/` (`core_index/templates/core_index/index.html:12`): link "Carteles" → `/x_cartel/` → editor vacío (ver quirks).
4. **`/imprimir/` y `/imprimir/tabla/`** (`bdd/urls.py:107-109` → `views_old.Imprimir`): **sin link en ningún lado** — URL oculta (tipeo manual/bookmark). `imprimir/carteles/1/` también mapea a `Imprimir` pero la vista no maneja esa ruta (cae sin `muro`).
5. **`/x_cartel/imprimir_cartelitos/`** (`x_cartel/urls.py:31` → `Cartelito`): tampoco linkeada en templates — se entra tipeando la URL.
6. **Admin**: `x_cartel/admin.py` registra `Carteles` y `CartelesCajon` (**no** `Cartelitos`); `bdd` auto-registra sus modelos.
7. **Autenticación:** ninguna vista/endpoint de carteles tiene `login_required` ni permisos — todo el flujo es público.

### 2. Modelos (`x_cartel/models.py`)

- `Cartelitos` (líneas 5-18): `item` OneToOne→`bdd.Item`, `proveedor` FK, `revisar`, `habilitado`, `descripcion`. `save()` inicializa `descripcion=item.descripcion` solo en creación.
- `Carteles` (21-44): `item` FK (null), `proveedor` FK (null), `revisar`, `descripcion` + `tamano_descripcion` (default 100, px), `texto_final`, `final`, `texto_final_efectivo`, `final_efectivo` + sus `tamano_*` (px). `set_description()` existe pero **nunca se llama** → carteles nuevos quedan con `descripcion=None`.
- `CartelesCajon` (47-70): espejo de `Carteles` con `item` FK semánticamente vacío.
- Campos de `bdd.Item` involucrados: `descripcion`, `final`, `final_efectivo`, `final_rollo`, `final_rollo_efectivo`, `tiene_cartel` (flag de UI y de redondeo), `cajon`, `sub_carpeta`, `sub_titulo`, `proveedor`, `actualizado`, `factor_division`, `*_base`.

### 3. Flujo end-to-end

**(A) Origen del precio (upstream, sin Drive para el cartel en sí):**
Planilla proveedor (Gmail/Drive → CSV) → `actualizador/actualizador_csv.py` redondea `final`/`final_efectivo` con `round_price(is_cartel=False)` (líneas 676, 761) → se guardan en `Item.*_base` (`crear_o_actualizar_registro` renombra `final`→`final_base`, líneas 229-236) → `item.recompute_finales()` (`bdd/models.py:355-383`) deriva `final*` aplicando `factor_division` (si >1) y `round_price(is_cartel=item.tiene_cartel)` — si no hay factor, `final = final_base` tal cual.

**(B) Marcado para revisión:**
Al terminar de procesar cada proveedor, el actualizador hace `Carteles.objects.filter(proveedor=proveedor).update(revisar=True)` y lo mismo para `CartelesCajon` (`actualizador_csv.py:882-893`; duplicado en `actualizador_main.py:389-402` + llamadas en 737 y 1086). Solo marca carteles cuyo `proveedor` FK ya fue poblado (i.e. guardados alguna vez desde el editor — 68/200 tienen `proveedor_id NULL` y nunca se marcan).

**(C) Listado de trabajo `/listar_carteles/`** (`views_old.py:1110-1195`):
- `get_context_data`: fija `muro_doble.html` + `[plantilla_formulario.html, tabla_listado_carteles_prueva.html]`; arma `MyForm` sobre modelo `Carteles` con campos `[proveedor, revisar]` (GET → `/listar_carteles/`); **efecto lateral en GET: `CartelesCajon.objects.get_or_create(id=cajon.id)` para cada uno de los 39 cajones**.
- `get`: anota `Cajon` con `Exists(Item.filter(cajon=OuterRef, carteles__revisar=True))` → **siempre** filtra `tiene_item_para_revisar=True` (el checkbox `revisar` del form solo afecta `items_sin_cajon`, no los cajones). Con `proveedor` agrega `item__proveedor=proveedor`. Cada cajón carga **todos** sus items (`Item.objects.filter(cajon=cajon)`), no solo los marcados. `items_sin_cajon` = `Item(tiene_cartel=True, cajon=None, carteles__revisar=filtro)` — inner join: items sin fila `Carteles` no aparecen.
- Template `tabla_listado_carteles_prueva.html`: fila por cajón (click expande `.child`), link cajón → `/x_cartel/imprimir_cajon/<cajon.id>`, link ítem → `/x_cartel/imprimir/<item.id>`; cada fila de ítem trae input texto + checkbox para **cartelito** que al cargar dispara `GET /x_cartel/cartelito/?item_id=` **por cada input** (N+1) y POSTea al tipear Enter / togglear.

**(D) Editor + impresión de cartel individual** `/x_cartel/imprimir/<item_id>` (`x_cartel/views.py:17-142`, `Cartel`, template `x_cartel/templates/x_cartel/prueba_edicion.html`):
- GET: `Carteles.objects.get_or_create(id=item_id)` — crea la fila con pk = id del ítem (FK `item`/`proveedor` quedan NULL hasta el primer POST). Renderiza formulario con 5 pares textarea+tamaño (`descripcion`, `texto_final` "Precio de lista", `final`, `texto_final_efectivo`, `final_efectivo` "$ Contado Efectivo") + checkbox `revisar` + preview `#cartel` (div 20.95×29.6 cm, Anton).
- JS: `inicializarSpan`/`agregarListeners` copian texto y `font-size` a los spans en vivo. `actualizarTextoArticulo` pide `GET /precios_articulos/<id>` (o `/precios_articulos_cajon/<cajon_id>`) → reemplaza placeholders **`[[ dato.final ]]`, `[[ dato.final_efectivo ]]`, `[[ dato.final_rollo ]]`, `[[ dato.final_rollo_efectivo ]]`** (ítem) o **`[[ dato_N.* ]]`** (cajón) dentro del texto guardado, aplicando `custom_price()` — réplica JS del modo cartel de `utils/rounding.round_price` (>1000 → 500; ≥10000 y múltiplo de 1000 → −100). En DB hoy: 15 carteles con placeholder en `final_efectivo`, 24 `CartelesCajon` con `[[ dato_N.* ]]`.
- POST: persiste los 5 textos + tamaños + `cartel.item=item`, `cartel.proveedor=item.proveedor`. `revisar` se lee pero **no se guarda para ítem individual** (solo rama cajón lo usa).
- **Imprimir**: `imprimir()` abre `window.open`, escribe el `outerHTML` de `#cartel` + Anton + Bootstrap CDN y llama `ventana.print()` — impresión 100% client-side, sin PDF ni Drive.

**(E) Cartel por cajón** `/x_cartel/imprimir_cajon/<cajon_id>`: mismo `Cartel`; `get_or_create(id=cajon_id)` sobre `CartelesCajon`; `hay_descripciones` lista los `Item` del cajón como títulos; POST con `revisar="true"` marca el `CartelesCajon` y propaga `revisar=True` creando `Carteles(id=item.id)` por cada ítem del cajón (con cualquier otro valor presente los desmarca; checkbox ausente = sin cambio). Los `[[ dato_N.* ]]` se resuelven por posición contra `Item.objects.filter(cajon=cajon_id)`.

**(F) Cartelitos**: desde `/listar_carteles/` (inputs por fila) → `POST /x_cartel/cartelito/` (`CrearCartelitoView`): primer POST crea la fila con `habilitado=False` (no togglea en `created`), segundo POST togglea. Impresión en `/x_cartel/imprimir_cartelitos/` → `Cartelito` → `cartelitos_x6.html` (grilla 2 col × 105×99 mm; muestra `final_efectivo`, `final` si difiere, `final_rollo` si >0) → el usuario imprime con el browser (no hay botón).

**(G) Batch x6 por sub_carpeta/sub_titulo**: `/imprimir/` (form `MyForm` con `sub_carpeta`, `sub_titulo`, action `tabla/` POST) → `/imprimir/tabla/` filtra `Item.objects.filter(**form_data)` → `static/templates/imprimir_carteles_x6.html` (grilla 6/hoja sobre `datos` dicts). `generic_template.html` oculta navbar/carrito cuando `ruta_actual == '/imprimir/tabla/'`. Sin botón imprimir — Ctrl+P.

### 4. Doble/triple redondeo del precio impreso

`final` ya viene redondeado por el pipeline (CSV `is_cartel=False`; si `factor_division>1` se re-redondea con `is_cartel=tiene_cartel`); el editor lo vuelve a pasar por `custom_price()` (modo cartel) → el precio impreso es `round_cartel(round_no_cartel(precio))` — a propósito o no, es el comportamiento vigente.

### 5. Quirks, dead code y duplicación (verificado)

- **Vistas duplicadas**: `views_old.ListarCarteles/Imprimir/ItemsView` son las cableadas; las versiones refactor de `views/main.py` (con logging, prefetch, `campos_tabla`) son dead code salvo que un registro `Armador` las invoque — hoy ninguno (`bdd_armador` solo referencia Inicio/Actualizar/ListadoPedidos).
- **`Carteles.id == Item.id` por convención**, no por FK: `get_or_create(id=item_id)`; `item_id` NULL en 48/200, `proveedor_id` NULL en 68/200 → `marcar_revisar_carteles` no los alcanza.
- **`revisar` jamás se limpia en ítem individual** (checkbox del editor es no-op en esa rama) → el cartel queda "a revisar" hasta que su cajón lo propague en False. Los cajones en `/listar_carteles/` siempre filtran `revisar=True` aunque el form diga lo contrario.
- `item.cartelito` en el template **nunca resuelve** (el accessor real del OneToOne es `cartelitos`) → inputs vacíos server-side que el JS rellena vía AJAX (N+1 requests por página).
- `POST /x_cartel/` sin kwargs → `UnboundLocalError` (500). `precios_articulos*` no verifican método. `print()` de debug en `Cartelito` y `Cartel`.
- `tamano_*` vacío → `0` en vez de default. `Cartel.get_context_data` recibe `request` como primer arg posicional (firma no estándar, funciona porque se llama a mano).
- Templates muertos: `x_cartel/cartel.html` (URL `PruebaEdicion` comentada), `static/templates/imprimir_tabla.html`, `static/templates/tabla_listado_carteles.html`. Bug visible: `imprimir_carteles_x6.html:9` tiene `{{ dato.descripcion }}}` (llave extra → `}` literal impreso).
- Config Armador vestigial en DB: `Contenedor` id=5 `imprimir-tabla`, id=10 `contenedor_listar_carteles`, `Plantilla` 9/12 — sin efecto (las vistas hardcodean muro/plantillas).
- Duplicación de grillas x6: `static/templates/imprimir_carteles_x6.html` (dicts `datos`) vs `x_cartel/templates/x_cartel/cartelitos_x6.html` (objetos `Cartelitos`).

## Affected Areas

- `x_cartel/models.py` — 3 modelos del dominio cartel (`Cartelitos` sin admin).
- `x_cartel/views.py` — `Cartel` (editor A4 ítem/cajón), `Cartelito`, `CrearCartelitoView`, `precios_articulos`, `precios_articulos_cajon`.
- `x_cartel/urls.py` — 7 rutas (una comentada).
- `x_cartel/templates/x_cartel/{prueba_edicion,cartelitos_x6,cartel}.html` — editor con JS de placeholders + print client-side; `cartel.html` muerto.
- `bdd/views_old.py` — `ListarCarteles` (1110-1195), `Imprimir` (610-701), `ItemsView` (586-604): las versiones activas.
- `bdd/views/main.py` — duplicados refactorizados (dead, 128-324, 456-631).
- `bdd/urls.py:5,23,76,107-110` — wiring a `views_old`.
- `bdd/models.py` — `Item` (`tiene_cartel` l.284, `tipo_cartel` 287, `p_c_*` 292-298, `sub_carpeta` 254, `sub_titulo` 259, `recompute_finales` 355), `Cajon`, `Sub_Carpeta`/`Sub_Titulo`/`Tipo_Cartel` (114-123).
- `bdd/views/ajax.py` — `editar_item` (tiene_cartel GET/POST, 386-431).
- `bdd/views/forms.py` — `MyForm` resuelve modelos en `bdd`/`x_cartel` (67-84) — usado por form de `ListarCarteles` e `Imprimir`.
- `static/templates/` — `tabla_listado_carteles_prueva.html` (lista + JS cartelitos), `imprimir_carteles_x6.html`, `muro_doble.html`, `muro_imprimir.html`, `plantilla_formulario.html`, `tabla_buscador.html` (botón Cartel + modal), `generic_template.html` (oculta navbar en `/imprimir/tabla/`).
- `actualizador/actualizador_csv.py` (882-893) y `actualizador/actualizador_main.py` (389-402, 737, 1086) — `revisar=True` post-proceso de proveedor.
- `utils/rounding.py` — `round_price(is_cartel=…)`; réplica JS `custom_price()` en `prueba_edicion.html`.
- `core_config/urls.py:32` — monta `x_cartel.urls` en raíz.
- `core_index/templates/core_index/index.html:12` — link "Carteles".
- `articulos/models.py` — `Cartel`/`ArticuloProveedor.cartel` (duplicado abandonado).

## Approaches

Exploración as-is — no se evalúan enfoques. Si un change futuro toca carteles, los candidatos naturales (del hallazgo) son: unificar el vínculo `Carteles↔Item` (FK real vs convención pk), hacer que guardar un cartel limpie `revisar`, deduplicar `views_old`↔`views/main.py`, y consolidar las dos grillas x6.

## Recommendation

Usar este documento como baseline antes de cualquier modificación. No tocar `bdd/urls.py` sin recordar que apunta a `views_old`. Cualquier change que altere `Item.*_base`/`recompute_finales`/`round_price` impacta directamente lo que se imprime.

## Risks

- **Sin autenticación** en todo el flujo de carteles (edición e impresión públicas).
- El flag `revisar` se marca masivamente desde el actualizador y **nunca se desmarca** en ítems individuales → la lista de trabajo crece con falsos pendientes.
- `Carteles.id==Item.id` por convención: colisiones o `get_or_create` con pk ajeno crean filas huérfanas (FK NULL) invisibles para `marcar_revisar_carteles`.
- Precio impreso depende de redondeo duplicado (server + JS) — cambiar `round_price` sin tocar `custom_price()` diverge cartel vs sistema.
- `listar_carteles` tiene efecto lateral en GET (crea `CartelesCajon` por cajón) y la tabla muestra todos los ítems del cajón (ruido).
- `bdd/urls.py` consulta la DB en import-time con `except: pass` — un `Armador` inválido borra rutas silenciosamente (no afecta a las rutas estáticas de carteles, pero sí al navbar).
- N+1 AJAX por página en la lista de carteles (un `GET /x_cartel/cartelito/` por input).

## Ready for Proposal

**No — exploración standalone as-is.** Es el baseline pedido antes de tocar carteles; el orquestador puede usarlo como contexto cuando el usuario pida un change concreto sobre este flujo.
