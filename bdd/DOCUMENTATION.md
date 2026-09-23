# App `bdd` - Base de Datos Central

**Versión documentada:** v3.10.0
**Fecha:** 2026-07-13

---

## 1. Propósito

`bdd` es la aplicación central del sistema Ferretería Paoli. Contiene:
- El modelo de inventario completo (`Item` con 40+ campos)
- El sistema de construcción dinámica de vistas (Armador)
- El sistema de carritos de compra con roles de usuario
- Los endpoints AJAX para carrito, pedidos y edición de items
- La integración con Google Drive/Gmail para planillas de proveedores
- El template base `generic_template.html` que usa todo el sistema

Es la app de la que dependen `facturacion`, `pedido`, `x_cartel`, `actualizador` y `administracion_financiera`.

---

## 2. Estructura de Archivos

```
bdd/
├── __init__.py
├── admin.py              (95 líneas)  - Registro automático de todos los modelos
├── apps.py               (7 líneas)   - AppConfig
├── classes.py            (832 líneas) - Clase Patoba: integración Google Drive/Gmail/Sheets
├── models.py             (654 líneas) - 22 modelos
├── urls.py               (124 líneas) - URLs dinámicas + estáticas
├── views/
│   ├── __init__.py       (25 líneas)  - Re-exports para urls.py
│   ├── base.py           (529 líneas) - MiVista: vista base con Armador
│   ├── main.py           (632 líneas) - Vistas principales (Inicio, Busqueda, Imprimir, etc.)
│   ├── ajax.py           (827 líneas) - 11 endpoints AJAX
│   ├── forms.py          (184 líneas) - MyForm dinámico + BusquedaForm
│   └── utils.py          (169 líneas) - Helpers: articulo_to_dict, calcular_total, carrito_to_dict
├── views_old.py          (1230 líneas) - CÓDIGO LEGACY (duplicado de views/)
├── templatetags/
│   ├── __init__.py
│   └── custom_filters.py (42 líneas)  - Filtros: zip_lists, to_float, en_lista
└── templates/            (vacío - los templates están en static/templates/)
```

**Nota:** Los templates que usa `bdd` NO están en `bdd/templates/` sino en `static/templates/` (directorio global de templates).

---

## 3. Modelos (`bdd/models.py`)

### 3.1 Inventario

#### `Item` - Modelo central (40+ campos)

Representa un producto del inventario. Es el modelo más importante del sistema.

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `cajon` | FK→`Cajon` | null | Ubicación física del item |
| `marca` | FK→`Marca` | null | Marca del producto |
| `codigo` | CharField(20) | null | Código del item (formato `XXX/AB`) |
| `barras` | IntegerField | null | Código de barras |
| `descripcion` | CharField(200) | null | Descripción del producto |
| `precio_base` | FloatField | 0.0 | Precio de planilla del proveedor |
| `porcentaje` | FloatField | 1.0 | Porcentaje al público |
| `porcentaje_efectivo` | FloatField | 1.0 | Porcentaje en efectivo |
| `porcentaje_oferta` | FloatField | 1.0 | Porcentaje de oferta |
| `porcentaje_oferta_efectivo` | FloatField | 1.0 | Porcentaje de oferta en efectivo |
| `oferta` | BooleanField | False | Si el item está en oferta |
| `precio_rollo_caja` | BooleanField | False | Si el precio base es por rollo/caja |
| `venta_rollo_caja` | BooleanField | False | Si se vende por rollo/caja |
| `porcentaje_metro` | FloatField | 1.0 | Porcentaje distinto para venta por metro |
| `pack_cantidad` | FloatField | 1.0 | Cantidad que divide/multiplica el precio base |
| `cantidad_rollo_caja` | FloatField | 1.0 | Cantidad que trae el rollo/caja |
| `descuento_rollo_caja` | FloatField | 1.0 | Descuento venta por rollo/caja |
| `descuento_rollo_caja_efectivo` | FloatField | 1.0 | Descuento rollo/caja en efectivo |
| `final_rollo` | FloatField | 0.0 | Precio final por rollo |
| `final_rollo_efectivo` | FloatField | 0.0 | Precio final por rollo en efectivo |
| `final` | FloatField | 0.0 | Precio final al público |
| `final_efectivo` | FloatField | 0.0 | Precio final en efectivo |
| `final_base` | FloatField | 0.0 | Precio base sin factor_division (escrito por actualizador) |
| `final_efectivo_base` | FloatField | 0.0 | Idem para efectivo |
| `final_rollo_base` | FloatField | 0.0 | Idem para rollo |
| `final_rollo_efectivo_base` | FloatField | 0.0 | Idem para rollo efectivo |
| `trabajado` | BooleanField | False | Si el item está siendo trabajado |
| `sub_carpeta` | FK→`Sub_Carpeta` | null | Hoja de destino para impresión |
| `sub_titulo` | FK→`Sub_Titulo` | null | Subtítulo para organización |
| `actualizado` | BooleanField | False | Si está actualizado respecto a la planilla |
| `fecha` | DateField | auto_now_add | Fecha de creación |
| `stock` | FloatField | 0.0 | Cantidad en stock |
| `proveedor` | FK→`Proveedor` | null | Proveedor del item |
| `factor_division` | FloatField | null | Factor de división para conversión unidad/caja |
| `tiene_cartel` | BooleanField | False | Si tiene cartel impreso |
| `tipo_cartel` | FK→`Tipo_Cartel` | null | Tipo de cartel |
| `p_c_efectivo` | FloatField | 0.0 | % cartel efectivo |
| `p_c_debito` | FloatField | 0.0 | % cartel débito |
| `p_c_credito` | FloatField | 0.0 | % cartel crédito |

