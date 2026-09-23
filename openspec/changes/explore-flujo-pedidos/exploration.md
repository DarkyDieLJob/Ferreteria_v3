# Exploration: Flujo de trabajo ACTUAL de pedidos a proveedores (as-is)

**Tipo:** exploración standalone (sin change asociado) — baseline de seguridad antes de cualquier modificación al ciclo de pedidos. **No propone cambios.**
**Fecha:** 2026-09-23 · **Rama:** `produccion`
**Fuentes:** verificación directa de todo `pedido/` (models, forms, 9 archivos de views, urls, 17 templates, 4 JS), `bdd/views/ajax.py`, `bdd/views/main.py`, `bdd/urls.py`, `static/templates/{tabla_buscador,tabla_pedidos,seleccionar_proveedor}.html`, `cajas/templates/cajas/caja_tabla_resultado.html`, `utils/queryset_to_xlsx.py`, `ejecutar_utils.py`, `pedido/README.md`, `bdd/DOCUMENTATION.md`, `.gitignore` y **consultas de solo lectura a `db.sqlite3` local** (datos de prod).

---

## Current State

### Modelos (`pedido/models.py`, 73 líneas — verificado contra migración `0001_initial` y DB)

| Modelo | Campos | Estado real en DB |
|--------|--------|-------------------|
| `Pedido` | `fecha` (auto_now_add), `proveedor` FK, `articulo_pedido` M2M→ArticuloPedido, `total` Float, `fecha_entrega` Date null, `estado` choices `Pd/En/Et/Co` default `Pd` | 59 filas: **37 `Co` + 22 `Pd`, 0 `En`, 0 `Et`**. `fecha_entrega` NULL en las 59, `total`=0 en las 59 → **ambos campos muertos** |
| `ArticuloPedido` | `proveedor` FK, `item` FK, `cantidad` Float, `llego` Bool, `fecha` Date `auto_created=True, default="2021-01-01"` | 2338 filas, **TODAS con `fecha='2021-01-01'`** → la columna Fecha de las tablas es ruido constante. `llego`: 2046 False / 292 True |
| `ArticuloDevolucion` | `fecha` auto_now_add, `proveedor` FK, `item` FK, `cantidad` Float | **0 filas** — feature implementada (~2023) sin uso en prod |
| `Vendido` | `proveedor`, `item`, `cantidad`, `umbral`, `pedido` | **0 filas, nunca importado por ninguna vista** — modelo muerto |

`admin.py` solo registra `ArticuloPedido` y `Pedido` (ni `Vendido` ni `ArticuloDevolucion`).

### Flujo end-to-end (verificado en código + JS + templates)

**0. Origen de "faltantes" (`bdd.Lista_Pedidos` — 4375 filas, 78 con `pedido=True`):**
La lista de faltantes NO nace en la app pedido; se alimenta desde `bdd`:
- **Ventas:** `agregar_articulo_a_carrito` (`bdd/views/ajax.py:505-569`) — cada ítem agregado a un carrito de venta hace `get_or_create`/`F()+cantidad` en `Lista_Pedidos` si el item tiene `proveedor`. *La demanda de ventas acumula faltantes automáticamente.*
- **Consulta en caja:** `cajas/templates/cajas/caja_tabla_resultado.html:103` — el botón "ver" (muestra precios) **silenciosamente** hace POST a `/crear_modificar_lista_pedidos/` → `+1` a `cantidad` (`bdd/views/ajax.py:161-293`). El proveedor se deduce de la abreviatura del código (`XXX/3D` → `ListaProveedores.abreviatura='/3D'` → `Proveedor.identificador`), con fallback a `item.proveedor`. También setea `item.trabajado=True` y reasigna `item.proveedor`.
- **Gestión manual:** `ListadoPedidos` (`bdd/views/main.py:329`, vista Armador, modelo `Lista_Pedidos`) renderiza `static/templates/tabla_pedidos.html` con `eliminar_articulo_pedido` (confirmar=`pedido=True`+cantidad, o borrar) y `cambiar_cantidad_pedido` (0 = borra). UI paralela vieja: `seleccionar_proveedor.html` (página suelta con modal, también usa esos endpoints).
- **Alta directa desde buscador:** botón "agregar al pedido" en `tabla_buscador.html:369` → POST `/agregar_articulo_a_pedido/<id>/` (montado en **raíz** por `bdd/urls.py:113`) → `pedido/views/externo.py`: crea `ArticuloPedido(cantidad=1)`, marca `Lista_Pedidos.pedido=True` con `cantidad-1`, y lo adjunta al `Pedido` `Pd` del proveedor (get_or_create). Si el item no tiene proveedor → 400 `missing_proveedor` y el front abre el modal de edición de item. La tabla del buscador muestra `tiene_pedido` (anotación `Exists(Lista_Pedidos)` en `bdd/views/base.py:479`).

