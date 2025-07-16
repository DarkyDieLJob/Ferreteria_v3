# Configuración de la API v4

Esta guía explica cómo configurar el entorno de desarrollo para la API v4 del sistema de Ferretería Paoli.

## Requisitos Previos

- Python 3.8+
- pip (gestor de paquetes de Python)
- Git
- Entorno virtual (recomendado)

## Instalación de Dependencias

1. **Clonar el repositorio** (si aún no lo has hecho):
   ```bash
   git clone https://github.com/tu-usuario/ferreteria-paoli.git
   cd ferreteria-paoli
   ```

2. **Crear y activar un entorno virtual** (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias de la API v4**:
   ```bash
   pip install djangorestframework djangorestframework-simplejwt drf-yasg django-cors-headers django-filter
   ```

## Configuración del Proyecto

1. **Asegúrate de que las siguientes aplicaciones estén en INSTALLED_APPS** (en `settings.py` o `local_settings.py`):
   ```python
   INSTALLED_APPS = [
       # ...
       'rest_framework',
       'rest_framework.authtoken',
       'corsheaders',
       'drf_yasg',
       # ...
   ]
   ```

2. **Agrega la configuración de DRF** (puedes copiarla de `core_config/api_settings.py` o incluirla directamente en tu configuración):
   ```python
   from .api_settings import REST_FRAMEWORK, CORS_ORIGIN_WHITELIST, SWAGGER_SETTINGS
   ```

3. **Configura las URLs** (deberías tener algo como esto en tu `urls.py` principal):
   ```python
   from django.urls import path, include
   
   urlpatterns = [
       # ... otras URLs ...
       path('api/v4/', include('core_config.api.v4.urls', namespace='v4')),
   ]
   ```

## Ejecutando el Servidor de Desarrollo

1. **Asegúrate de que todas las migraciones estén aplicadas**:
   ```bash
   python manage.py migrate
   ```

2. **Crea un superusuario** (si aún no tienes uno):
   ```bash
   python manage.py createsuperuser
   ```

3. **Inicia el servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```

4. **Accede a la documentación interactiva**:
   - Swagger UI: http://localhost:8000/api/v4/docs/swagger/
   - ReDoc: http://localhost:8000/api/v4/docs/redoc/

## Estructura del Proyecto

```
core_config/
├── api/
│   └── v4/
│       ├── __init__.py
│       ├── urls.py         # Rutas de la API
│       ├── serializers/    # Serializadores
│       ├── views/          # Vistas basadas en clases
│       ├── permissions/    # Permisos personalizados
│       └── docs/           # Documentación adicional
└── ...
```

## Convenciones de Código

- **Vistas**: Usar ViewSets siempre que sea posible
- **Serializadores**: Un archivo por modelo
- **Permisos**: Implementar permisos personalizados cuando sea necesario
- **Documentación**: Usar docstrings siguiendo el formato Google Style

## Próximos Pasos

1. Implementar autenticación JWT
2. Configurar throttling y rate limiting
3. Agregar más documentación
4. Implementar pruebas automatizadas

## Solución de Problemas Comunes

- **Problema**: No se encuentra el módulo 'rest_framework'
  **Solución**: Asegúrate de haber instalado las dependencias con `pip install -r requirements.txt`

- **Problema**: Error de CORS al acceder a la API
  **Solución**: Verifica que `corsheaders` esté en INSTALLED_APPS y que `CORS_ORIGIN_WHITELIST` esté configurado correctamente

- **Problema**: La documentación de la API no se muestra
  **Solución**: Asegúrate de que `drf-yasg` esté instalado y configurado correctamente