**Métodos:**
- `calcular_precio_final()` - Calcula `self.final` (BUG: referencia `self.constante` que no existe)
- `calcular_precio_efectivo_final()` - Calcula `self.final_efectivo` (BUG: referencia `self.constante`)
- `calcular_precio_rollo_final()` - Calcula `self.final_rollo` (BUG: referencia `self.venta_metro`)
- `calcular_precio_rollo_efectivo_final()` - Calcula `self.final_rollo_efectivo`
- `marcar_actualizado()` / `marcar_desactualizado()` - Setea `actualizado`
- `recompute_finales()` - Deriva `final*` desde `*_base` aplicando `factor_division` y redondeo. Usa `utils.rounding.round_price()`. **No guarda** el modelo (caller debe llamar `save()`)

**Sistema de precios:**
1. El `actualizador` escribe `final_base`, `final_efectivo_base`, etc. desde el CSV del proveedor
2. `recompute_finales()` deriva `final`, `final_efectivo`, etc. aplicando `factor_division` (si > 1) y redondeo
3. Las vistas muestran `final` y `final_efectivo` directamente

#### `Marca`
- `codigo` - CharField(20)

#### `Cod_Barras`
- `barras` - IntegerField
- `articulo` - FK→`Item`

#### `Sector` → `Cajonera` → `Cajon`
Jerarquía de ubicación física:
- `Sector`: `codigo` (CharField 20)
- `Cajonera`: `codigo`, FK→`Sector`
- `Cajon`: `codigo`, FK→`Cajonera`

#### `Sub_Carpeta`, `Sub_Titulo`, `Tipo_Cartel`
Heredan de `Generica` (campo `nombre`). Usados para organización de impresión y carteles.

### 3.2 Proveedores

#### `ListaProveedores`
- `abreviatura` - CharField(5) (ej: `/3D`, `/B`, `/F`)
- `nombre` - CharField(25)
- `hay_csv_pendiente` - BooleanField (usado por admin actions)

#### `Proveedor`
- `identificador` - FK→`ListaProveedores`
- `text_display` - CharField(30) (nombre visible)
- `cuit`, `direccion`, `email`, `telefono` - Datos de contacto
- `corredor`, `corredor_telefono` - Datos del corredor

#### `Condiciones`
Configuración de cómo leer el CSV de cada proveedor:
- `proveedor` - FK→`Proveedor`
- `fila_inicial` - IntegerField (fila donde empiezan los datos)
- `codigo`, `nombre`, `precio_base` - CharField(1) (letra de columna A/B/C...)
- `porcentaje`, `porcentaje_21`, `porcentaje_10_5` - FloatField
- `dolar` - CharField(1) (columna del dólar)

**BUG:** `detectar_columna()` y `ordenar_columnas()` referencian `self.descripcion` que no existe como campo.

#### `Archivo`
- `proveedor` - FK→`Proveedor`
- `condiciones` - FK→`Condiciones`
- `agregado` - DateField (auto_now_add)
- `editado` - DateField (auto_now)
- `archivo` - FileField (upload_to="inbox")

**BUG:** `descargar()` y `basename()` referencian `self.descarga` que no existe.

#### `Compras`
- `proveedor` - FK→`Proveedor`
- `fecha` - DateField
- `numero_remito` - IntegerField
- `importe`, `saldo` - FloatField
- `observaciones` - TextField

### 3.3 Planillas

#### `Listado_Planillas`
Registro de planillas descargadas/procesadas desde Google Drive:
- `proveedor` - FK→`Proveedor`
- `fecha` - DateField (auto_now_add)
- `descripcion` - CharField(50)
- `identificador` - CharField(50) (unique)
- `hoja` - CharField(50)
- `listo` - BooleanField (procesada)
- `descargar` - BooleanField (marcada para descarga)
- `link_descarga` - CharField(50) (ruta al .xlsx)
- `link_descarga_ods` - CharField(50) (ruta al .ods)
- `id_sp` - CharField(50) (ID de Google Sheets)
- `hojas` - TextField (lista de hojas)
- `descargado` - BooleanField (si fue descargada por usuario)
- `fecha_descarga` - DateTimeField
- `usuario_descarga` - FK→`auth.User`

### 3.4 Sistema de Pedidos

#### `Lista_Pedidos`
- `proveedor` - FK→`Proveedor`
- `item` - FK→`Item`
- `cantidad` - FloatField
- `pedido` - BooleanField (si fue confirmado/pedido)

### 3.5 Sistema de Carrito