**1. Crear pedido:** `GET /pedidos/home/` (`HomeView`) — tabla por proveedor con columnas Nuevo Pedido / Pendiente / Enviado / Entregado / Faltantes (`pedidos_activos = proveedor.pedido_set.exclude(estado="Et")` — N+1 por proveedor; como `Et` nunca se usa, trae también los `Co`, que no se muestran en ninguna columna). `GET /pedidos/nuevo_pedido/<proveedor_id>` → `get_or_create(proveedor, estado="Pd")` → redirect a editar. **Invariante: a lo sumo UN `Pd` por proveedor** (mismo get_or_create usado por `nuevo_pedido`, `externo.agregar_al_pedido` y `controlar.post`).

**2. Editar pedido:** `/pedidos/editar_pedido/<pedido_id>` o `editar_pedido_por_proveedor/<proveedor_id>` (`EditarPedidoView`). Pantalla: form `ArticuloPedidoForm` (Select2 autocomplete vía `ItemAutocomplete`), tabla "Artículos en el pedido" (cantidad editable + cancelar), tabla "Artículos faltantes" (input "cuánto pedir" + botón). Acciones AJAX (todas POST JSON, CSRF por header):
- POST del form → crea `ArticuloPedido` + `Lista_Pedidos.pedido=True` + `pedido.articulo_pedido.add()`. Si `url_destino=controlar_pedido` (hidden input en el form de controlar) redirige allí.
- `/pedidos/agregar_al_pedido/` (`editar.agregar_al_pedido`) — crea artículo desde faltante, **resta la cantidad pedida de `Lista_Pedidos.cantidad`**, marca `pedido=True`. Devuelve el artículo serializado para insertar la fila sin reload.
- `/pedidos/actualizar_cantidad/<id>` — ajusta `ArticuloPedido.cantidad` y compensa la diferencia en `Lista_Pedidos.cantidad` (acepta coma decimal).
- `/pedidos/cancelar_articulo_pedido/` — quita del M2M, `pedido=False`, **devuelve** cantidad a `Lista_Pedidos.cantidad`.
- **Quirk:** si `pedido` es `None` (editar por proveedor sin Pd), `{{ pedido.id }}` renderiza vacío → `var pedidoId = ;` = SyntaxError JS.

**3. Enviar:** botón "Enviar pedido" → POST `/pedidos/enviar_pedido/` → `estado="En"` (rechaza pedido vacío). **No hay envío real**: ni email, ni Drive, ni WhatsApp — el artefacto es `GET /pedidos/pedido/<id>/pdf/` (`pdf.py`, reportlab: título proveedor + fecha + tabla Ítem/Cantidad). El usuario descarga el PDF y lo manda por fuera del sistema. Desde `detalle_pedido` (única pantalla para `En`) hay botones "Controlar Pedido" y "Descargar PDF".

**4. Recepción/control:** `/pedidos/controlar_pedido/<pedido_id>` (`ControlarPedidoView`). Cada fila: input cantidad + checkbox "Llegó?" (checked por default) + checkbox "Devolver?".
- Click en "Llegó?" → `agregarAlStock()` → POST `/pedidos/agregar_al_stock/` → `item.stock += articulo_pedido.cantidad`, `articulo_pedido.cantidad=0`, `llego=<checkbox>`, y `Lista_Pedidos.cantidad -= 1` (**siempre 1, no la cantidad real**). La cantidad editada en el input **se ignora** — el view usa el valor de DB. La fila se remueve del DOM.
- Click en "Devolver?" → POST `/pedidos/agregar_devolucion/` → quita del pedido M2M, `Lista_Pedidos.pedido=False`, crea `ArticuloDevolucion` con la cantidad del pedido, `articulo_pedido.cantidad=0`. **No toca stock.**
- Botón "Pedido Controlado" → POST `/pedidos/marcar_controlado/` → `post()`: `estado="Co"` y los artículos con `llego=False` se migran (`pedido.articulo_pedido.add(*)`) al `Pd` del mismo proveedor (get_or_create) → rollover automático de no-recibidos al próximo pedido.

**5. Faltantes:** `/pedidos/listar_faltantes/<proveedor_id>` — tabla read-only de `Lista_Pedidos` por proveedor (la edición real ocurre en editar_pedido o en las UIs de bdd).

**6. Devoluciones:** `/pedidos/listar_devoluciones/` — lista `ArticuloDevolucion`; checkbox "Ya se devolvió" → POST `/pedidos/eliminar_devolucion/` (mapea a `ListarDevolucionesView.post` → `delete()`). PDFs: `/pedidos/devoluciones/pdf/` (global, filtros `fecha_desde/fecha_hasta/proveedor_id/q`) y `/pedidos/devoluciones/<proveedor_id>/pdf/` — ambos exigen `is_authenticated` (401 si no). **En prod: 0 devoluciones.**

