# Configuración de la Documentación

## Configuración Inicial

### 1. Dependencias Python

```bash
pip install sphinx myst-parser django-sphinx-theme
```

### 2. Estructura del Proyecto

```bash
mkdir -p core_docs/docs
```

### 3. Iniciar Proyecto Sphinx

```bash
cd core_docs/docs
sphinx-quickstart
```

Durante la configuración:
- Use `yes` para todo
- Use `markdown` como formato de fuente
- Use `html` como formato de salida

### 4. Configurar conf.py

```python
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath('../../'))
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'
django.setup()

extensions = [
    'myst_parser',
    'sphinx.ext.autodoc'
]

myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "html_image",
    "smartquotes",
    "html_admonition",
    "deflist",
    "replacements",
    "colon_fence"
]
```

## Estructura de la Documentación

La documentación se organiza en archivos Markdown (.md) en el directorio `core_docs/docs/`. La estructura es:

- `index.md`: Página principal de la documentación
- `documentacion.md`: Configuración y guía de uso
- `conf.py`: Configuración de Sphinx
- `Makefile`: Scripts de construcción
- `source` y `_build`: Directorios generados por Sphinx
- `_static`: Directorio para archivos estáticos

### Convención de Imágenes

1. **Estructura de Directorios**
   ```
   core_docs/docs/
   ├── _static/  # Directorio principal para archivos estáticos
   │   └── images/  # Directorio para todas las imágenes
   │       ├── sistema_pedidos/  # Subdirectorio para imágenes de sistema de pedidos
   │       ├── facturacion/      # Subdirectorio para imágenes de facturación
   │       └── ...              # Otros subdirectorios según sección
   ```

2. **Nomenclatura de Archivos**
   - Usa nombres descriptivos y en minúsculas
   - Incluye la fecha en YYYYMMDD si es necesario
   - Usa extensión .png o .jpg
   - Ejemplo: `proceso_pedido_20250531.png`

3. **Inserción de Imágenes en Markdown**
   ```markdown
   ![Descripción de la imagen](/_static/images/sistema_pedidos/nombre_archivo.png)
   ```
   - La ruta debe comenzar con `/_static/` para que Sphinx pueda localizar la imagen correctamente
   - No uses rutas relativas como `../_static/` ya que pueden causar problemas en la reconstrucción

4. **Tamaño y Calidad**
   - Máximo ancho recomendado: 1200px
   - Calidad: 70-80%
   - Formato: PNG para interfaces, JPG para capturas de pantalla

5. **Proceso de Incorporación**
   1. **Crear Directorio**
      ```bash
      mkdir -p core_docs/docs/_static/images/nombre_seccion
      ```
   2. **Mover Imagen**
      ```bash
      cp /ruta/a/tu/imagen.png core_docs/docs/_static/images/nombre_seccion/
      ```
   3. **Actualizar Documentación**
      - Agrega la imagen usando la sintaxis correcta: `![Descripción](/_static/images/nombre_seccion/nombre_archivo.png)`
      - Reconstruye la documentación: `python manage.py rebuild_docs`

6. **Validación**
   - Verifica que la imagen se copie correctamente en el directorio de salida: `_build/html/_static/images/`
   - Si la imagen no aparece, verifica:
     - Que la ruta en el markdown use `/_static/`
     - Que el archivo exista en el directorio correcto
     - Que la reconstrucción de la documentación no muestre errores

## Catálogo de Imágenes

Consulte el [Catálogo de Imágenes](catalogo_imagenes.md) para ver una lista completa de todas las imágenes utilizadas en la documentación, organizadas por sección y con sus descripciones correspondientes.

## Guía de Uso

### 1. Crear/Modificar Documentación

1. **Crear nuevo archivo**
   - Crea un nuevo archivo `.md` en el directorio `core_docs/docs/`
   - Usa un nombre descriptivo y en minúsculas (ejemplo: `gestion_inventario.md`)
   - Actualiza el TOC en `index.md` si es necesario

2. **Modificar archivo existente**
   - Edita el archivo correspondiente en el directorio `core_docs/docs/`
   - No modifiques archivos en `_build/html/` ya que son generados automáticamente

3. **Estructura de los Archivos**
   - Usa los siguientes niveles de encabezados:
     ```markdown
     # Título Principal
     ## Subtítulo
     ### Sección
     ```
   - Usa `<nombre_archivo>` para referencias internas
   - Ejemplo: `- Instalación <instalacion>`

### 2. Reconstrucción de la Documentación

1. **Reconstrucción Manual**
   ```bash
   # Desde el directorio core_docs/docs/
   make clean
   make html
   ```

2. **Reconstrucción Automática**
   - La documentación se reconstruye automáticamente cuando se modifican ciertos modelos:
     - Item
     - Proveedor
     - Lista_Pedidos
     - Listado_Planillas

3. **Comando Django**
   ```bash
   python manage.py rebuild_docs
   ```

### 3. Reglas Importantes

1. **No Modificar Archivos Generados**
   - No modifiques archivos en `_build/html/`
   - Los cambios se perderán en la próxima reconstrucción

2. **Mantener Consistencia**
   - Usa la misma estructura y formato en todos los archivos
   - Mantén la jerarquía de encabezados consistente
   - Usa el mismo estilo de enlaces y referencias

3. **Versionado**
   - La versión se obtiene automáticamente de `package.json`
   - Se muestra en la barra de anuncio superior
   - No modificar la sección de versiones manualmente

## Mantenimiento

1. **Actualizaciones Regulares**
   - Actualiza la documentación cuando se realicen cambios importantes en el código
   - Mantén la documentación sincronizada con el código

2. **Revisión**
   - Revisa periódicamente la documentación para asegurar que está actualizada
   - Verifica que los enlaces internos funcionen correctamente

3. **Errores Comunes**
   - Referencias rotas en el TOC
   - Archivos no incluidos en el TOC
   - Formato inconsistente
   - Versiones desactualizadas

## Comandos Útiles

```bash
# Reconstruir manualmente
make clean
make html

# Usar comando Django
python manage.py rebuild_docs

# Verificar estado
make html  # Muestra advertencias y errores
```