#### `Carrito`
- `usuario` - FK→`auth.User`
- Relación: 1 usuario → 1 carrito

#### `Articulo` (en carrito)
- `item` - FK→`Item`
- `carrito` - FK→`Carrito` (related_name="articulos")
- `cantidad` - FloatField
- `precio` - DecimalField(10,2) (precio al público)
- `precio_efectivo` - DecimalField(10,2)

#### `ArticuloSinRegistro`
Para items que no están en el inventario pero se venden:
- `descripcion` - CharField(300)
- `carrito` - FK→`Carrito` (related_name="articulos_sin_registro")
- `cantidad` - FloatField
- `precio` - DecimalField(10,2)

### 3.6 Sistema de Andamios (UI dinámica)

#### `NavBar`
- `url_inicial` - CharField(20)
- `text_display` - CharField(30)

#### `Muro`
- `muro_html` - CharField(30) (nombre del template de muro)

#### `Plantilla`
- `plantilla_html` - CharField(30) (nombre del template de plantilla)

#### `Contenedor`
- `nombre` - CharField(30)
- `url` - CharField(30)
- `a`, `b`, `c` - FK→`Plantilla` (hasta 3 plantillas por contenedor)

#### `Modelo_Campos`
- `nombre` - CharField(30) (campo del modelo a mostrar)

#### `Formulario_Campos`
- `nombre` - CharField(30) (campo del formulario)

#### `Formulario_Campos_Contiene`
- `nombre` - CharField(30) (campo que usa búsqueda `__icontains`)

#### `Formulario_Campos_Empieza_Con`
- `nombre` - CharField(30) (campo que usa búsqueda `__istartswith`)

#### `Armador` - Configurador dinámico de vistas
- `nav_bar` - FK→`NavBar`
- `vista` - CharField(30) (nombre de la clase vista, default "Inicio")
- `url` - CharField(30) (ruta URL)
- `url_nombre` - CharField(30)
- `muro` - FK→`Muro`
- `contenedor` - FK→`Contenedor`
- `modelo` - CharField(30) (nombre del modelo a mostrar)
- `modelo_campos` - M2M→`Modelo_Campos` (campos a mostrar en tabla)
- `busqueda` - BooleanField (si la vista tiene búsqueda)
- `formulario` - CharField(30)
- `formulario_boton` - CharField(30)
- `formulario_campos` - M2M→`Formulario_Campos`
- `formulario_campos_contiene` - M2M→`Formulario_Campos_Contiene`
- `formulario_campos_empieza_con` - M2M→`Formulario_Campos_Empieza_Con`

### 3.7 Registros

#### `Tipo_Registro`
- `nombre` - CharField(30)

#### `Registros`
- `fecha` - DateField
- `tipo` - FK→`Tipo_Registro`
- `nombre` - CharField(30)
- `link` - CharField(200)
- `link_descargar` - CharField(200)
- `automatioco` - BooleanField (sic, typo en el campo)

### 3.8 Modelos abstractos

- `GenericaLista` (abstract): `abreviatura`, `nombre`
- `Generica` (abstract): `nombre`

---

## 4. Vistas

### 4.1 `views/base.py` - `MiVista(TemplateView)`

**Template:** `generic_template.html`

Es la vista base de casi todo el sistema. Su `get_context_data()` construye el contexto completo:

1. **Versión** (líneas 42-57): Lee `package.json` y pone `context["version"]`
2. **Navegación** (línea 60): `NavBar.objects.all()` → `context["barra_de_navegacion"]`
3. **Armador** (líneas 65-206): Busca `Armador` por URL, obtiene:
   - `muro` (template del muro)
   - `contenedor` (plantillas a incluir)
   - `modelo` (modelo Django para la tabla)
   - `formulario_campos` (campos del formulario)
   - `titulos` (campos a mostrar en tabla)
   - Construye `MyForm` dinámico
4. **Planillas** (líneas 208-231): Cuenta planillas nuevas y descargables
5. **MercadoPago** (líneas 233-330): Si `INTEGRATE_MERCADOPAGO` e `INTERNET` están activos, busca pagos de los últimos 30 min y 24 horas
6. **Links de pedidos** (línea 333): `settings.TABLA_LINK_PEDIDOS`

**Método `get()`:** Si el Armador tiene `busqueda=True`, procesa los parámetros GET para filtrar el modelo. Soporta `__icontains` y `__istartswith` según la configuración del Armador. Si el modelo es `Item`, anota `tiene_pedido` (Exists sobre `Lista_Pedidos`).

**Método `post()`:** Procesa el formulario `MyForm` para guardar datos en el modelo configurado por el Armador.

### 4.2 `views/main.py` - Vistas principales

#### `Inicio(MiVista)`
Hereda todo de `MiVista`. Es la página principal del sistema.

#### `Prueba(MiVista)`
Vista de prueba. Agrega `context["titulo_prueba"]`.

#### `BusquedaView(FormView)`
- **Template:** `plantilla_prueba.html`
- **Form:** `BusquedaForm` (marca, cajon, cajonera, sector)
- Filtra `Item` por marca, cajón, cajonera o sector