**7. Exportes XLSX:** `ejecutar_utils.py` (raíz, 4 líneas) → `utils/queryset_to_xlsx.ejecutar()` — script **manual** (sin cron/Celery/cola; nada lo invoca). Genera `media/pedidos/pedidos.xlsx` (dump de `Lista_Pedidos`), `articulos_vendidos.xlsx` (agregado mensual de `facturacion.ArticuloVendido`) y un `<Proveedor.text_display>.xlsx` por proveedor — exactamente los archivos gitignored de `.gitignore:58-81`. El side-effect `arrancar_django_config()` al importar el módulo ya estaba documentado.

### Estados reales del ciclo
`Pd → En → Co`. `Et` (Entregado) **nunca se asigna** — solo aparece en `exclude(estado="Et")` (home.py:19, editar.py:35,89), lo que vuelve ese filtro un no-op. `En` tampoco persiste en la DB actual (los enviados terminan `Co`), pero `enviar_pedido` sí lo escribe. No hay transición "revertir".

### Permisos / roles
**Prácticamente nulos.** Ninguna vista de `pedido` usa `@login_required`/decoradores; no hay `LoginRequiredMiddleware` en settings. Solo chequeos puntuales: `ItemAutocomplete` (devuelve queryset vacío anónimo), `descargar_devoluciones_pdf` y `..._por_proveedor_pdf` (401), y `nav_bar.html` muestra login/logout. Todos los endpoints mutadores (`agregar_al_stock`, `enviar_pedido`, `agregar_devolucion`, `actualizar_cantidad`, `nuevo_pedido`, `eliminar_devolucion`) **son alcanzables sin autenticación** y modifican `Item.stock`, `Pedido`, `Lista_Pedidos`. CSRF sí aplica (middleware default; el JS manda `X-CSRFToken`).

### Integraciones
- `bdd`: `Item` (stock, trabajado, proveedor), `Proveedor`/`ListaProveedores` (abreviatura `XXX/AB`), `Lista_Pedidos` (faltantes — corazón compartido entre ventas y pedidos), `NavBar` (la DB tiene `pedidos/home/|"Pedidos"` → entrada en el menú dinámico principal).
- `facturacion`: solo lectura agregada de `ArticuloVendido` en el export xlsx.
- Drive/Gmail/Patoba: **cero integración** en pedidos (el envío es manual vía PDF descargado).
- Front: `base_pedido.html` con Bootstrap local + jQuery local + Select2 local (`vendor/`), Quagga lazy-load. `dal_select2` para el autocomplete. `crispy_forms` para el form.

### Divergencias README vs código real
`pedido/README.md` es bueno pero quedó viejo en:
- §11: dice que `ItemAutocomplete` filtra `codigo__endswith` por abreviatura → en realidad filtra `proveedor_id` param + `codigo__icontains OR descripcion__icontains` (`base.py:44-55`).
- §7: "jQuery local y CDN" → solo local; Select2 también local (no CDN).
- §9: `static/css/pedido.css` "(a crear)" → ya existe (`pedido/static/css/pedido.css`, 95 líneas).
- §4: lista 7 archivos de vistas; hay **9** (`pdf.py`, `pdf_devoluciones.py`, `externo.py` no mencionados) — y las devoluciones tienen PDFs con auth check que el README no documenta.

