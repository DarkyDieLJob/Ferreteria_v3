# Módulo de Testing - Ferretería

## Descripción
Módulo de pruebas para la aplicación de Ferretería, diseñado para facilitar la ejecución de pruebas funcionales y de integración en el sistema.

## Características Principales

- Interfaz web para ejecutar pruebas
- Gestión de interfaces de prueba personalizables
- Seguimiento de ejecuciones de pruebas
- Reportes de cobertura de código
- Integración con el sistema existente

## Configuración Inicial

1. Asegúrate de que la aplicación esté en `INSTALLED_APPS` en `settings.py`:
   ```python
   INSTALLED_APPS += [
       'core_testing',
   ]
   ```

2. Configura la base de datos para pruebas en `local_settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'test_db.sqlite3',
       }
   }
   ```

3. Ejecuta las migraciones:
   ```bash
   python manage.py migrate core_testing
   ```

## Uso

1. Inicia el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

2. Accede al panel de pruebas en:
   ```
   http://localhost:8000/testing/
   ```

## Estructura del Proyecto

```
core_testing/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── signals.py
├── templates/
│   └── core_testing/
│       ├── base.html
│       ├── dashboard.html
│       ├── interface.html
│       └── testrun_detail.html
├── testing_interfaces/
│   ├── __init__.py
│   ├── base.py
│   └── example.py
├── tests.py
├── urls.py
└── views.py
```

## Ejecución de Pruebas

Para ejecutar las pruebas unitarias:

```bash
python manage.py test core_testing
```

Para ver la cobertura de código:

```bash
coverage run --source='.' manage.py test
coverage report
```

## Documentación Adicional

- [Objetivos del Módulo](OBJETIVOS.md)
- [Guía de Desarrollo](docs/DEVELOPMENT.md) (pendiente)
- [API Reference](docs/API.md) (pendiente)