#### `ItemsView(View)`
- Endpoint AJAX que devuelve items de un cajón específico
- URL: `items/<int:cajon_id>`
- Devuelve JSON: `[{id, codigo, descripcion, final}]`

#### `Imprimir(TemplateView)`
- **Template:** `generic_template.html`
- Maneja dos rutas:
  - `/imprimir/` - Formulario para seleccionar sub_carpeta y sub_titulo
  - `/imprimir/tabla/` - Tabla con items filtrados para imprimir carteles
- Campos mostrados: descripcion, final, final_efectivo, final_rollo, final_rollo_efectivo, actualizado

#### `ListadoPedidos(MiVista)`
- Sobrescribe `get()` para filtrar `Lista_Pedidos`
- Soporta filtros por campos que contienen (`__icontains`) o empiezan con (`__istartswith`)
- Manejo especial de ForeignKey: si el campo es FK y el modelo relacionado tiene `descripcion`, usa `__descripcion__icontains`
- Campos mostrados: id, item__codigo, item__descripcion, cantidad, pedido
- Usa `select_related("item")` para optimizar

#### `ListarCarteles(TemplateView)`
- **Template:** `generic_template.html`
- Lista cajones que tienen items con carteles
- Filtros: proveedor, revisar (boolean)
- Crea `CartelesCajon` si no existen para cada cajón
- Items sin cajón se listan aparte
- Cada item tiene URL `/x_cartel/imprimir/<item_id>/`

### 4.3 `views/ajax.py` - Endpoints AJAX

#### `crear_modificar_lista_pedidos(request, proveedor_id=None)`
- **GET:** Devuelve lista de pedidos como JSON, opcionalmente filtrados por proveedor
- **POST:** Crea o incrementa cantidad en `Lista_Pedidos` a partir del código del item
  - Determina proveedor por abreviatura del código (ej: `XXX/3D` → proveedor con abreviatura `/3D`)
  - Fallback: usa `item.proveedor` si no encuentra por abreviatura
  - Marca `item.trabajado = True` y asigna proveedor

#### `seleccionar_proveedor(request)`
- Devuelve lista de proveedores (JSON si accepts JSON, HTML si no)

#### `cambiar_cantidad_pedido(request, id_articulo, cantidad)`
- **POST:** Cambina cantidad de un `Lista_Pedidos`
- Si cantidad = 0, elimina el registro

#### `editar_item(request, id_articulo)`
- **GET:** Devuelve datos del item para modal de edición (stock, barras, tiene_cartel, cajon, cajones disponibles, proveedores, subtitulos, factor_division)
- **POST:** Actualiza stock, barras, tiene_cartel, cajon, proveedor, sub_titulo, factor_division
- Si las columnas base existen en DB, llama `recompute_finales()` y devuelve precios actualizados

#### `agregar_articulo_a_carrito(request, id_articulo)`
- **POST:** Agrega item al carrito del usuario (o de otro usuario si es caja_general)
- Soporta cantidades decimales (acepta coma como separador)
- También actualiza `Lista_Pedidos` si el item tiene proveedor

#### `carrito(request)`
- **GET:** Devuelve info básica del carrito del usuario actual

#### `consultar_carrito(request)`
- **GET:** Devuelve contenido detallado de carritos
- Si el usuario es `caja_general` (superuser, username="Caja", o grupo "caja_general"): puede ver todos los carritos de cajeros
- Si no, solo ve su propio carrito
- Cada carrito incluye: articulos, articulos_sin_registro, carrito_id, color
- Calcula totales con `calcular_total()`

#### `usuarios_caja(request)`
- **GET:** Devuelve lista de usuarios del grupo "cajeros" (excluyendo "Caja")
- Incluye color por usuario

#### `eliminar_articulo_pedido(request)`
- **POST:** Confirma (marca `pedido=True`) o elimina un `Lista_Pedidos`

#### `descargar_archivo(request)`
- **GET:** Descarga `script_pyinstaller.py` desde MEDIA_ROOT

#### `reportar_item(request, articulo_id)`
- **GET:** Devuelve estados posibles para reporte de item

#### `enviar_reporte(request, articulo_id)`
- **POST:** Recibe reporte de item (estado + detalles)
- **NOTA:** La lógica de guardado está comentada (modelo de reporte pendiente)

### 4.4 `views/forms.py`

#### `MyForm(forms.Form)`
Formulario dinámico que se construye a partir de un nombre de modelo y lista de campos:
- `__init__(model_name, fields_to_show)`: Busca el modelo en apps `bdd` o `x_cartel`, crea campos automáticamente
- Si `fields_to_show == ["__all__"]`: muestra todos los campos
- Si `fields_to_show == ["None"]`: no muestra campos
- Aplica widgets personalizados: DateInput, TimeInput, DateTimeInput, EmailInput
- `save(model_name)`: Crea una nueva instancia del modelo con los datos del formulario

#### `BusquedaForm(forms.Form)`
- Campos: marca, cajon, cajonera, sector (todos ModelChoiceField, opcionales)

### 4.5 `views/utils.py`

