# Apps de Negocio - Documentación Exhaustiva

**Versión documentada:** v3.10.0
**Fecha:** 2026-07-13

---

## Índice

1. [facturacion](#1-facturacion)
2. [boletas](#2-boletas)
3. [cajas](#3-cajas)

---

## 1. facturacion

### 1.1 Propósito

`facturacion` gestiona:
- El procesamiento de transacciones de venta (carrito → transacción → impresión fiscal)
- El CRUD completo de clientes
- La generación de tickets fiscales (JSON para websocket a impresora Hasar/Epson)
- Los cierres Z (reporte fiscal diario)
- Las vistas de facturación diaria y mensual
- La comunicación WebSocket con la impresora fiscal (fiscalberry)

### 1.2 Estructura

```
facturacion/
├── __init__.py
├── admin.py
├── apps.py
├── models.py              (202 líneas)  - 5 modelos
├── views.py               (962 líneas)  - Vistas principales + endpoints AJAX
├── views_clientes.py      (292 líneas)  - CRUD de clientes
├── forms.py               (66 líneas)   - ClienteForm, ClienteQuickForm, ClienteFilterForm
├── funtions.py            (360 líneas)  - Lógica de negocio: registrar_articulos_vendidos
├── classes.py             (848 líneas)  - TicketFactura, ComandoFiscal, FormasPago, etc.
├── cliente.py             (122 líneas)  - conectar_a_websocket (cliente WebSocket)
├── servidor_fake_ws.py    (127 líneas)  - Servidor WebSocket de prueba
├── urls.py                (98 líneas)   - 17 URLs
├── notebook/
│   └── procesador_de_informes.py
└── templates/facturacion/
    ├── facturacion.html           (83 líneas)  - Facturación diaria
    ├── facturacion_mensual.html   (26 líneas)  - Facturación mensual
    ├── cierre_z.html              (44 líneas)  - Vista de cierres Z
    ├── add_client.html            (31 líneas)  - Formulario alta cliente (legacy)
    ├── cliente_form_page.html     (35 líneas)  - Formulario alta/edición cliente
    ├── clientes_list.html         (256 líneas) - Listado de clientes con filtros
    └── partials/
        ├── cliente_form.html      (22 líneas)  - Fragmento form para modal AJAX
        └── cliente_delete.html    (40 líneas)  - Fragmento eliminación con reasignación
```

### 1.3 Modelos (`models.py`)

#### `Cliente`
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `razon_social` | CharField(45) | Nombre/razón social |
| `cuit_dni` | CharField(11) | CUIT o DNI |
| `responsabilidad_iva` | CharField(1) | Choices: I, E, A, C, B, M, S, V, W, T |
| `tipo_documento` | CharField(1) | Choices: C(CUIT), 0-4, " "(sin calificador) |
| `domicilio` | CharField(45) | null |
| `telefono` | CharField(45) | null |

**Métodos:**
- `get_responsabilidad()` → nombre largo (ej: "RESPONSABLE_INSCRIPTO")
- `get_tipo_documento()` → nombre largo (ej: "CUIT", "Documento Nacional de Identidad")

**Mapeos internos:**
- `RESPONSABILIDAD_A_NOMBRE`: dict código → nombre AFIP
- `TIPO_DOCUMENTO_A_NOMBRE`: dict código → nombre descriptivo

#### `ArticuloVendido`
Registro de un artículo vendido en una transacción:
- `item` - FK→`bdd.Item` (null, si es registrado)
- `sin_registrar` - FK→`bdd.ArticuloSinRegistro` (null, si no está en inventario)
- `cantidad` - FloatField

**Métodos:**
- `get_item()` → `{ds, importe, importe_efectivo, qty}` para ticket fiscal
  - Si `item`: usa `item.descripcion`, `item.final`, `item.final_efectivo`
  - Si `sin_registrar`: usa `sin_registrar.descripcion`, `sin_registrar.precio`

#### `MetodoPago`
- `display` - CharField(250) (ej: "Efectivo con ticket", "Efectivo s/ticket", "Cuenta Corriente")
- `ticket` - BooleanField (si genera ticket fiscal)

#### `Transaccion`
- `cliente` - FK→`Cliente` (default=1, Consumidor Final)
- `usuario` - FK→`auth.User`
- `articulos_vendidos` - M2M→`ArticuloVendido`
- `metodo_de_pago` - FK→`MetodoPago`
- `fecha` - DateTimeField (auto_now_add)
- `total` - FloatField
- `tipo_cbte` - CharField(3) (ej: "FB", "FA", "TB")
- `numero_cbte` - IntegerField (número de comprobante impreso)

**Métodos:**
- `get_cliente_id()` → `self.cliente.id`

#### `CierreZ`
Réplica de los datos del cierre fiscal Z de la impresora (30+ campos):
- `fecha` - DateField (auto_now_add)
- `zeta_numero` - IntegerField (número de Z)
- `cant_doc_fiscales`, `cant_doc_fiscales_a_emitidos`, `cant_doc_fiscales_bc_emitidos`
- `monto_ventas_doc_fiscal`, `monto_iva_doc_fiscal`, `monto_percepciones`
- `ultimo_doc_a`, `ultimo_doc_b`, `ultima_nc_a`, `ultima_nc_b`
- `status_fiscal`, `status_impresora` (hexadecimal)
- etc.

### 1.4 URLs (`urls.py`)

| URL | Vista | Nombre | Descripción |
|-----|-------|--------|-------------|
| `obtener_metodos_pago/` | `obtener_metodos_pago` | - | GET: lista de métodos de pago |
| `obtener_cliente/` | `obtener_cliente` | - | GET: lista de clientes |
| `procesar_transaccion/` | `procesar_transaccion` | - | POST: procesa venta + impresión fiscal |
| `agregar_articulo_sin_registro/` | `agregar_articulo_sin_registro` | - | POST: agrega item no registrado al carrito |
| `eliminar_articulo/` | `eliminar_articulo` | - | POST: elimina item del carrito |
| `eliminar_articulo_sin_registro/` | `eliminar_articulo_sin_registro` | - | POST: elimina item sin registro |
| `actualizar_cantidad_articulo/` | `actualizar_cantidad_articulo` | - | POST: actualiza cantidad |
| `actualizar_cantidad_articulo_sin_registro/` | `actualizar_cantidad_articulo_sin_registro` | - | POST: actualiza cantidad sin registro |
| `vista_cierre_z/` | `CierreZVieW` | `cierres-fiscales` | Vista de cierres Z |
| `facturacion/clientes/` | `ClientesListView` | `clientes-list` | Listado de clientes |
| `facturacion/clientes/nuevo/` | `ClienteNuevoView` | `clientes-nuevo` | Alta de cliente |
| `facturacion/clientes/editar/<id>/` | `ClienteEditarView` | `clientes-editar` | Edición de cliente |
| `facturacion/clientes/eliminar/<id>/` | `ClienteEliminarView` | `clientes-eliminar` | Eliminación de cliente |
| `facturacion/clientes/api/crear/` | `api_crear_cliente` | `clientes-api-crear` | API JSON alta rápida |
| `facturacion/clientes/legacy/` | `Clientes` | `clientes` | Alias legado |
| `facturacion/` | `Facturacion` | `facturacion` | Facturación diaria |
| `facturacion/mensual/` | `FacturacionMensual` | `facturacion-mensual` | Facturación mensual |
| `facturacion/<year>/<month>/<day>/` | `Facturacion` | `facturacion_fecha` | Facturación por fecha |
| `consulta_impresora_generica/` | `consulta_impresora_fiscal_generica` | - | GET: consulta config impresora |

### 1.5 Vistas (`views.py`)

#### Endpoints AJAX

**`obtener_metodos_pago(request)`**
- GET → JSON: `[{id, display}]`

**`obtener_cliente(request)`**
- GET → JSON: `{clientes: [{id, razon_social, cuit_dni, domicilio, telefono}]}`

**`procesar_transaccion(request)`** (POST, @csrf_exempt)
Flujo completo de venta:
1. Extrae datos del POST (usuario, carrito_id, cliente_id, total, total_efectivo, metodo_de_pago)
2. Llama `registrar_articulos_vendidos()` que:
   - Obtiene usuario, método de pago y carrito
   - Determina monto abonado (efectivo o normal según método)
   - Crea `Transaccion`
   - Valida carrito no vacío, cantidades y precios > 0
   - Crea `ArticuloVendido` por cada item y los asocia
   - Si método ≠ 1 y hay cliente: genera JSON del ticket con `TicketFactura`
3. Por cada boleta en el JSON: envía via WebSocket a la impresora fiscal
4. Extrae número y tipo de comprobante de la respuesta
5. Limpia el carrito (elimina articulos)
6. Actualiza `Transaccion` con tipo_cbte y numero_cbte

**`agregar_articulo_sin_registro(request)`** (POST, @csrf_exempt)
- Agrega item no registrado al carrito
- Maneja descripciones duplicadas (agrega sufijo numérico)
- Acepta coma decimal en cantidad y precio

**`eliminar_articulo(request)`** (POST, @csrf_exempt)
- Elimina item registrado del carrito
- Actualiza `Lista_Pedidos` restando cantidad

**`actualizar_cantidad_articulo(request)`** (POST, @csrf_exempt)
- Actualiza cantidad de item registrado
- Actualiza `Lista_Pedidos` por diferencia

**`eliminar_articulo_sin_registro(request)`** / **`actualizar_cantidad_articulo_sin_registro(request)`**
- Equivalentes para items sin registro (sin afectar Lista_Pedidos)

#### Vistas de template

**`Facturacion(TemplateView)`**
- Template: `facturacion/facturacion.html`
- Muestra transacciones del día (o fecha específica via URL)
- Agrega totales por método de pago
- URL: `facturacion/<year>/<month>/<day>/` o `facturacion/`

**`FacturacionMensual(TemplateView)`**
- Template: `facturacion/facturacion_mensual.html`
- Agrupa transacciones por fecha (año → mes → día) usando `agrupar_transacciones_por_fecha()`

**`CierreZVieW(TemplateView)`**
- Template: `facturacion/cierre_z.html`
- GET: lista cierres Z ordenados por fecha descendente
- POST: envía comando `dailyClose: "Z"` via WebSocket, parsea respuesta, crea `CierreZ`, ejecuta cola de tareas del actualizador

**`Clientes(TemplateView)`** (legacy)
- Template: `facturacion/add_client.html`
- GET: muestra formulario `ClienteForm`
- POST: guarda cliente, redirige a `/buscador/`
- Reemplazada por `ClienteNuevoView` en `views_clientes.py`

**`consulta_impresora_fiscal_generica(request)`**
- GET: envía comando `getConfigurationData` via WebSocket
- Intenta parsear respuesta como JSON, luego como Python literal
- Devuelve JSON

### 1.6 Vistas de clientes (`views_clientes.py`)

**`ClientesListView(TemplateView)`**
- Template: `facturacion/clientes_list.html`
- Filtros: razón social, CUIT/DNI, responsabilidad IVA, tipo documento
- Paginación (default 25, configurable via `page_size`, max 200)
- Preserva querystring en paginación

**`ClienteNuevoView(TemplateView)`**
- Template: `facturacion/cliente_form_page.html`
- GET: formulario vacío
- POST: guarda, redirige a listado

**`ClienteEditarView(TemplateView)`**
- Template: `facturacion/cliente_form_page.html` (o partial si AJAX)
- GET: formulario con datos del cliente. Si AJAX → devuelve partial `cliente_form.html`
- POST: actualiza. Si AJAX → JSON `{ok, cliente}` o `{ok: false, html}` con errores

**`ClienteEliminarView(TemplateView)`**
- Template: `facturacion/partials/cliente_delete.html`
- GET: muestra confirmación con count de transacciones y selector de destino
- POST: reasigna transacciones a cliente destino, elimina cliente
  - No permite eliminar Consumidor Final (ID=1)
  - No permite eliminar al mismo destino
  - Usa `db_transaction.atomic()`

**`api_crear_cliente(request)`** (POST)
- Acepta JSON o form-data
- Usa `ClienteQuickForm`
- Devuelve JSON `{ok: true, cliente: {...}}` o `{ok: false, errors: {...}}`

### 1.7 Formularios (`forms.py`)

**`ClienteForm(ModelForm)`** - Alta/edición completa
- Campos: `__all__`
- Widgets Bootstrap: TextInput, Select

**`ClienteQuickForm(ModelForm)`** - Alta rápida desde buscador
- Campos: `__all__`
- Mismos widgets

**`ClienteFilterForm(Form)`** - Filtros del listado
- `q`: razón social (icontains)
- `cuit`: CUIT/DNI (icontains)
- `iva`: responsabilidad IVA (choice)
- `tdoc`: tipo documento (choice)

### 1.8 Lógica de negocio (`funtions.py`)

**`registrar_articulos_vendidos(request_dict)`** (@transaction.atomic)
1. Obtiene usuario, método de pago y carrito
2. Determina monto abonado (efectivo si método es "efectivo con ticket" o "efectivo s/ticket")
3. Crea `Transaccion`
4. Valida carrito no vacío, cantidades > 0, precios > 0
5. Crea `ArticuloVendido` por cada item (registrado o sin registro)
6. Asocia todos a la transacción
7. Si método ≠ 1 y hay cliente: crea `TicketFactura` y genera JSON
8. Devuelve `{json, articulos, articulos_sin_registro, transaccion}`

**`cliente_to_dict(cliente)`** → `{id, razon_social, cuit_dni, domicilio, telefono}`

**`request_on_procesar_transaccion_to_dict(request)`** → extrae datos del POST

**`ciclo(fiscal)`** / **`ciclo_desborde(fiscal)`** - Ejecutan ciclos de comandos fiscales (legacy, para `ComandoFiscal`)

### 1.9 Clases fiscales (`classes.py`)

#### `TicketFactura` (sistema nuevo, JSON)
Orquesta la generación del JSON del ticket fiscal:
- `__init__(transaccion)`: crea `FormasPago`, `TicketCabecera`, lista de `TicketItem`
- Determina si necesita desborde (split) si total > límite (999999999)
- `get_ticket_json()` → lista de JSONs, uno por ticket (si hay split)
- Cada JSON tiene: `printTicket` (cabecera + items + formasPago) + `printerName`

#### `FormasPago`
- `ds`: nombre del método de pago
- `importe`: total de la transacción
- `get_efectivo()`: True si ds es "efectivo con ticket" o "efectivo s/ticket"
- `get_formas_pago_json(cant)`: divide importe si hay split

#### `TicketCabecera`
- Determina tipo de comprobante (FA para Responsable Inscripto, FB para resto)
- Datos del cliente (nro_doc, domicilio, nombre, tipo_responsable)
- Si no hay cliente o es ID 1: Consumidor Final por defecto
- `get_boleta_a()`: True si tipo_cbte == "FA"

#### `TicketItem`
- `alic_iva`, `importe`, `importe_efectivo`, `ds`, `qty`, `tasaAjusteInternos`
- `set_div_cant(cantidad)`: divide cantidad para split de tickets
- `get_item_json(efectivo, boleta_a)`:
  - Si efectivo: usa `importe_efectivo`
  - Si boleta_a: divide importe por 1.21 (remueve IVA)
  - Trunca descripción a 30 caracteres

#### `ComandoFiscal` (sistema legacy, comandos)
Genera secuencia de comandos para impresoras fiscales antiguas:
- Crea `Boleta` en DB con secuencia de `Comando` y `OrdenComando`
- Comandos: abrir recibo, setear cliente, imprimir items, subtotal, total, cerrar
- Soporta desborde (split) con factor de división
- `cierre_z()` / `informe_z()`: comandos standalone

### 1.10 Cliente WebSocket (`cliente.py`)

**`conectar_a_websocket(data)`** (async)
- Se conecta a `settings.IP_BEW_SOCKET` (ej: `ws://169.254.0.251:12000/ws`)
- Envía JSON, recibe respuesta
- Maneja: ConnectionClosedError, InvalidURI, ConnectionRefusedError, TimeoutError
- Devuelve dict parseado o dict de error

### 1.11 Servidor fake (`servidor_fake_ws.py`)
Servidor WebSocket de prueba para testing:
- Escucha en `0.0.0.0:12000/ws`
- Responde a cualquier mensaje con un JSON fijo de cierre Z
- Usado para testing sin impresora real

### 1.12 Templates

| Template | Líneas | Descripción |
|----------|--------|-------------|
| `facturacion.html` | 83 | Tabla de transacciones del día con totales por método de pago |
| `facturacion_mensual.html` | 26 | Transacciones agrupadas por fecha |
| `cierre_z.html` | 44 | Lista de cierres Z + botón para nuevo cierre |
| `add_client.html` | 31 | Formulario de alta legacy |
| `cliente_form_page.html` | 35 | Formulario de alta/edición (reutilizable) |
| `clientes_list.html` | 256 | Listado con filtros, paginación, botones de acción |
| `partials/cliente_form.html` | 22 | Fragmento de form para modal AJAX |
| `partials/cliente_delete.html` | 40 | Confirmación de eliminación con selector de destino |

### 1.13 Documentación existente (`readme.md`)

**ESTADO: EQUIVOCADO** - `facturacion/readme.md` (466 líneas) es la documentación del proyecto fiscalberry/printFiscal (protocolo de impresora fiscal Hasar/Epson). NO documenta la app Django.

Contenido del readme:
- Configuración de impresora fiscal (config.ini)
- Comandos: printTicket, openDrawer, dailyClose, getLastNumber
- Formatos JSON del protocolo fiscalberry
- Tipos de comprobantes, documentos, responsables
- Ejemplos de JSON para factura A, nota de crédito, remito
- Respuestas de impresora Hasar y Epson

### 1.14 Dependencias

**Internas:**
- `bdd.models`: `Carrito`, `Articulo`, `ArticuloSinRegistro`, `Item`, `Lista_Pedidos`, `NavBar`
- `boletas.models`: `Boleta`, `Comando`, `OrdenComando`
- `actualizador.task`: `agregar_tareas_en_cola` (ejecutado tras cierre Z)
- `utils.ordenar_query`: `agrupar_transacciones_por_fecha`

**Externas:**
- `websockets` (cliente WebSocket a impresora fiscal)
- `asyncio` (ejecutar cliente WebSocket sincrónico)
- `reportlab` (generación de PDF de pedidos)

**Settings:**
- `IP_BEW_SOCKET`: URI del WebSocket de la impresora fiscal

### 1.15 Bugs conocidos

- `views.py:5` - Import de `Inicio` desde `bdd.views_old` (sobrescrito en línea 6 por `views.main`)
- `consulta_impresora_fiscal_generica`: intenta `json.loads()` sobre un dict (la respuesta ya viene parseada desde `conectar_a_websocket`)
- `ComandoFiscal._total_tender` referencia `self.sub_total_calculado_para_ticket` que puede no estar definido si se llama sin ejecutar `set_articulos` primero

---

## 2. boletas

### 2.1 Propósito

`boletas` gestiona la cola de boletas fiscales pendientes de impresión. Las boletas se crean desde `facturacion.classes.ComandoFiscal` (sistema legacy de comandos) y se marcan como impresas cuando la impresora confirma.

### 2.2 Estructura

```
boletas/
├── __init__.py
├── admin.py               (8 líneas)   - Registro manual de 3 modelos
├── apps.py
├── models.py              (34 líneas)  - 3 modelos
├── views.py               (39 líneas)  - BoletasView (API JSON)
├── classes.py             (1 línea)    - Vacío
├── funtions.py            (1 línea)    - Vacío
├── urls.py                (7 líneas)   - 1 URL
└── tests.py
```

### 2.3 Modelos (`models.py`)

#### `Comando`
- `comando` - CharField(500) (string de comando fiscal, ej: `B\x1cdescripcion\x1cqty\x1cprice\x1c21.0\x1cM\x1c0\x1c0\x1cT`)

#### `Boleta`
- `comandos` - M2M→`Comando` (through=`OrdenComando`)
- `tipo` - CharField(1) ("A", "B" o "C")
- `impreso` - BooleanField (default=True)

#### `OrdenComando`
- `boleta` - FK→`Boleta`
- `comando` - FK→`Comando`
- `orden` - PositiveIntegerField (secuencia del comando dentro de la boleta)

### 2.4 URL

```python
path("boletas_pendientes/", BoletasView.as_view(), name="boletas")
```

### 2.5 Vista (`views.py`)

#### `BoletasView(View)` (@csrf_exempt)
- **GET:** Devuelve boletas con `impreso=False`
  - JSON: `{boletas: [{id_boleta, tipo, comandos: [str, str, ...]}]}`
  - Comandos ordenados por `orden`
- **POST:** Marca boleta como impresa
  - Body: `{status, id_boleta}`
  - Si status == "2": `boleta.impreso = True`, guarda

### 2.6 Integración con facturacion

1. `ComandoFiscal.__init__()` crea una `Boleta` con tipo A/B
2. `ComandoFiscal._add_comando()` crea `Comando` y `OrdenComando` asociados
3. La boleta queda pendiente (`impreso=False`)
4. `BoletasView.get()` lista boletas pendientes
5. La impresora (o software intermedio) procesa los comandos
6. `BoletasView.post()` marca como impresa

**Nota:** Este es el sistema LEGACY. El sistema actual (`TicketFactura`) usa JSON via WebSocket directo, sin pasar por `boletas`.

### 2.7 Archivos vacíos

- `classes.py` (1 línea, vacío)
- `funtions.py` (1 línea, vacío)

### 2.8 Admin

Registro manual simple:
```python
admin.site.register(Boleta)
admin.site.register(Comando)
admin.site.register(OrdenComando)
```

---

## 3. cajas

### 3.1 Propósito

`cajas` fue diseñada para gestionar cajas/registros de ventas, pero está **completamente vacía** en código Python. Solo tiene templates.

### 3.2 Estructura

```
cajas/
├── __init__.py
├── admin.py               (vacío)
├── apps.py
├── models.py              (vacío - sin modelos)
├── views.py               (3 líneas - solo import, sin vistas)
├── tests.py
└── templates/cajas/
    ├── caja_formulario.html    (85 líneas)  - Template de formulario
    └── caja_tabla_resultado.html (305 líneas) - Template de tabla con JS
```

### 3.3 Estado

- **Sin modelos** (`models.py` solo tiene imports)
- **Sin vistas** (`views.py` solo tiene `from django.shortcuts import render`)
- **Sin URLs** (no incluida en `core_config/urls.py`)
- **Sin admin** (`admin.py` vacío)

### 3.4 Templates existentes

#### `caja_formulario.html` (85 líneas)
- Réplica de `plantilla_formulario.html` con:
  - Formulario dinámico con campos del modelo
  - Botón de escaner de código de barras
  - Tabla de pagos de MercadoPago
- **No se usa** (no hay vista que lo renderice)

#### `caja_tabla_resultado.html` (305 líneas)
- Réplica de `tabla_buscador.html` con:
  - Tabla de items con botones Ver, Agregar, Editar, Cartel
  - Modal de edición (cantidad, barras, cajon, tiene_cartel)
  - Modal de carrito (cantidad, selección de usuario caja)
  - JS completo para AJAX
  - **BUG:** `data.modal_cantidad` debería ser `data.modal_stock` (campo que devuelve `editar_item`)
  - **BUG:** `usuario_caja` hace `+1` al ID (línea 285: `Number(...value) + 1`)
  - Hardcodea `esDarkydiel = (usuarioActual == 'darkydiel')` para mostrar usuarios caja
- **No se usa** (no hay vista que lo renderice)

### 3.5 Conclusión

`cajas` es una app abandonada. Los templates son copias de `static/templates/` con modificaciones que probablemente fueron experimentales. No tiene funcionalidad activa.

---

## 4. Relación entre apps de negocio

### 4.1 Flujo de venta completo

```
Usuario busca item (bdd.views.MiVista)
  → Tabla con botones Ver/Al carrito/Editar
  → Click "Al carrito" → POST /agregar_articulo_a_carrito/ (bdd.ajax)
  → Carrito se actualiza (polling cada 3 seg desde JS)

Usuario abre panel de carrito (tabla_lateral_carritos.html)
  → Selecciona cliente y método de pago
  → Click "Cerrar Transacción"
  → POST /procesar_transaccion/ (facturacion.views)
    → registrar_articulos_vendidos()
      → Crea Transaccion + ArticuloVendido
      → Genera JSON del ticket (TicketFactura)
    → Por cada boleta JSON:
      → conectar_a_websocket() → impresora fiscal
      → Recibe número de comprobante
    → Limpia carrito
    → Actualiza Transaccion con tipo_cbte y numero_cbte
```

### 4.2 Flujo de cierre Z

```
Usuario → /vista_cierre_z/ (facturacion.views.CierreZVieW)
  → POST: enviar {dailyClose: "Z"} via WebSocket
  → Impresora responde con datos del cierre
  → Crear CierreZ en DB
  → Ejecutar agregar_tareas_en_cola() (actualizador)
  → Redirigir a /vista_cierre_z/
```

### 4.3 Sistema legacy vs actual

| Aspecto | Legacy (ComandoFiscal + boletas) | Actual (TicketFactura + WebSocket) |
|---------|----------------------------------|-----------------------------------|
| Generación | `ComandoFiscal` crea `Boleta` + `Comando` en DB | `TicketFactura` genera JSON en memoria |
| Transporte | Polling: `BoletasView.get()` lista pendientes | Directo: WebSocket al instante |
| Confirmación | `BoletasView.post()` marca impreso | Respuesta del WebSocket |
| Modelos | `Boleta`, `Comando`, `OrdenComando` | Ninguno (transaccional) |
| Estado | `ComandoFiscal` aún en `classes.py` | `TicketFactura` es el usado |

### 4.4 Dependencias

```
facturacion
  ├── bdd (Carrito, Articulo, ArticuloSinRegistro, Item, Lista_Pedidos, NavBar)
  ├── boletas (Boleta, Comando, OrdenComando - solo legacy)
  ├── actualizador (agregar_tareas_en_cola - tras cierre Z)
  └── utils (agrupar_transacciones_por_fecha)

boletas
  └── (sin dependencias de otras apps)

cajas
  └── (abandonada, sin dependencias activas)
```