### Código muerto / quirks confirmados
1. `Vendido` — modelo sin uso (0 filas, sin imports, sin admin).
2. `ArticuloPedido.fecha` — `auto_created=True`+default ⇒ **todas las filas = 2021-01-01** (2338/2338 en DB). Columna Fecha inútil en 3 templates.
3. `Pedido.total` y `fecha_entrega` — jamás escritos (59/59 en 0/NULL); `fecha_entrega` solo se lee en pdf.py y home.
4. `estado="Et"` — inalcanzable desde UI; columna "Entregado" del home siempre vacía.
5. `urls.py`: nombre `actualizar-cantidad` duplicado (líneas 43 y 94) **y** shadowing de import — `devoluciones.actualizar_cantidad` (línea 5) queda tapada por `editar.actualizar_cantidad` (línea 6) → ambas rutas resuelven a la de editar; la de devoluciones es **dead code**.
6. `/pedidos/actualizar_llego/` + `actualizarLlego()` en `editar_pedido.js` — **dead code**: `controlar_pedido.js` usa `agregarAlStock` al clickear el checkbox; nadie llama al endpoint (que además decrementa `Lista_Pedidos` en 1 fijo y fuerza `pedido=False`).
7. `marcar_controlado` GET → `TypeError` (su `get()` exige `pedido_id`); `eliminar_devolucion` GET → renderiza la lista de devoluciones. Ambas URLs son "acciones" disfrazadas de CBV.
8. `agregar_al_stock` decrementa `Lista_Pedidos.cantidad` en `1` fijo e ignora la cantidad del input del usuario.
9. `barra_de_navegacion` hardcodeada en `GeneralPedidoView` incluye "Sección 2" con links muertos (`subseccion21/22`) — placeholder visible en prod.
10. `ArticuloPedido` puede quedar huérfano: `cancelar_articulo_pedido`/`agregar_devolucion` lo sacan del M2M pero no lo borran (cantidad=0 en devolución); `detalle` lista `pedido.articulo_pedido` (M2M) mientras `controlar`/`editar` filtran por `pedido=pedido_id` (reverse FK implícito `articulopedido_set`... **inconsistente**: `ArticuloPedido.objects.filter(pedido=...)` usa la relación M2M inversa, no un FK — funciona pero es frágil de leer).
11. Home hace N+1 (`proveedor.pedido_set` por proveedor) y carga `Co` invisibles.
12. `views/__init__.py` vacío (urls importan submódulos directo); `tests.py` = stub de 3 líneas; **cero tests de pedido** en `tests/`.
13. `apps.py`/`admin.py` triviales; migración única `0001_initial` generada con Django 5.2.1 (proyecto corre 4.0.6 — compatible pero anómalo).

## Affected Areas
- `pedido/` — app completa (models/forms/urls/views×9/templates×17/static js+css).
- `bdd/views/ajax.py` — `crear_modificar_lista_pedidos`, `cambiar_cantidad_pedido`, `eliminar_articulo_pedido`, `agregar_articulo_a_carrito` (escribe `Lista_Pedidos` en cada venta).
- `bdd/urls.py:29,113` — monta `pedido.views.externo.agregar_al_pedido` en raíz `/agregar_articulo_a_pedido/`.
- `bdd/views/main.py` `ListadoPedidos` + `static/templates/tabla_pedidos.html`, `seleccionar_proveedor.html`, `tabla_buscador.html` — UIs paralelas del mismo `Lista_Pedidos`.
- `cajas/templates/cajas/caja_tabla_resultado.html:103` — efecto colateral oculto (ver precio ⇒ suma faltante).
- `utils/queryset_to_xlsx.py:141-170` + `ejecutar_utils.py` — exportes manuales a `media/pedidos/`.
- `bdd/models.py` `Lista_Pedidos` (391), `Proveedor`/`ListaProveedores` (33-70), `Item.proveedor/stock/trabajado`.

## Approaches
N/A — documentación as-is. Si un change futuro toca pedidos, los candidatos naturales son: (a) unificar las 4 UIs que pisan `Lista_Pedidos`; (b) proteger endpoints mutadores con auth; (c) corregir el -1 fijo y la cantidad ignorada en `agregar_al_stock`; (d) decidir el destino de `Et`/`total`/`fecha_entrega`/`Vendido`/devoluciones (usar o borrar). Cada uno tiene blast-radius en `bdd` y en JS legacy.

## Recommendation
Usar este documento como contrato as-is antes de tocar `pedido/` o `Lista_Pedidos`. La lectura clave: **`Lista_Pedidos` es el estado compartido entre ventas (bdd) y compras (pedido)** — `cantidad` significa "demanda acumulada neta" y `pedido=True` significa "ya incluido en un pedido Pd". Cualquier refactor debe preservar ese contrato implícito o migrarlo explícitamente.

## Risks
- Mutación de `Item.stock` y `Lista_Pedidos` desde endpoints sin auth ni transacción — condiciones de carrera reales (el JS ya tuvo que agregar debounce/busy-flags por duplicados en Chrome).
- El "faltante" se descuenta en lugares dispersos (`agregar_al_pedido`, `cancelar_articulo_pedido`, `agregar_al_stock`, `actualizar_llego` muerto) con aritmética inconsistente → deriva de cantidades acumulada en prod.
- Artículos `llego=False` migra(ñ|n)do al próximo `Pd` al controlar: si ese `Pd` ya fue "enviado" (raro pero posible vía admin), se re-envían sin control.
- DB de prod convive en el working dir (`db.sqlite3`) — los números de esta exploración son del negocio real.

## Ready for Proposal
**No — exploración standalone as-is.** Sin propuesta de cambio. Cuando se decida tocar pedidos: lanzar `sdd-propose` con alcance acotado (ej. hardening de endpoints, o fix del control de recepción) usando este documento + `explore-arquitectura-monolito` como contexto.