#### `articulo_to_dict(articulo)`
Convierte `Articulo` o `ArticuloSinRegistro` a diccionario para JSON:
- `Articulo`: id, item, descripcion, cantidad, precio, precio_efectivo
- `ArticuloSinRegistro`: id, descripcion, cantidad, precio, precio_efectivo (= precio)

#### `calcular_total(datos)`
Calcula totales por carrito:
- Suma `precio * cantidad` para articulos registrados
- Suma `precio_efectivo * cantidad` para efectivo
- Para sin registro: usa `precio` para ambos totales
- Usa `Decimal` con `ROUND_HALF_UP` y 2 decimales
- Acepta cantidades decimales con coma o punto

#### `carrito_to_dict(carrito)`
Devuelve `{id, usuario}` del carrito.

### 4.6 `views/__init__.py`
Re-exporta todas las vistas públicas para que `urls.py` pueda importarlas.

---

## 5. URLs (`bdd/urls.py`)

### URLs dinámicas (desde DB)
```python
for nav_bar in NavBar.objects.all():
    armador = Armador.objects.get(nav_bar=nav_bar)
    vista = import_string(f"bdd.views.{armador.vista}")
    armador_paths.append(path(nav_bar.url_inicial, vista.as_view(), name=nav_bar.text_display))
```
Las URLs se generan automáticamente desde los modelos `NavBar` y `Armador` en la base de datos.

### URLs estáticas

| URL | Vista | Nombre |
|-----|-------|--------|
| `items/<int:cajon_id>` | `ItemsView` | `items` |
| `seleccionar_proveedor/` | `seleccionar_proveedor` | `seleccionar_proveedor` |
| `carrito/` | `carrito` | `carrito` |
| `editar_item/<int:id_articulo>/` | `editar_item` | `editar_item` |
| `agregar_articulo_a_carrito/<int:id_articulo>/` | `agregar_articulo_a_carrito` | `agregar_articulo_a_carrito` |
| `cambiar_cantidad_pedido/<int:id_articulo>/<int:cantidad>/` | `cambiar_cantidad_pedido` | `cambiar_cantidad_pedido` |
| `crear_modificar_lista_pedidos/` | `crear_modificar_lista_pedidos` | `mi_vista_ajax` |
| `consultar_carrito/` | `consultar_carrito` | `consultar_carrito` |
| `usuarios_caja/` | `usuarios_caja` | `usuarios_caja` |
| `eliminar_articulo_pedido/` | `eliminar_articulo_pedido` | `eliminar_articulo_pedido` |
| `crear_modificar_lista_pedidos/<int:proveedor_id>` | `crear_modificar_lista_pedidos` | `mi_vista_ajax_get` |
| `imprimir/` | `Imprimir` | `imprimir` |
| `imprimir/tabla/` | `Imprimir` | `imprimir tabla` |
| `imprimir/carteles/1/` | `Imprimir` | `imprimir 1 cartel` |
| `listar_carteles/` | `ListarCarteles` | `listar_carteles` |
| `descargar_archivo/` | `descargar_archivo` | `descargar_archivo` |
| `agregar_articulo_a_pedido/<int:articulo_id>/` | `agregar_al_pedido` (from pedido) | `agregar_articulo_a_pedido` |

---

## 6. Admin (`bdd/admin.py`)

### `BaseModelAdmin`
Registro automático de TODOS los modelos de `bdd`:
- Auto-detecta campos (excluye `id`, relaciones reversas)
- `list_display` = todos los campos
- `search_fields` = todos los campos
- Para M2M: crea método `_display` que muestra los objetos relacionados
- Casos especiales:
  - `Armador`: oculta `modelo_campos`, `formulario_campos*` del list_display
  - `Item`: oculta `fecha` de fields y list_display
  - `Listado_Planillas`: oculta `fecha` de fields
- Actions dinámicas: si el modelo tiene `hay_csv_pendiente`, agrega actions "Marcar CSV pendiente" y "Alternar CSV pendiente"

### Registro automático
```python
model_classes = [cls for name, cls in inspect.getmembers(my_models)
                 if inspect.isclass(cls) and issubclass(cls, models.Model) and not cls._meta.abstract]
for model in model_classes:
    admin.site.register(model, BaseModelAdmin)
```

---

## 7. Clase `Patoba` (`bdd/classes.py`)

Integración con Google Drive, Gmail y Google Sheets usando OAuth2 de `django-allauth`.

### Constructor
- Obtiene `SocialToken` del usuario
- Crea credenciales OAuth2
- Inicializa servicios: `gmail`, `drive`, `sheets`
- Define `filtro_hojas_descarga`: hojas a excluir al copiar
- `id_carpeta_pedidos`: ID hardcodeado de carpeta de Drive

### Métodos principales

