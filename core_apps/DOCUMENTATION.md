# Apps Core - Documentación Exhaustiva

**Versión documentada:** v3.10.0
**Fecha:** 2026-07-13

---

## Índice

1. [core_config](#1-core_config)
2. [core_andamios](#2-core_andamios)
3. [core_docs](#3-core_docs)
4. [core_index](#4-core_index)
5. [core_elementos](#5-core_elementos)
6. [core_testing](#6-core_testing)
7. [Relación entre apps core](#7-relación-entre-apps-core)

---

## 1. core_config

### 1.1 Propósito

`core_config` es la app de configuración principal del proyecto Django. Contiene:
- `settings.py` (gitignored - no versionado)
- URLs raíz que incluyen todas las apps
- Configuración de logging (generador dinámico + middleware)
- Vista de descarga de logs para staff
- Puntos de entrada ASGI/WSGI
- Configuración legacy de Celery (no usado)

### 1.2 Estructura

```
core_config/
├── __init__.py
├── asgi.py                 (17 líneas)  - Punto de entrada ASGI
├── wsgi.py                 (17 líneas)  - Punto de entrada WSGI
├── celery.py               (13 líneas)  - Configuración Celery (LEGACY - no usado)
├── settings.py             (gitignored) - Configuración Django
├── log_config.py           (76 líneas)  - Generador de config de logging por app
├── exception_logging.py    (34 líneas)  - Middleware: captura excepciones no manejadas
├── request_logging.py      (42 líneas)  - Middleware + filtro: request_id, user, IP
├── urls.py                 (62 líneas)  - URL raíz: incluye todas las apps
├── views/
│   └── logs.py             (188 líneas) - Vista staff para descarga de logs
├── templates/
│   └── core_config/
│       └── logs_download.html (28 líneas)
├── api/v4/                 (vacío)
└── tests/                  (vacío)
```

### 1.3 URLs (`urls.py`)

Incluye todas las apps del proyecto:

```python
urlpatterns = [
    path("", include("carga_archivo.urls")),
    path("", include("facturacion.urls")),
    path("", include("boletas.urls")),
    path("pedidos/", include("pedido.urls")),
    path("", include("x_cartel.urls")),
    path("", include("x_articulos.urls")),
    path("", include("bdd.urls")),
    path("", include("core_docs.urls")),
    path("", include("core_index.urls")),
    path("", include("actualizador.urls")),
    path("", include("reportes.urls")),
    path("administracion_financiera/", include("administracion_financiera.urls")),
    path("", RedirectView.as_view(url="/bienbenida/"), name="index"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("_admin/logs/download/", logs_views.download_logs, name="download_logs"),
]

urlpatterns += [
    path("accounts/", include("allauth.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]

urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]
```

**Notas:**
- La mayoría de apps se montan en la raíz (`""`)
- `pedido` se monta en `/pedidos/`
- `administracion_financiera` se monta en `/administracion_financiera/`
- Redirección raíz → `/bienbenida/` (core_index)
- Autenticación: `allauth` + `django.contrib.auth`
- Media y static servidos en desarrollo

### 1.4 Logging

#### `log_config.py` - `generate_app_logging_config()`

Genera configuración de handlers y loggers para una lista de apps:

**Parámetros:**
- `apps`: lista de nombres de apps
- `base_log_dir`: directorio base de logs
- `base_formatter`: nombre del formatter (default: "verbose")
- `max_bytes`: tamaño máximo por archivo (default: 5MB)
- `backup_count`: cantidad de backups (default: 5)
- `level_info`, `level_error`: niveles para cada handler

**Por cada app genera:**
- Handler INFO: `logs/<app>/info.log` (RotatingFileHandler)
- Handler ERROR: `logs/<app>/error.log` (RotatingFileHandler)
- Logger: nivel DEBUG, propagate=True, con ambos handlers + console_errors

**Crea directorios automáticamente** con `os.makedirs(exist_ok=True)`.

#### `request_logging.py`

**`RequestIDMiddleware`:**
- Asigna `request.request_id = str(uuid.uuid4())` a cada request
- Guarda el request en thread-local para acceso desde el filter
- Limpia thread-local en `finally`

**`RequestContextFilter`:**
- Filtro de logging que agrega a cada record:
  - `request_id`: UUID del request (o "-")
  - `user`: username si está autenticado (o "anon")
  - `ip`: IP del cliente (HTTP_X_FORWARDED_FOR o REMOTE_ADDR)

#### `exception_logging.py` - `ExceptionLoggingMiddleware`

- Captura excepciones no manejadas en vistas
- Registra con `logger.exception()` usando el módulo de la vista como nombre de logger
- **Re-lanza la excepción** (no altera la respuesta)
- Obtiene el módulo desde `request.resolver_match.func.__module__`

### 1.5 Vista de descarga de logs (`views/logs.py`)

#### `LogDownloadForm`
- `apps`: MultipleChoiceField (choices desde `settings.APPS_TO_LOG`)
- `from_date`, `to_date`: DateTimeField (widget datetime-local)
- `include_rotated`: BooleanField (incluir logs rotados)
- `include_info`, `include_error`: BooleanField
- `max_size_mb`: IntegerField (1-500, default 100)

#### `download_logs(request)`
- **Decorador:** `@staff_member_required`
- **Feature flag:** `settings.ENABLE_LOG_DOWNLOAD` (default: False → 404)
- **GET:** Muestra formulario con defaults (últimas 24h)
- **POST:**
  1. Valida formulario
  2. Filtra archivos por rango de fechas (mtime)
  3. Valida path traversal (compara `resolve()` con `logs_root`)
  4. Crea ZIP temporal con límite de tamaño
  5. Archivos que exceden el límite se listan en `_SKIPPED.txt`
  6. Limpieza del temporal al cerrar la respuesta
  7. Devuelve `FileResponse` con el ZIP

**URL:** `_admin/logs/download/`

### 1.6 Templates

#### `logs_download.html`
Template HTML minimalista (sin Bootstrap) con:
- Formulario con campos: apps (checkboxes), from_date, to_date, include_info, include_error, include_rotated, max_size_mb
- Mensaje de error/info si lo hay

### 1.7 Settings relevantes (desde README y código)

| Setting | Tipo | Default | Descripción |
|---------|------|---------|-------------|
| `LOG_DIR` | str | "logs" | Directorio base de logs |
| `LOG_MAX_BYTES` | int | 3145728 (3MB) | Tamaño máximo por archivo |
| `LOG_BACKUP_COUNT` | int | 5 | Cantidad de backups |
| `LOG_LEVEL` / `MAIN_LOG_LEVEL` | str | "INFO" | Nivel del log raíz |
| `ACT_LOG_LEVEL` | str | "INFO" | Nivel app actualizador |
| `BDD_LOG_LEVEL` | str | "INFO" | Nivel app bdd |
| `X_CARTEL_LOG_LEVEL` | str | "INFO" | Nivel app x_cartel |
| `APPS_TO_LOG` | list | - | Apps para logging y descarga |
| `ENABLE_LOG_DOWNLOAD` | bool | False | Activa vista de descarga |
| `INTEGRATE_MERCADOPAGO` | bool | False | Activa integración MP |
| `INTERNET` | bool | False | Hay conexión a internet |
| `MP_TOKEN_FILE` | str | "./mp_access_token.txt" | Ruta al token de MP |
| `TABLA_LINK_PEDIDOS` | list | [] | Links de pedidos |
| `ACT_CSV_BATCH_SIZE` | int | 1000 | Tamaño de lote CSV |
| `ACT_CSV_EFECTIVO_DESCUENTO_PCT` | float | 0.0 | % descuento efectivo CSV |

### 1.8 Celery (LEGACY)

`celery.py` configura Celery pero **no se usa**. El sistema usa hilos nativos (ver CHANGELOG v3.4.0: "Se elimina el soporte a celery. Se inicia el soporte a hilos nativos").

### 1.9 api/v4 (vacío)

Directorio `api/v4/` existe pero está vacío (sin archivos .py). Era probablemente una API planificada.

---

## 2. core_andamios

### 2.1 Propósito

`core_andamios` define la estructura base de las páginas: navbar, contenedor, pie y head. Proporciona:
- Modelos de andamio (`Nav_Bar`, `Contenedor`, `Script`, `Pie`, `Url`)
- Context processor global (navbar para todas las vistas)
- Vista base `ContextoAndamio` (usada por `core_index`)
- Templates de andamio (head, navbar, contenedor, pie)

### 2.2 Estructura

```
core_andamios/
├── __init__.py
├── apps.py                 (6 líneas)   - AndamiosConfig
├── models.py               (42 líneas)  - 7 modelos
├── views.py                (25 líneas)  - ContextoAndamio
├── context_processors.py   (13 líneas)  - mi_procesador_de_contexto
├── admin.py                (61 líneas)  - Registro automático
├── templates/core_andamios/
│   ├── core_andamio.html   (27 líneas)  - Template base con blocks
│   ├── core_head.html      (36 líneas)  - Head con Bootstrap, meta tags
│   ├── core_navbar.html    (31 líneas)  - Navbar con items dinámicos
│   ├── core_contenedor.html (9 líneas)  - Block contenedor
│   └── core_pie.html       (47 líneas)  - Footer con datos de contacto
└── docs/core_andamios/
    └── index.md            (19 líneas)  - Doc aislada (DESACTUALIZADA)
```

### 2.3 Modelos (`models.py`)

#### `ModeloBase` (abstract)
- `nombre` - CharField(30)
- `text_display` - CharField(30)
- `__str__` devuelve `text_display`

#### `Contenedor(ModeloBase)`
- `html` - CharField(250) (template HTML del contenedor)

#### `Script(ModeloBase)`
- `html` - CharField(250) (JavaScript)

#### `Pie(ModeloBase)`
- `html` - CharField(250) (template HTML del pie)

#### `Url(ModeloBase)`
- `ruta` - CharField(250)
- `contenedor` - FK→`Contenedor`
- `script` - FK→`Script`
- `pie` - FK→`Pie`

#### `Nav_Bar(ModeloBase)`
- `url` - OneToOne→`Url`

#### `Contexto`
- `json` - JSONField (almacena contexto adicional)

**Nota:** Estos modelos son DIFERENTES de los de `bdd.models` (`NavBar`, `Muro`, `Plantilla`, `Contenedor`, `Armador`). Los de `core_andamios` definen la estructura HTML fija, los de `bdd` definen la construcción dinámica.

### 2.4 Context Processor (`context_processors.py`)

```python
def mi_procesador_de_contexto(request):
    contexto = {}
    contexto["barra_de_navegacion"] = Nav_Bar.objects.all()
    contexto["core_navbar_html"] = "core_andamios/core_navbar.html"
    contexto["core_contenedor_html"] = "core_andamios/core_contenedor.html"
    contexto["core_pie_html"] = "core_andamios/core_pie.html"
    contexto["core_head_html"] = "core_andamios/core_head.html"
    return contexto
```

**Importante:** Este context processor está registrado en `settings.TEMPLATES['OPTIONS']['context_processors']` y se ejecuta para TODAS las vistas. Agrega:
- `barra_de_navegacion`: QuerySet de `Nav_Bar` (de core_andamios, NO de bdd)
- `core_navbar_html`, `core_contenedor_html`, `core_pie_html`, `core_head_html`: nombres de templates

**Conflicto potencial:** `bdd.views.base.MiVista` también setea `context["barra_de_navegacion"]` pero con `bdd.models.NavBar.objects.all()`. Como el context processor se ejecuta antes que `get_context_data()`, el de `bdd` sobrescribe al de `core_andamios`.

### 2.5 Vista (`views.py`)

#### `ContextoAndamio(TemplateView)`
Vista base minimalista para páginas que usan andamios:

```python
class ContextoAndamio(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Index"
        context["core_andamio_id"] = 1
        context["hay_navbar_html"] = True
        context["hay_contenedor_html"] = True
        context["hay_pie_html"] = True
        return context
```

Usada por `core_index.Vista_Index`.

### 2.6 Templates

#### `core_andamio.html` - Template base
```html
<html lang="es">
<head>{% include core_head_html %}</head>
<body class="d-flex flex-column">
    <script src="bootstrap.bundle.min.js"></script>
    {% if hay_navbar_html %}{% include core_navbar_html %}{% endif %}
    {% if hay_contenedor_html %}{% block contenedor %}{% endblock %}{% endif %}
    {% if hay_pie_html %}{% include core_pie_html %}{% endif %}
</body>
</html>
```

#### `core_head.html` - Head
- Meta tags: charset, viewport
- Bootstrap 5.2.3 CSS (CDN)
- `admin/css/widgets.css`
- `admin:jsi18n` URL
- CSS inline: `.card-row`, `.contenedor`, `.precio` con responsive

#### `core_navbar.html` - Navbar
- Brand: "Ferreteria Paoli"
- Items desde `barra_de_navegacion` (context processor)
- Badge para planillas nuevas (si `nav.text_display == 'Actualizar'`)
- Login/logout
- **Nota:** Usa `nav.url.ruta` (modelo `core_andamios.Nav_Bar`) a diferencia de `generic_template.html` que usa `nav.url_inicial` (modelo `bdd.NavBar`)

#### `core_contenedor.html` - Block contenedor
Solo define `{% block contenedor %}` con un `<h1>Contenedor</h1>` placeholder.

#### `core_pie.html` - Footer
- Información de contacto: Calle 57 nº811, La Plata
- Email: pyfpaoli@yahoo.com.ar
- Tel: +54 9 221 314 3160
- Copyright: "© 2023 Desarrollado por: DarkyDieL"

### 2.7 Admin (`admin.py`)

Registro automático de todos los modelos (similar a `bdd/admin.py`):
- `BaseModelAdmin` con auto-detección de campos
- Excluye `id` y relaciones reversas
- `list_display` = todos los campos
- `search_fields` = todos los campos
- Para M2M: crea método `_display`

### 2.8 Documentación existente (DESACTUALIZADA)

`core_andamios/docs/core_andamios/index.md` (19 líneas):
- Describe context vars incorrectas: `core_navbar`, `core_contenedor`, `core_script`, `core_pie`
- Las reales son: `core_navbar_html`, `core_contenedor_html`, `core_head_html`, `core_pie_html`
- Dice "El contexto se define en views.py bajo la clase ContextoAndamio" - correcto pero incompleto
- No menciona el context processor

---

## 3. core_docs

### 3.1 Propósito

`core_docs` gestiona:
1. La documentación técnica generada con Sphinx (serve_docs)
2. La vista del registro de cambios (changeLog)

### 3.2 Estructura

```
core_docs/
├── __init__.py
├── apps.py
├── admin.py
├── models.py              (vacío - sin modelos)
├── urls.py                (8 líneas)
├── views.py               (49 líneas)
├── templates/
│   └── change_log.html    (118 líneas) - Renderiza CHANGELOG.md
└── docs/                  (Sphinx)
    ├── conf.py            (53 líneas)
    ├── index.md           (28 líneas)
    ├── instalacion.md     (5 líneas)
    ├── sintaxis.md        (35 líneas)
    ├── documentacion_codigo_fuente.md (18 líneas)
    ├── core.md            (48 líneas)
    ├── apps.md            (8 líneas)
    ├── core_andamios/
    │   └── core_andamios_index.md (7 líneas)
    └── _build/html/       (HTML generado por Sphinx)
```

### 3.3 URLs (`urls.py`)

```python
urlpatterns = [
    re_path(r"^docs/(?P<path>.*)$", serve_docs),
    path("change_log/", changeLog, name="change-log"),
]
```

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/docs/<path>` | `serve_docs` | Sirve HTML generado por Sphinx |
| `/change_log/` | `changeLog` | Renderiza CHANGELOG.md como HTML |

### 3.4 Vistas (`views.py`)

#### `serve_docs(request, path)`
- Sirve archivos HTML desde `core_docs/docs/_build/html/`
- Si el archivo no existe, redirige a `index.html`
- Es un serve estático sobre el output de Sphinx

#### `changeLog(request)`
- Lee `CHANGELOG.md` desde `settings.BASE_DIR`
- Convierte Markdown a HTML con `markdown2.markdown()`
- Codifica emojis con `emojis.encode()`
- Renderiza `change_log.html` con `{"changelog": change_log}`

### 3.5 Template `change_log.html`

Template estilizado (118 líneas) con:
- Bootstrap 5.2.3 (CDN)
- Bootstrap Icons
- Header con gradiente azul-morado
- Container max-width 900px
- Renderiza `{{ changelog|safe }}` (HTML ya convertido desde Markdown)

### 3.6 Sphinx (`docs/conf.py`)

**Configuración:**
- Proyecto: "Ferreteria"
- Autor: "DarkyDielJob"
- Release: "v2.0" (**DESACTUALIZADO** - actual: v3.10.0)
- Extensiones: `myst_parser`, `sphinx.ext.autodoc`
- Tema: `furo`
- Idioma: `es`
- `master_doc = "index"` (index.md)
- MyST extensions: dollarmath, amsmath, deflist, html_admonition, html_image, colon_fence, smartquotes, replacements, substitution

**Estado de la documentación Sphinx:** TODOS los archivos .md son stubs vacíos o desactualizados (ver auditoría para detalle).

### 3.7 Dependencias

- `markdown2` - Conversión Markdown → HTML
- `emojis` - Codificación de emojis (`:emoji_name:` → unicode)
- `sphinx` - Generación de documentación
- `myst_parser` - Soporte Markdown en Sphinx
- `furo` - Tema de Sphinx

---

## 4. core_index

### 4.1 Propósito

`core_index` es la app de bienvenida. Muestra una página de inicio simple con links al sistema.

### 4.2 Estructura

```
core_index/
├── __init__.py
├── apps.py                (6 líneas)
├── admin.py               (vacío)
├── models.py              (vacío - sin modelos)
├── urls.py                (7 líneas)
├── views.py               (17 líneas)
└── templates/core_index/
    └── index.html         (14 líneas)
```

### 4.3 URL

```python
path("bienbenida/", Vista_Index.as_view(), name="index")
```

**Nota:** La URL raíz (`/`) redirige a `/bienbenida/` (configurado en `core_config/urls.py`).

### 4.4 Vista (`views.py`)

#### `Vista_Index(ContextoAndamio)`
Hereda de `core_andamios.views.ContextoAndamio`:

```python
class Vista_Index(ContextoAndamio):
    template_name = "core_index/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contenido_1"] = "core_elementos/core_formulario.html"
        context["elemento_parrafo"] = "core_elementos/core_parrafo.html"
        context["parrafo"] = "Un parrafo"
        return context
```

### 4.5 Template `index.html`

```html
{% extends 'core_andamios/core_andamio.html' %}

{% block contenedor %}
    <h1>{{ titulo }}</h1>
    <a href="../buscador/">Sistema viejo!</a>
    {% include contenido_1 %}
    {% include elemento_parrafo %}
    <a href="../x_cartel/">Carteles</a>
{% endblock %}
```

- Hereda de `core_andamio.html` (andamio completo: head, navbar, pie)
- Incluye `core_formulario.html` (que solo dice "FORMULARIO AS P" - placeholder)
- Incluye `core_parrafo.html` (que muestra `{{ parrafo }}` = "Un parrafo")
- Links: "Sistema viejo!" → `/buscador/`, "Carteles" → `/x_cartel/`

**Estado:** Página de bienvenida minimalista, probablemente placeholder.

---

## 5. core_elementos

### 5.1 Propósito

`core_elementos` define elementos reutilizables para los andamios: tablas, formularios, modales, tarjetas, listas y párrafos. Es una biblioteca de componentes HTML.

### 5.2 Estructura

```
core_elementos/
├── __init__.py
├── apps.py                (6 líneas)
├── admin.py               (61 líneas)  - Registro automático
├── models.py              (56 líneas)  - 6 modelos
├── views.py               (80 líneas)  - Vista Crud
├── templatetags/
│   ├── __init__.py
│   └── filtro.py          (14 líneas)  - Filtro get_attr
├── templates/core_elementos/
│   ├── core_tabla.html    (36 líneas)  - Tabla simple
│   ├── core_tabla_crud.html (59 líneas) - Tabla con CRUD + modal
│   ├── core_formulario.html (3 líneas)  - Placeholder
│   ├── core_modal.html    (19 líneas)  - Modal de edición
│   ├── core_tarjeta.html  (3 líneas)   - Placeholder
│   ├── core_lista.html    (3 líneas)   - Placeholder
│   └── core_parrafo.html  (3 líneas)   - Párrafo simple
└── static/core_elementos/js/
    ├── core_tabla.js      - JS para tabla simple
    └── core_tabla_crud.js (156 líneas) - JS para tabla CRUD
```

### 5.3 Modelos (`models.py`)

#### `Modelo_Base` (abstract)
- `nombre` - CharField(30)
- `elemento_html` - CharField(30) (template del elemento)

#### `Modelo_Tablas(Modelo_Base)`
- `lista_de_titulos` - TextField(300)
- `lista_articulos` - TextField(300)

#### `Modelo_Formularios(Modelo_Base)`
- `lista_de_campos` - TextField(300)

#### `Modelo_Tarjetas(Modelo_Base)`
- `titulo` - CharField(30)
- `descripcion` - CharField(30)

#### `Modelo_Listas(Modelo_Base)`
- (sin campos adicionales)

#### `Paginas`
- `tiene_tabla` - BooleanField
- `modelo_tablas` - M2M→`Modelo_Tablas`
- `tiene_formulario` - BooleanField
- `modelo_formularios` - M2M→`Modelo_Formularios`
- `tiene_tarjeta` - BooleanField
- `modelo_tarjetas` - M2M→`Modelo_Tarjetas`
- `tiene_lista` - BooleanField
- `modelo_lista` - M2M→`Modelo_Listas`

**BUG:** `Paginas.__str__` referencia `self.html` que no existe como campo.

### 5.4 Vista (`views.py`)

#### `Crud(TemplateView)`
- **Template:** `x_articulos/crud.html`
- Vista CRUD para `x_articulos.models.Articulo`
- `get_context_data()`: Obtiene todos los artículos, omite campos `ultimo_cambio`, `actualizado`, `id`
- Define `lista_titulos = ["codigo", "descripcion"]`
- Incluye `core_tabla_crud.html` y `core_modal.html`
- `post()`: Procesa `ArticuloForm`, actualiza el artículo, devuelve JSON

**Nota:** Esta vista está acoplada a `x_articulos` a pesar de estar en `core_elementos`. Debería estar en `x_articulos/views.py`.

### 5.5 Template Tags (`templatetags/filtro.py`)

#### `get_attr(objeto, nombre_atributo)`
- Si `objeto` es dict: `objeto.get(nombre_atributo)`
- Si no: `getattr(objeto, nombre_atributo, None)`

Usado en `core_tabla_crud.html` para acceder a campos dinámicos: `{{ dato|get_attr:titulo }}`

### 5.6 Templates

#### `core_tabla.html` - Tabla simple
- Columnas: Código, Descripción
- Filas con `data-*` attributes para todos los campos del item
- Incluye `core_tabla.js`
- Incluye modal si `hay_modal_html`

#### `core_tabla_crud.html` - Tabla con CRUD
- Usa `{% load filtro %}` para acceso dinámico a campos
- Columnas dinámicas desde `lista_titulos`
- `data-*` attributes generados dinámicamente
- Incluye `core_tabla_crud.js`
- Modal de edición con `{{ form|crispy }}` (requiere `crispy_forms`)
- POST a `/articulos/` para guardar cambios

#### `core_modal.html` - Modal de edición
- Modal Bootstrap con formulario
- Campo oculto `id_codigo`
- `{{ form.as_p }}` para renderizar campos

#### `core_formulario.html` - Placeholder
Solo contiene `<h1>FORMULARIO AS P</h1>` (no implementado)

#### `core_tarjeta.html` - Placeholder
Solo contiene `<h1>TARJETA T1</h1>` (no implementado)

#### `core_lista.html` - Placeholder
Solo contiene `<h1>LITA DE ITEMS</h1>` (no implementado)

#### `core_parrafo.html` - Párrafo
Muestra `{{ parrafo }}` en un `<p>`

### 5.7 JavaScript

#### `core_tabla_crud.js` (156 líneas)
- Crea modal dinámico al hacer click en fila
- Expande fila con precios (campos `data-*` que no están en `lista_titulos`)
- Click en fila expandida abre modal de edición
- Carga datos del formulario desde `data-*` attributes
- Submit del formulario via fetch y via jQuery AJAX (doble implementación)
- Actualiza la tabla con la respuesta
- Escape cierra el modal

### 5.8 Admin (`admin.py`)

Registro automático de modelos (similar a otras apps core):
- `BaseModelAdmin` con auto-detección de campos
- Casos especiales para `Formulario_Campos` y `Modelo_Campos` (oculta `armador`)

---

## 6. core_testing

### 6.1 Propósito

`core_testing` fue diseñada para albergar interfaces de testing, fixtures y utilidades de prueba. Actualmente está **completamente vacía**.

### 6.2 Estructura

```
core_testing/
├── .pytest_cache/
├── __pycache__/
├── fixtures/              (vacío)
├── management/commands/   (vacío)
├── migrations/
│   ├── __init__.py
│   └── 0001_initial.py    (migración vacía - sin modelos)
├── templatetags/          (vacío)
├── testing_interfaces/    (vacío)
├── tests/                 (vacío)
├── utils/                 (vacío)
└── views/                 (vacío)
```

### 6.3 Estado

- **Sin modelos** (`models.py` no existe)
- **Sin vistas** (`views/` vacío)
- **Sin URLs** (no incluida en `core_config/urls.py`)
- **Sin tests** (`tests/` vacío)
- **Sin management commands** (`management/commands/` vacío)
- Solo tiene `migrations/0001_initial.py` (migración vacía)

**Conclusión:** App abandonada/incompleta. Se creó la estructura de directorios pero nunca se llenó con código.

---

## 7. Relación entre apps core

### 7.1 Flujo de renderizado con andamios

```
core_config/urls.py
  → Redirección / → /bienbenida/
  → core_index/urls.py: /bienbenida/ → Vista_Index

Vista_Index (core_index)
  → Hereda de ContextoAndamio (core_andamios)
  → Template: core_index/index.html
    → {% extends 'core_andamios/core_andamio.html' %}
      → {% include core_head_html %}    (core_andamios/core_head.html)
      → {% include core_navbar_html %}  (core_andamios/core_navbar.html)
      → {% block contenedor %}          (definido en core_index/index.html)
        → {% include contenido_1 %}     (core_elementos/core_formulario.html)
        → {% include elemento_parrafo %}(core_elementos/core_parrafo.html)
      → {% include core_pie_html %}     (core_andamios/core_pie.html)
```

### 7.2 Flujo de renderizado con bdd (sistema principal)

```
core_config/urls.py
  → bdd/urls.py: rutas dinámicas desde Armador
  → MiVista (bdd/views/base.py)
    → Template: generic_template.html (static/templates/)
    → NO usa core_andamio.html (tiene su propio template)
    → Context processor de core_andamios agrega barra_de_navegacion
    → MiVista sobrescribe barra_de_navegacion con bdd.models.NavBar
    → Navbar propio con versión, badges de planillas, login/logout
```

### 7.3 Dos sistemas de andamios paralelos

| Aspecto | core_andamios | bdd (Armador) |
|---------|---------------|---------------|
| Template base | `core_andamio.html` | `generic_template.html` |
| Navbar | `core_navbar.html` | Inline en `generic_template.html` |
| Modelos de nav | `Nav_Bar` (con `url.ruta`) | `NavBar` (con `url_inicial`) |
| Context vars | `core_navbar_html`, etc. | `muro`, `lista_html`, `form` |
| Vista base | `ContextoAndamio` | `MiVista` |
| Dinamismo | Estático (DB-driven simple) | Dinámico (Armador configura todo) |
| Usado por | `core_index` | Todo el resto del sistema |

**Conclusión:** `core_andamios` fue el sistema original de andamios, pero `bdd` con su sistema de `Armador` lo reemplazó en la práctica. `core_andamios` solo se usa para la página de bienvenida (`core_index`).

### 7.4 Context processor vs get_context_data

El context processor de `core_andamios` se ejecuta para TODAS las vistas (incluidas las de `bdd`), pero `MiVista.get_context_data()` sobrescribe `barra_de_navegacion` con `bdd.models.NavBar`. Las variables `core_navbar_html`, `core_contenedor_html`, `core_pie_html`, `core_head_html` están disponibles en todos los templates pero solo se usan en `core_andamio.html` (que solo usa `core_index`).

### 7.5 core_elementos: uso real vs planeado

| Elemento | Estado | Usado por |
|----------|--------|-----------|
| `core_tabla.html` | Funcional | Templates antiguos |
| `core_tabla_crud.html` | Funcional | `core_elementos/views.py:Crud` |
| `core_modal.html` | Funcional | `core_tabla.html` |
| `core_parrafo.html` | Funcional | `core_index/index.html` |
| `core_formulario.html` | Placeholder | `core_index/index.html` |
| `core_tarjeta.html` | Placeholder | No usado |
| `core_lista.html` | Placeholder | No usado |

### 7.6 core_docs: integración

- `/change_log/` es accesible desde el navbar de `generic_template.html` (link "Registro de cambios")
- `/docs/` sirve la documentación Sphinx (actualmente stubs vacíos)
- `conf.py` dice `release = "v2.0"` (debería ser v3.10.0)

### 7.7 core_config: rol de orquestador

`core_config` no es una app de negocio, es la configuración del proyecto:
- `settings.py` define todas las apps instaladas, middleware, logging, etc.
- `urls.py` incluye todas las apps y define rutas de admin/auth/media
- Middleware: `RequestIDMiddleware` + `ExceptionLoggingMiddleware`
- Logging: `log_config.py` genera config dinámica por app
- Vista de logs: solo para staff, con feature flag

### 7.8 Dependencias entre apps core

```
core_config (settings, urls, logging)
  ├── core_andamios (andamios, context processor)
  │   ├── core_index (página de bienvenida)
  │   └── core_elementos (elementos reutilizables)
  ├── core_docs (documentación Sphinx + changelog)
  └── core_testing (vacío - abandonada)
```

`core_config` incluye todas las apps en sus URLs, pero las apps core dependen entre sí:
- `core_index` depende de `core_andamios` (hereda `ContextoAndamio`)
- `core_index` depende de `core_elementos` (incluye sus templates)
- `core_elementos` depende de `x_articulos` (vista `Crud` usa `Articulo` y `ArticuloForm`)
- `core_andamios` no depende de otras apps core (solo de `bdd` indirectamente via context processor)
- `core_docs` no depende de otras apps core
- `core_testing` no depende de nada (está vacía)
