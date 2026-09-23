# Apps Auxiliares - Documentación Exhaustiva

**Versión documentada:** v3.10.0
**Fecha:** 2026-07-13

---

## Índice

1. [actualizador](#1-actualizador)
2. [administracion_financiera](#2-administracion_financiera)
3. [reportes](#3-reportes)
4. [x_cartel](#4-x_cartel)
5. [x_articulos](#5-x_articulos)
6. [carga_archivo](#6-carga_archivo)
7. [utils](#7-utils)
8. [Apps vacías/abandonadas](#8-apps-vacíasabandonadas)

---

## 1. actualizador

### 1.1 Propósito

`actualizador` gestiona la descarga, procesamiento y actualización de planillas de precios de proveedores desde Google Drive/Gmail. Es el motor que mantiene el inventario actualizado.

### 1.2 Estructura

```
actualizador/
├── __init__.py
├── admin.py
├── apps.py
├── models.py              (vacío - sin modelos propios)
├── urls.py                (15 líneas)   - 4 URLs
├── views.py               (618 líneas)  - 4 vistas
├── actualizador_main.py   (808 líneas)  - Orquestador principal (descarga desde Gmail/Drive)
├── actualizador_csv.py    (1156 líneas) - Procesamiento CSV → Item
├── task.py                (398 líneas)  - Cola de tareas en hilos
├── sincronizador.py       (48 líneas)   - Backup/restore de BD en Drive
└── templates/
    ├── actualizador/
    │   └── reckup.html
    └── actualizar.html
```

### 1.3 URLs

| URL | Vista | Descripción |
|-----|-------|-------------|
| `actualizar/` | `Actualizar` | Vista principal de planillas |
| `reckup/` | `Reckup` | Descarga backup de BD desde Drive |
| `actualizar/ahora/` | `ActualizarAhora` | Dispara actualización inmediata |
| `actualizador/marcar_descargado/` | `MarcarDescargado` | AJAX: marca planilla como descargada |

### 1.4 Vistas (`views.py`)

#### `Actualizar(MiVista)` - Vista principal
Hereda de `bdd.views.base.MiVista`. Gestiona el ciclo completo de planillas:

**GET (`get_context_data`):**
1. Lista planillas no procesadas (`listo=False, descargar=False`)
2. Descarga cada archivo desde Drive, lee hojas con pandas
3. Elimina registros con error 404 (archivo no encontrado en Drive)
4. Limpia archivos antiguos (mantiene solo el más reciente por proveedor)
5. Lista planillas listas y descargables

**POST:**
- Si `actualizar_planillas != "True"`: marca planillas seleccionadas como listas, asigna proveedor y hoja
- Si `actualizar_planillas == "True"`: procesa planillas seleccionadas
  1. Busca archivo en Inbox de Drive
  2. Busca plantilla correspondiente en carpeta de Plantillas
  3. Copia hoja "Reemplazable" de la plantilla
  4. Crea copia en carpeta de Descargas
  5. Si `descargar == "True"`: genera ZIP con todos los archivos
- Borrado de planillas seleccionadas

#### `ActualizarAhora(TemplateView)`
- Programa actualización inmediata (hora actual + 1 minuto)
- Llama `agregar_tareas_en_cola()` que encola: `principal`, `principal_csv`, `buckup`

#### `Reckup(TemplateView)`
- Descarga backup de la BD desde Google Drive
- Llama `sincronizador.reckup()`

#### `MarcarDescargado(View)`
- POST AJAX: marca/desmarca planilla como descargada
- Registra usuario y fecha de descarga

### 1.5 Sistema de tareas (`task.py`)

#### `ColaTareasWorker` (Singleton)
- Cola de tareas en hilo daemon (no bloqueante)
- `agregar_tarea(func, *args)`: encola función
- `ejecutar_tareas()`: loop infinito que procesa cola
- Espera hasta hora programada antes de ejecutar
- Thread-safe con locks

#### `agregar_tareas_en_cola(hora_inicio)`
Encola tareas estándar:
1. `principal` (actualizador_main): descarga planillas desde Gmail, procesa con Google Sheets
2. `principal_csv` (actualizador_csv): procesa CSVs y actualiza items en BD
3. `buckup` (sincronizador): sube backup de BD a Drive

#### `HiloManager` (legacy)
- Gestión manual de hilos con `nuevo_hilo`, `iniciar_hilo`, `agregar_proceso`
- `agregar_proceso` es BLOQUEANTE (usa `.join()`)
- Reemplazado por `ColaTareasWorker` en la práctica

#### Imports lazy
Todas las funciones reales se importan lazy (dentro de funciones) para evitar `populate() isn't reentrant` durante la inicialización de Django.

### 1.6 Procesamiento principal (`actualizador_main.py`, 808 líneas)

Función `principal()`:
1. Inicializa Django (lazy setup)
2. Usa `Patoba` para acceder a Gmail y Drive
3. Busca emails con planillas de proveedores
4. Descarga adjuntos a Drive
5. Registra planillas en `Listado_Planillas`
6. Copia hojas a plantillas de Google Sheets
7. Llama `buscar_modificar_registros_lotes()` para actualizar items

### 1.7 Procesamiento CSV (`actualizador_csv.py`, 1156 líneas)

Función `principal_csv()`:
1. Lee planillas marcadas como `listo=True`
2. Descarga desde Drive
3. Parsea con pandas según `Condiciones` del proveedor
4. Actualiza `Item.final_base`, `final_efectivo_base`, etc.
5. Aplica `recompute_finales()` (factor_division + redondeo)
6. Marca items como actualizados

Función `apply_custom_round()`:
- Aplica redondeo unificado a todos los items
- Usa `utils.rounding.round_price()`

Función `buscar_modificar_registros_lotes()`:
- Busca items por código en lotes
- Actualiza precios base desde el CSV
- Soporta `ACT_CSV_BATCH_SIZE` y `ACT_CSV_EFECTIVO_DESCUENTO_PCT` desde settings

### 1.8 Sincronizador (`sincronizador.py`)

- `buckup()`: Sube `db.sqlite3` a Google Drive (carpeta hardcodeada)
- `reckup()`: Descarga `db.sqlite3` desde Google Drive
- Usa `Patoba(None)` (autenticación con usuario ID 1)

### 1.9 Settings relevantes

| Setting | Descripción |
|---------|-------------|
| `INBOX` | ID de carpeta Drive con planillas entrantes |
| `PLANTILLAS` | ID de carpeta Drive con plantillas |
| `DESCARGAR` | ID de carpeta Drive para descargas |
| `ACT_CSV_BATCH_SIZE` | Tamaño de lote CSV (default 1000) |
| `ACT_CSV_EFECTIVO_DESCUENTO_PCT` | % descuento efectivo (default 0) |

### 1.10 Dependencias

- `bdd.classes.Patoba` (Google Drive/Gmail/Sheets)
- `bdd.models.Listado_Planillas`, `Item`, `Proveedor`
- `bdd.views.base.MiVista`, `bdd.views.forms.MyForm`
- `utils.rounding.round_price`
- `x_cartel.models.Carteles`, `CartelesCajon`
- `pandas`, `openpyxl`, `google-api-python-client`

---

## 2. administracion_financiera

### 2.1 Propósito

Gestión financiera del negocio: boletas de proveedores, servicios, impuestos, cheques, cuentas, tarjetas de crédito, débitos automáticos y cuenta corriente por proveedor.

### 2.2 Estructura

```
administracion_financiera/
├── __init__.py
├── admin.py               (112 líneas)
├── apps.py
├── models.py              (285 líneas)  - 12 modelos
├── views.py               (342 líneas)  - 24 vistas
├── services.py            (185 líneas)  - Lógica de liquidación
├── forms.py               (128 líneas)  - 8 formularios
├── urls.py                (60 líneas)   - 24 URLs
├── templatetags/
│   ├── __init__.py
│   └── form_tags.py
└── templates/administracion_financiera/ (20 templates con Tailwind)
```

### 2.3 Modelos (`models.py`)

| Modelo | Descripción |
|--------|-------------|
| `ProveedorFinanciero` | Extensión financiera de `bdd.Proveedor` (plazo, descuentos, punto venta) |
| `Cuenta` | Cuenta bancaria/MP/tarjeta (tipo, nombre, banco, identificador) |
| `TarjetaCredito` | Tarjeta de crédito (cuenta liquidación, cierre, vencimiento) |
| `Servicio` | Servicio recurrente (nombre, sujeto pasivo, periodo) |
| `Impuesto` | Impuesto (nacional/provincial/municipal, jurisdicción) |
| `Boleta` | Boleta de proveedor (proveedor, fecha, monto, estado) |
| `TicketDePago` | Ticket de pago de servicio/impuesto (periodo, vencimiento, monto) |
| `Pago` | Pago polimórfico (GenericFK a Boleta o TicketDePago) |
| `CtaCteProveedor` | Cuenta corriente por proveedor |
| `MovimientoCtaCte` | Movimiento de ctacte (cargo/abono, saldo acumulado) |
| `Cheque` | Cheque (proveedor, cuenta, número, monto, estado) |
| `DebitoAutomatico` | Débito automático (servicio/impuesto/ticket → cuenta/tarjeta) |

**MedioPago (TextChoices):** EFECTIVO, BANCO, MP, TARJETA

**Características:**
- Pago polimórfico via GenericForeignKey
- MovimientoCtaCte también polimórfico (traza origen del movimiento)
- DebitoAutomatico tiene constraints XOR (exactamente un objetivo, exactamente un medio)
- Boleta tiene unique constraint (proveedor + punto_venta + numero_completo)
- Campos `semana_iso` (formato YYYY-Www) en Boleta, TicketDePago, Pago, MovimientoCtaCte

### 2.4 URLs (24 rutas)

Montadas en `/administracion_financiera/`:

| Grupo | URLs |
|-------|------|
| Dashboard | `/` |
| Cargas | `carga/boleta/`, `carga/servicio/`, `carga/impuesto/`, `carga/cheque/` |
| Liquidación | `liquidacion/` |
| Proveedores | `proveedores/`, `proveedores/<id>/editar/` |
| Cuentas | `cuentas/`, `cuentas/nueva/`, `cuentas/<id>/editar/` |
| Tarjetas | `tarjetas/`, `tarjetas/nueva/`, `tarjetas/<id>/editar/` |
| Servicios | `servicios/`, `servicios/nuevo/`, `servicios/<id>/editar/`, `servicios/<id>/eliminar/` |
| Impuestos | `impuestos/`, `impuestos/nuevo/`, `impuestos/<id>/editar/`, `impuestos/<id>/eliminar/` |
| Tickets | `tickets/generar/impuestos/`, `tickets/generar/servicios/` |
| Quick actions | `servicios/<id>/ticket_actual/`, `impuestos/<id>/ticket_actual/` |

### 2.5 Vistas (`views.py`)

Todas decoradas con `@staff_required` (is_active + is_staff).

- **`dashboard`**: Resumen semanal (boletas y tickets pendientes)
- **`carga_*`**: Formularios de alta (boleta, servicio, impuesto, cheque)
- **`liquidacion`**: Lista pendientes de la semana, procesa pagos (boleta o ticket)
- **`proveedores_list` / `proveedor_financiero_edit`**: Gestión de proveedores financieros
- **`cuentas_list` / `cuenta_edit`**: CRUD de cuentas
- **`tarjetas_list` / `tarjeta_edit`**: CRUD de tarjetas
- **`servicios_list` / `servicio_edit` / `servicio_delete`**: CRUD de servicios
- **`impuestos_list` / `impuesto_edit` / `impuesto_delete`**: CRUD de impuestos
- **`generar_ticket_*`**: Genera tickets de pago para el periodo actual

### 2.6 Services (`services.py`)

- **`current_iso_week_key()`**: Devuelve clave ISO (ej: "2026-W28")
- **`list_pending_for_week(week_key)`**: Boletas y tickets pendientes de la semana
- **`liquidate_boleta()`**: @transaction.atomic - Crea Pago, marca boleta pagada, genera MovimientoCtaCte
- **`liquidate_ticket()`**: @transaction.atomic - Crea Pago, marca ticket pagado, auto-genera próximo ticket para el siguiente periodo
- **`_validate_allowed_account_for_ticket()`**: Valida que la cuenta esté permitida para la carga
- **`vencimiento_in_same_month()`**: Ajusta día de vencimiento al mes destino

### 2.7 Forms (`forms.py`)

8 ModelForms: `BoletaForm`, `ServicioForm`, `ImpuestoForm`, `ChequeForm`, `ProveedorFinancieroForm`, `CuentaForm`, `TarjetaCreditoForm`, `ImpuestoTicketForm`, `ServicioTicketForm`

### 2.8 Templates (20 archivos con Tailwind CSS)

- `base.html`, `dashboard.html`, `liquidacion.html`
- Cargas: `carga_boleta.html`, `carga_servicio.html`, `carga_impuesto.html`, `carga_cheque.html`
- Listas: `cuentas_list.html`, `tarjetas_list.html`, `servicios_list.html`, `impuestos_list.html`, `proveedores_list.html`
- Edición: `cuenta_edit.html`, `tarjeta_edit.html`, `servicio_edit.html`, `impuesto_edit.html`, `proveedor_financiero_edit.html`
- Tickets: `generar_ticket.html`, `generar_ticket_impuestos.html`, `generar_ticket_servicios.html`
- Parciales: `_form_fields.html`

### 2.9 Dependencias

- `bdd.models.Proveedor`
- Django ContentTypes (GenericForeignKey)
- Tailwind CSS (CDN o local)

---

## 3. reportes

### 3.1 Propósito

Generación de reportes de ventas con arquitectura hexagonal (ports & adapters). Integra con Google Drive para leer planillas de control y escribir reportes.

### 3.2 Estructura

```
reportes/
├── __init__.py
├── admin.py
├── apps.py
├── models.py              (32 líneas)   - ReportControlEntry
├── urls.py                (11 líneas)   - 2 URLs
├── views.py               (223 líneas)  - DailyReportView
├── views_batch.py         (147 líneas)  - DriveBatchView
├── usecases.py            (396 líneas)  - RunDailyReport (caso de uso)
├── ports.py               (60 líneas)   - DrivePort, StoragePort, ExcelIO (abstract)
├── adapters_patoba.py     (89 líneas)   - PatobaDriveAdapter
├── adapters_storage.py    - DjangoStorageAdapter
├── excel_io.py            (29 líneas)   - PandasExcelIO
├── forms.py               (49 líneas)   - DailyReportForm
├── conf.py                (33 líneas)   - Configuración con defaults
└── templates/reportes/
    ├── diario.html
    └── drive_batch.html
```

### 3.3 Arquitectura hexagonal

```
views.py
  → usecases.py (RunDailyReport)
    → ports.py (DrivePort, StoragePort, ExcelIO - abstract)
    → adapters_patoba.py (PatobaDriveAdapter → bdd.classes.Patoba)
    → adapters_storage.py (DjangoStorageAdapter → Django default_storage)
    → excel_io.py (PandasExcelIO → pandas/openpyxl/odf)
```

### 3.4 Modelos

#### `ReportControlEntry`
- `name`, `drive_file_id` (unique), `mime_type`, `folder_id`
- `allowed`, `processed` (booleanos de control)
- `year`, `month` (para organización)
- `last_processed_at`, `error_message`
- `created_at`, `updated_at`
- Indexes en `folder_id` y `(allowed, processed)`

### 3.5 URLs

| URL | Vista | Descripción |
|-----|-------|-------------|
| `reportes/diario/` | `DailyReportView` | Reporte diario de ventas |
| `reportes/drive-batch/` | `DriveBatchView` | Procesamiento batch desde Drive |

### 3.6 Ports (`ports.py`)

**`DrivePort` (ABC):** `download_file`, `upload_or_update`, `ensure_child_folder`, `list_folder`, `read_sheet_values`, `find_child_folder_by_name`, `find_folder_by_name`

**`StoragePort` (ABC):** `save`

**`ExcelIO` (ABC):** `read_all_sheets`, `write_xlsx`, `write_ods`

### 3.7 Adapters

- **`PatobaDriveAdapter`**: Implementa `DrivePort` usando `bdd.classes.Patoba`
- **`DjangoStorageAdapter`**: Implementa `StoragePort` usando `django.core.files.storage.default_storage`
- **`PandasExcelIO`**: Implementa `ExcelIO` usando pandas + openpyxl + odf

### 3.8 Configuración (`conf.py`)

Defaults overridables desde settings:
- `REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID`: carpeta Drive de salida
- `REPORTES_INPUT_FOLDER_ID` / `REPORTES_INPUT_FOLDER_NAME`: carpeta de entrada
- `REPORTES_CONTROL_SHEET_ID` / `REPORTES_CONTROL_TAB`: libro de control
- `REPORTES_REQUIRE_STAFF`: requiere staff (default True)
- `REPORTES_ALLOWED_MIME_TYPES`: xlsx, ods
- `REPORTES_MIN_YEAR`: año mínimo (2026)

### 3.9 Dependencias

- `bdd.classes.Patoba` (Google Drive)
- `pandas`, `openpyxl`, `odf` (Excel/ODS)
- `django-allauth` (OAuth token)

---

## 4. x_cartel

### 4.1 Propósito

Generación y edición de carteles de precios para impresión. Cada item puede tener un cartel con descripción, precios y tamaños de fuente configurables.

### 4.2 Estructura

```
x_cartel/
├── __init__.py
├── admin.py
├── apps.py
├── models.py              (71 líneas)   - 3 modelos
├── views.py               (228 líneas)  - 5 vistas
├── urls.py                (33 líneas)   - 7 URLs
└── templates/x_cartel/
    ├── cartel.html
    ├── cartelitos_x6.html
    └── prueba_edicion.html
```

### 4.3 Modelos

#### `Cartelitos`
- `item` - OneToOne→`bdd.Item`
- `proveedor` - FK→`bdd.Proveedor`
- `revisar`, `habilitado` - BooleanField
- `descripcion` - TextField (auto-inicializada con `item.descripcion`)

#### `Carteles`
- `item` - FK→`bdd.Item`
- `proveedor` - FK→`bdd.Proveedor`
- `revisar` - BooleanField
- `descripcion`, `texto_final`, `final`, `final_efectivo`, `texto_final_efectivo` - TextField (contenido del cartel)
- `tamano_descripcion`, `tamano_texto_final`, `tamano_final`, `tamano_final_efectivo`, `tamano_texto_final_efectivo` - IntegerField (tamaños de fuente)

#### `CartelesCajon`
Igual que `Carteles` pero para cajones completos.

### 4.4 URLs

| URL | Vista | Descripción |
|-----|-------|-------------|
| `x_cartel/` | `Cartel` | Cartel por defecto |
| `x_cartel/imprimir/<item_id>` | `Cartel` | Cartel de un item específico |
| `x_cartel/imprimir_cajon/<cajon_id>` | `Cartel` | Carteles de un cajón |
| `x_cartel/cartelito/` | `CrearCartelitoView` | Crear cartelito |
| `x_cartel/imprimir_cartelitos/` | `Cartelito` | Imprimir cartelitos habilitados |
| `precios_articulos/<articulo_id>` | `precios_articulos` | AJAX: precios de un item |
| `precios_articulos_cajon/<cajon_id>` | `precios_articulos_cajon` | AJAX: precios de un cajón |

### 4.5 Vistas

- **`Cartel(TemplateView)`**: Edición de cartel. GET muestra formulario con datos del item/caron. POST guarda tamaños de fuente y textos.
- **`Cartelito(TemplateView)`**: Lista cartelitos habilitados para impresión (6 por página)
- **`CrearCartelitoView`**: Alta de cartelitos
- **`precios_articulos`** / **`precios_articulos_cajon`**: Endpoints AJAX que devuelven precios

### 4.6 Dependencias

- `bdd.models.Item`, `bdd.models.Cajon`
- Integrado con `bdd.views.main.ListarCarteles`

---

## 5. x_articulos

### 5.1 Propósito

CRUD experimental de items. Filtra items por código `metdh` (hardcodeado). Usa el sistema de andamios de `core_elementos`.

### 5.2 Estructura

```
x_articulos/
├── __init__.py
├── admin.py
├── apps.py
├── models.py              (12 líneas)   - 1 modelo
├── views.py               (113 líneas)  - 1 vista
├── forms.py               (32 líneas)   - 2 forms
├── urls.py                (8 líneas)    - 2 URLs
└── templates/x_articulos/
    └── crud.html
```

### 5.3 Modelo

#### `Articulo`
- `codigo` - CharField(50)
- `descripcion` - CharField(250)
- `precio_base` - FloatField
- `ultimo_cambio` - DateField (auto_now_add)
- `actualizado` - BooleanField
- `precio_efectivo` - FloatField

**Nota:** Este modelo es DIFERENTE de `bdd.Item`. Parece ser un modelo experimental/abandonado.

### 5.4 Forms

- **`ArticuloForm`**: ModelForm para `Articulo` (codigo, precio_base, precio_efectivo)
- **`Item_Form`**: ModelForm para `bdd.Item` (codigo, barras, finales, sub_carpeta, sub_titulo, actualizado, stock, proveedor)

### 5.5 URLs

| URL | Vista | Descripción |
|-----|-------|-------------|
| `articulos/` | `Crud` | Tabla CRUD |
| `articulos/<id>` | `Crud` | Tabla CRUD (con ID, no usado diferenciado) |

### 5.6 Vista

#### `Crud(TemplateView)`
- Template: `x_articulos/crud.html`
- Filtra items con `codigo__contains="metdh"` (hardcodeado)
- Omite 26 campos de Item
- Muestra solo: codigo, descripcion + campos no omitidos
- Usa `core_elementos/core_tabla_crud.html` y `core_elementos/core_modal.html`
- POST: actualiza item via AJAX

**Estado:** App experimental con filtro hardcodeado. No es de uso general.

---

## 6. carga_archivo

### 6.1 Propósito

Upload simple de archivos al sistema.

### 6.2 Estructura

```
carga_archivo/
├── __init__.py
├── admin.py
├── apps.py
├── models.py              (7 líneas)   - 1 modelo
├── views.py               (15 líneas)  - 1 vista
├── forms.py               (10 líneas)  - 1 form
├── urls.py                (7 líneas)   - 1 URL
└── templates/
    ├── upload.html
    └── success.html
```

### 6.3 Modelo

#### `Document`
- `uploaded_file` - FileField (upload_to="media/")

### 6.4 URL

| URL | Vista | Descripción |
|-----|-------|-------------|
| `upload_file/` | `upload_file` | Formulario de upload |

### 6.5 Vista

#### `upload_file(request)`
- GET: muestra formulario `UploadFileForm`
- POST: guarda archivo, muestra `success.html`

### 6.6 Estado

App minimalista funcional. Montada en la raíz de URLs.

---

## 7. utils (módulo)

### 7.1 Propósito

Módulo de utilidades transversales usado por múltiples apps.

### 7.2 Estructura

```
utils/
├── __init__.py
├── rounding.py            (52 líneas)   - round_price
├── ordenar_query.py       (22 líneas)   - agrupar_transacciones_por_fecha
├── outsider.py            (12 líneas)   - arrancar_django_config
├── constantes_django.py   (5 líneas)    - TIPOS_LOGS
└── queryset_to_xlsx.py    (175 líneas)  - queryset_to_xlsx
```

### 7.3 Funciones

#### `rounding.py`

**`round_price(value, is_cartel)`** - Regla unificada de redondeo:
- ≤ 0 → 0
- < 50 → 50
- < 75 → 50
- < 100 → 100
- Sin cartel, ≥ 100 → múltiplo de 100 más cercano
- Con cartel, > 1000 → múltiplo de 500 más cercano
- Con cartel, ≥ 10000 y múltiplo de 1000 → restar 100
- Mínimo: 50

Usado por: `bdd.models.Item.recompute_finales()`, `actualizador.actualizador_csv.apply_custom_round()`

#### `ordenar_query.py`

**`agrupar_transacciones_por_fecha(queryset)`** → dict anidado `{año: {mes: {dia: [transacciones]}}}`

Usado por: `facturacion.views.FacturacionMensual`

#### `outsider.py`

**`arrancar_django_config()`** - Setea `DJANGO_SETTINGS_MODULE` y llama `django.setup()`. Para scripts standalone.

#### `constantes_django.py`

**`TIPOS_LOGS`** - `[("I", "INFO: "), ("E", "Error: ")]`

#### `queryset_to_xlsx.py`

**`queryset_to_xlsx(queryset, filename)`** - Exporta queryset a archivo .xlsx con openpyxl. Soporta dicts y objetos de modelo.

**Nota:** Llama `arrancar_django_config()` a nivel de importación (puede causar problemas si se importa desde Django).

---

## 8. Apps vacías/abandonadas

### x_widgets

- **Sin modelos, sin vistas, sin URLs**
- Mencionada en `core_docs/docs/core.md` (incorrectamente como `.widgets`)
- Abandonada

### core_testing

- **Sin modelos, sin vistas, sin URLs, sin tests**
- Solo tiene `migrations/0001_initial.py` (migración vacía)
- Abandonada

### cajas

- **Sin modelos, sin vistas, sin URLs**
- 2 templates experimentales (no usados)
- Abandonada

### articulos

- 6 modelos definidos (`Marca`, `Categoria`, `Cartel`, `Proveedor`, `Articulo`, `CodigoBarras`, `ArticuloProveedor`)
- **Sin vistas, sin URLs**
- Los modelos duplican conceptos de `bdd` (Marca, Proveedor, Articulo)
- Probablemente abandonada en favor de `bdd`

---

## 9. Resumen de dependencias entre apps auxiliares

```
actualizador
  ├── bdd (MiVista, MyForm, Patoba, Listado_Planillas, Item, Proveedor)
  ├── utils (round_price)
  ├── x_cartel (Carteles, CartelesCajon)
  └── bdd.funtions (get_emails)

administracion_financiera
  └── bdd (Proveedor)

reportes
  └── bdd (Patoba)

x_cartel
  └── bdd (Item, Cajon, Proveedor)

x_articulos
  ├── bdd (Item)
  └── core_elementos (templates)

carga_archivo
  └── (sin dependencias de otras apps)

utils
  └── (sin dependencias, standalone)
```

### Apps por tamaño (líneas de código)

| App | Líneas aprox. | Estado |
|-----|---------------|--------|
| `actualizador` | ~2600 | Activa, core del negocio |
| `administracion_financiera` | ~750 | Activa, completa |
| `reportes` | ~900 | Activa, arquitectura hexagonal |
| `x_cartel` | ~350 | Activa |
| `x_articulos` | ~200 | Experimental (filtro hardcodeado) |
| `carga_archivo` | ~50 | Activa, minimalista |
| `utils` | ~260 | Activa, transversal |
| `x_widgets` | ~10 | Abandonada |
| `articulos` | ~80 | Abandonada |