| Método | Descripción |
|--------|-------------|
| `subir_sqlite3_a_drive(ruta, nombre, carpeta_id)` | Sube/actualiza backup de BD en Drive |
| `descargar_sqlite3_de_drive(nombre, carpeta_id, ruta)` | Descarga backup de BD desde Drive |
| `crear_hoja_google_drive(nombre, datos, libro_id)` | Crea/actualiza Google Sheet con datos y formato |
| `filtrar_trabajados()` | Genera hojas por proveedor con items trabajados |
| `listar(cant, id_carpeta)` | Lista archivos en carpeta de Drive |
| `obtener_id_por_nombre(nombre, carpeta)` | Busca ID de archivo por nombre |
| `copiar_reemplazable(id_prov, hoja, id_dest, id_plantilla)` | Copia hoja de .xls a Google Sheet |
| `obtener_id_hoja_por_nombre(nombre, id_archivo)` | Obtiene ID de hoja por nombre |
| `copiar_hoja(id_hoja, id_origen, id_destino)` | Copia hoja entre spreadsheets |
| `eliminar_hoja(id_hoja, id_archivo)` | Elimina hoja de spreadsheet |
| `renombrar_hoja(id_hoja, id_archivo, nombre)` | Renombra hoja |
| `crear_buscar_copia_descarga(id_archivo, id_carpeta)` | Copia completa de spreadsheet excluyendo hojas filtradas |
| `download_and_zip_files(files_dict)` | Descarga múltiples archivos y los zipea como .xlsx |
| `actualizar_plantilla(spreadsheets, sp)` | Descarga planilla de Drive, procesa con pandas, genera .xlsx y .ods, actualiza `Listado_Planillas` |
| `borrar_por_id(id)` | Elimina archivo de Drive |
| `desaturar()` | `time.sleep(0.07)` para no exceder rate limit de API |

---

## 8. Template Tags (`bdd/templatetags/custom_filters.py`)

| Filtro | Descripción |
|--------|-------------|
| `zip_lists(a, b)` | Zipea dos listas |
| `to_float(value)` | Convierte a float, multiplica por 1.15, redondea a múltiplo de 10 si > 10 |
| `en_lista(value)` | Verifica si un código (formato `XXX/AB`) tiene sufijo en lista de proveedores conocidos |

---

## 9. Templates (en `static/templates/`)

### Template base: `generic_template.html`
Estructura:
1. **Head:** Bootstrap CSS, jQuery, widgets CSS, favicon SVG
2. **Body:**
   - `data-usuario="{{ user.get_username }}"` para JS
   - Carga diferida de QuaggaJS (escaner de código de barras)
   - **Navbar** (si no es `/imprimir/tabla/`):
     - Brand: `Ferreteria Paoli V-{{version}}`
     - Items dinámicos desde `barra_de_navegacion`
     - Badges para planillas nuevas y descargas
     - Login/logout
     - Link a `/change_log`
   - **Contenido:**
     - `tabla_lateral_carritos.html` (siempre incluido)
     - `{% include muro %}` (muro dinámico desde Armador)
     - `{% block content %}` (para vistas específicas)
   - **JS:** Notificaciones de MercadoPago

### Muros
- `muro_simple.html`: Incluye `lista_html.0` en un div
- `muro_doble.html`: Incluye `lista_html.0` y `lista_html.1` en dos divs
- `muro_imprimir.html`: Template para tabla de impresión

### Plantillas
- `plantilla_formulario.html`: Formulario dinámico + botones de carrito + tabla de pagos MP (comentada) + Select2 para sub_titulo
- `plantilla_tabla.html`: Tabla genérica

### Tablas
- `tabla_buscador.html` (401 líneas): Tabla principal del buscador con:
  - Columnas: Código, Descripción, Acciones
  - Botones: Ver (expandir precios), Al carrito, Editar (modal), Cartel, Agregar al pedido
  - Modal de edición (stock, barras, cajon, proveedor, sub_titulo, factor_division, tiene_cartel)
  - Modal de carrito (cantidad, selección de usuario caja)
  - JS completo para AJAX: editar_item, agregar_articulo_a_carrito, agregar_al_pedido
- `tabla_lateral_carritos.html` (1001 líneas): Panel lateral de carritos con:
  - Botones de carritos con badges de cantidad
  - Formulario de transacción (cliente, método de pago)
  - Modal de alta rápida de cliente
  - Formulario de artículo sin registro
  - Tabla de artículos con edición de cantidad y eliminar
  - Auto-update cada 3 segundos
  - Colores por usuario con contraste automático
  - Persistencia de cliente seleccionado por carrito
- `tabla_pedidos.html`: Tabla de pedidos
- `tabla_link_pedidos.html`: Links de pedidos
- `tabla_mp.html`: Tabla de MercadoPago
- `tabla_listado_carteles.html` / `tabla_listado_carteles_prueva.html`: Listado de carteles
- `tabla_registros.html`: Registros

### Otros templates
- `base_buscador.html`, `base_carrito.html`, `base_inicio.html`, etc.: Bases alternativas
- `imprimir_carteles_x6.html`: Template de impresión de carteles (6 por página)
- `imprimir_tabla.html`: Tabla para impresión
- `descargar_planillas.html`: Descarga de planillas
- `seleccionar_proveedor.html`: Selector de proveedor
- `mp.html`: MercadoPago
- `parrafo.html`: Párrafo simple

---

## 10. Flujo de Request Completo

### 10.1 Request a una página dinámica (ej: `/`)

```
Usuario → /core_config/urls.py → /bdd/urls.py
  → NavBar.objects.all() genera rutas dinámicas
  → Armador.objects.get(nav_bar=...) obtiene configuración
  → import_string("bdd.views.Inicio") carga la vista
  → Inicio.get_context_data()
    → MiVista.get_context_data()
      → Lee package.json → context["version"] = "3.10.0"
      → NavBar.objects.all() → context["barra_de_navegacion"]
      → Armador.objects.filter(url=ruta_actual).first()
        → context["muro"] = armador.muro.muro_html + ".html"
        → context["modelo"] = armador.modelo
        → MyForm(model_name=..., fields_to_show=...) → context["form"]
        → Contenedor → lista de plantillas → context["lista_html"]
      → Listado_Planillas counts → context["nuevas_planillas"]
      → MercadoPago (si está activo) → context["payments"], context["tabla_mp"]
  → render "generic_template.html"
    → Navbar con versión y items dinámicos
    → {% include "tabla_lateral_carritos.html" %}
    → {% include muro %} (ej: "muro_simple.html")
      → {% include lista_html.0 %} (ej: "plantilla_formulario.html")
        → Renderiza formulario con campos del Armador
    → {% block content %} (si la vista específica lo define)
```

### 10.2 Búsqueda de items (GET con parámetros)

```
Usuario → /?codigo=123&descripcion=tornillo
  → MiVista.get()
    → get_context_data() (como arriba)
    → armador.busqueda == True
    → Procesa request.GET:
      → Si campo en formulario_campos_contiene → __icontains
      → Si campo en formulario_campos_empieza_con → __istartswith
      → Si no → coincidencia exacta
    → model.objects.filter(**filter_kwargs)
    → Si modelo == "Item": annotate(tiene_pedido=Exists(Lista_Pedidos...))
    → context["datos"] = list(queryset.values(*titulos))
  → render "generic_template.html" con tabla de resultados
```

### 10.3 Agregar item al carrito (AJAX)

```
Usuario hace click en "Al carrito"
  → JS abre ModalCarrito
  → fetch('/usuarios_caja/') → obtiene cajeros disponibles
  → Usuario selecciona cantidad y cajero (si es caja_general)
  → POST /agregar_articulo_a_carrito/<id>/
    → Body: {cantidad: 1, usuario_caja: 2}
    → agregar_articulo_a_carrito()
      → Valida autenticación
      → Determina usuario objetivo (propio o seleccionado)
      → Carrito.objects.get_or_create(usuario=usuario_objetivo)
      → Articulo.objects.get_or_create(item=item, carrito=carrito)
      → Si no creado: articulo.cantidad += cantidad (con F())
      → Lista_Pedidos.objects.get_or_create(proveedor=item.proveedor, item=item)
    → Response: {status: "ok"}
  → JS cierra modal
  → Auto-update del carrito (cada 3 seg) refresca la tabla lateral
```

### 10.4 Consultar carritos (AJAX, polling)

```
JS (cada 3 seg) → GET /consultar_carrito/?usuario=Mati
  → consultar_carrito()
    → _is_caja_general(request.user)?
      → Sí: obtiene cajeros o filtra por ?usuario=
        → Por cada cajero: Carrito + Articulos + ArticuloSinRegistro
        → datos[username] = {articulos, articulos_sin_registro, carrito_id, color}
      → No: solo su carrito
    → calcular_total(datos) → agrega total y total_efectivo por carrito
  → Response: JSON con todos los carritos
  → JS actualiza:
    → Badges de botones de carrito
    → Tabla de artículos del carrito visible
    → Totales
    → Color de fondo según usuario
```

---

## 11. Sistema de Roles de Carrito

### Grupos de Django
- **`cajeros`**: Usuarios con carrito personal. Solo ven y operan su carrito.
- **`caja_general`**: Usuarios autorizados para ver y operar todos los carritos de cajeros.

### Reglas
- `_is_caja_general(user)`: True si `is_superuser` OR `username == "Caja"` OR grupo "caja_general"
- `_get_cajeros_queryset()`: Usuarios del grupo "cajeros" excluyendo "Caja"
- `consultar_carrito`: caja_general ve todos los cajeros; otros solo el propio
- `agregar_articulo_a_carrito`: caja_general puede agregar a carrito ajeno via `usuario_caja`

### Colores por usuario
- `_USER_COLOR_MAP`: Mapeo fijo (Mati=#FFD54F, Carlos=#4FC3F7)
- `_PALETTE`: 7 colores de fallback
- `_user_color(username)`: Usa mapa fijo o hash MD5 del username para determinar índice de paleta
- `getTextColorForBg(hex)`: Calcula luminancia W3C para determinar texto negro/blanco

---

## 12. Integración con Google (clase `Patoba`)

### Autenticación
- Usa `django-allauth` con `SocialToken`
- Scopes: Drive, Gmail (readonly, modify, compose)
- Crea credenciales OAuth2 y servicios de Drive, Gmail y Sheets

### Flujo de planillas
1. `actualizador` descarga planillas desde Gmail/Drive
2. `Patoba.crear_buscar_copia_descarga()` copia spreadsheets excluyendo hojas filtradas
3. `Patoba.actualizar_plantilla()` procesa con pandas y genera .xlsx y .ods
4. Actualiza `Listado_Planillas` con links de descarga
5. Usuario descarga desde la UI (navbar badge)

### Backup de BD
- `subir_sqlite3_a_drive()`: Sube/actualiza db.sqlite3 a Drive
- `descargar_sqlite3_de_drive()`: Descarga backup desde Drive

---

## 13. Dependencias

### Dependencias internas (otras apps)
- `core_andamios`: `Nav_Bar`, `ContextoAndamio`, context processor
- `x_cartel`: `CartelesCajon`, `Carteles` (usado en `ListarCarteles`)
- `pedido`: `agregar_al_pedido` (importado en urls.py)
- `facturacion`: importa `Inicio` de `bdd.views.main` (y de `views_old` - ver sección 14)

### Dependencias externas
- `django-allauth` (SocialToken para Google OAuth)
- `google-api-python-client` (Drive, Gmail, Sheets)
- `pandas` (procesamiento de planillas)
- `mercadopago` (SDK de MercadoPago)
- `requests` (descarga de planillas)
- `openpyxl` / `xlsxwriter` / `odf` (escritura de Excel/ODS)

### Settings relevantes
- `INTEGRATE_MERCADOPAGO` (bool): Activa integración MP
- `INTERNET` (bool): Hay conexión a internet
- `MP_TOKEN_FILE`: Ruta al token de MP
- `TABLA_LINK_PEDIDOS`: Links de pedidos para el contexto
- `ESTADOS_REPORTE_ITEM`: Estados para reporte de items
- `APPS_TO_LOG`: Apps para logging (usado por core_config)

---

## 14. Código Legacy: `views_old.py` (1230 líneas)

### Estado
`views_old.py` contiene duplicados de TODAS las vistas que ya están en `views/`. Es código legacy que debería eliminarse.

### Imports activos desde `views_old`
- `bdd/urls.py:5` - importa `Imprimir`, `ItemsView` (debería ser de `views.main`)
- `bdd/urls.py:23` - importa `ListarCarteles` (debería ser de `views.main`)
- `facturacion/views.py:5` - importa `Inicio` (sobrescrito en línea 6 por `views.main`)

### Riesgo
- Confusión sobre qué versión de la vista se ejecuta
- Las vistas en `views_old` NO tienen el sistema de logging ni manejo de errores de las vistas nuevas
- Los imports de `urls.py` desde `views_old` significan que `Imprimir`, `ItemsView` y `ListarCarteles` ejecutan código legacy

### Recomendación
1. Cambiar imports de `bdd/urls.py` de `views_old` a `views.main`
2. Eliminar import de `facturacion/views.py:5` (ya sobrescrito)
3. Eliminar `views_old.py`

---

## 15. Bugs Conocidos (sin fix, solo documentación)

| Archivo | Línea | Bug | Impacto |
|---------|-------|-----|---------|
| `models.py:316` | `calcular_precio_final()` | Referencia `self.constante` (campo inexistente) | RuntimeError si se llama |
| `models.py:332` | `calcular_precio_efectivo_final()` | Referencia `self.constante` | RuntimeError si se llama |
| `models.py:320` | `calcular_precio_rollo_final()` | Referencia `self.venta_metro` (campo inexistente) | RuntimeError si se llama |
| `models.py:92` | `Condiciones.detectar_columna()` | Referencia `self.descripcion` (campo inexistente) | RuntimeError si se llama |
| `models.py:101` | `Condiciones.ordenar_columnas()` | Referencia `self.descripcion` | RuntimeError si se llama |
| `models.py:142` | `Archivo.descargar()` | Referencia `self.descarga` (campo inexistente) | RuntimeError si se llama |
| `models.py:148` | `Archivo.basename()` | Referencia `self.descarga` | RuntimeError si se llama |
| `models.py:53` | `Paginas.__str__` | Referencia `self.html` (campo inexistente) | Error en admin/templates |
| `models.py:565` | `Registros.automatioco` | Typo: debería ser `automatico` | Inconsistencia en DB |

**Nota:** Los métodos `calcular_precio_*` parecen no ser llamados en producción (el actualizador usa `recompute_finales()` en su lugar), pero son código muerto con bugs.

---

## 16. Puntos de Extensión

### Nueva vista dinámica
1. Crear vista en `bdd/views/main.py` heredando de `MiVista`
2. Crear entrada en `NavBar` (url_inicial, text_display)
3. Crear entrada en `Armador` (nav_bar, vista, url, muro, contenedor, modelo, etc.)
4. La URL se genera automáticamente en `urls.py`

### Nuevo endpoint AJAX
1. Crear función en `bdd/views/ajax.py`
2. Agregar URL en `bdd/urls.py`
3. Agregar import en `bdd/views/__init__.py`

### Nuevo modelo
1. Definir en `bdd/models.py`
2. Se registra automáticamente en admin (gracias a `inspect.getmembers`)
3. Si necesita vista: crear entrada en `Armador`

### Nuevo filtro de template
1. Agregar en `bdd/templatetags/custom_filters.py`
2. Usar en templates con `{% load custom_filters %}`
