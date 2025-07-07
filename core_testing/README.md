# 🧪 Módulo de Pruebas - Core Testing

> **Última actualización**: 06/07/2025  
> **Versión estable**: 1.0.0

## 📝 Descripción
Módulo integral de pruebas para la aplicación de Ferretería, diseñado para facilitar la ejecución, monitoreo y gestión de pruebas funcionales y de integración.

## 🚀 Características Principales

- ✅ **Ejecución de Pruebas**
  - Soporte para pruebas unitarias y de integración
  - Ejecución en paralelo para mayor velocidad
  - Filtrado por módulo o categoría

- 📊 **Dashboard Interactivo**
  - Monitoreo en tiempo real
  - Visualización de tendencias
  - Detalles de ejecuciones pasadas

- 📈 **Cobertura de Código**
  - Reportes detallados
  - Identificación de código no cubierto
  - Seguimiento histórico

- 🔄 **Integración**
  - Flujo de trabajo con ramas `develop` → `documentation` → `pre-release`
  - Compatible con el sistema CI/CD existente

- 🖥️ Dashboard interactivo para monitoreo de pruebas
- 🔄 Ejecución de pruebas con un solo comando (`run_tests`)
- 📊 Reportes detallados de cobertura de código
- 🔍 Seguimiento histórico de ejecuciones
- ⚡ Ejecución en paralelo para mayor velocidad
- 📈 Métricas y estadísticas de pruebas
- 🔔 Alertas y notificaciones de fallos

## ⚙️ Configuración Inicial

1. Asegúrate de que la aplicación esté en `INSTALLED_APPS` en `settings.py`:
   ```python
   INSTALLED_APPS += [
       'core_testing',
   ]
   ```

2. Configura la base de datos para pruebas en `local_settings.py`:
   ```python
   # Configuración para entorno de pruebas
   TESTING = DEBUG  # Asume modo de pruebas cuando DEBUG es True
   
   if TESTING:
       DATABASES = {
           'default': {
               'ENGINE': 'django.db.backends.sqlite3',
               'NAME': BASE_DIR / 'test_db.sqlite3',
           }
       }
       
       # Configuración específica para pruebas
       PASSWORD_HASHERS = [
           'django.contrib.auth.hashers.MD5PasswordHasher',
       ]
   ```

3. Ejecuta las migraciones:
   ```bash
   python manage.py migrate core_testing
   ```

## 🚀 Uso

### Ejecución de Pruebas

> **Importante**: Siempre usa `python manage.py run_tests` en lugar de `pytest` directamente para garantizar el registro adecuado de resultados.

### 🛠️ Comandos de Gestión

### run_tests

El comando `run_tests` es la forma recomendada de ejecutar pruebas en el proyecto, ya que garantiza que los resultados se registren correctamente en el dashboard y se generen los reportes necesarios.

#### Uso Básico

```bash
# Ejecutar todas las pruebas con cobertura (comportamiento por defecto)
python manage.py run_tests

# Ejecutar sin generar informe de cobertura
python manage.py run_tests --no-coverage

# Ejecutar pruebas de un módulo o archivo específico
python manage.py run_tests facturacion  # App completa
python manage.py run_tests facturacion/tests/test_models.py  # Archivo específico
python manage.py run_tests facturacion.tests.test_models  # Módulo Python

# Opciones de ejecución
python manage.py run_tests --parallel=4  # Ejecutar en 4 procesos
python manage.py run_tests --no-failfast  # Continuar después de fallos
python manage.py run_tests --keepdb  # Mantener la base de datos de pruebas
python manage.py run_tests -v 2  # Mayor verbosidad

# Ver todas las opciones disponibles
python manage.py run_tests --help
```

#### Comportamiento por Defecto

Por defecto, el comando:
1. Busca pruebas en los directorios: `tests/`, `core_testing/`, `facturacion/`, `articulos/`
2. Ejecuta las pruebas con cobertura de código
3. Genera informes en formato XML y HTML
4. Registra los resultados en la base de datos para el dashboard
5. Muestra un resumen de los resultados en la consola

### update_coverage

Actualiza las métricas de cobertura sin ejecutar pruebas:

```bash
python manage.py update_coverage
```

### Panel de Pruebas

1. Inicia el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

2. Accede al panel de pruebas en:
   ```
   http://localhost:8000/testing/dashboard/
   ```

   El dashboard muestra:
   - Resumen de pruebas ejecutadas
   - Estadísticas de cobertura
   - Historial de ejecuciones
   - Detalles de pruebas fallidas

### Ejecución de Pruebas desde la Línea de Comandos

Para ejecutar todas las pruebas del módulo:
```bash
python manage.py test core_testing --verbosity=2
```

Para ejecutar pruebas específicas:
```bash
# Ejecutar solo las pruebas de interfaces
python manage.py test core_testing.tests.test_interfaces

# Ejecutar una clase de prueba específica
python manage.py test core_testing.tests.test_interfaces.TestInterfaceDiscovery
```

## Sistema de Descubrimiento de Interfaces

El módulo incluye un sistema de descubrimiento automático de interfaces de prueba. Para crear una nueva interfaz de prueba:

1. Crea un nuevo archivo en `core_testing/testing_interfaces/` (ej: `mi_prueba.py`)
2. Define una clase que herede de `TestingInterface`:

```python
from core_testing.testing_interfaces.base import TestingInterface

class MiPrueba(TestingInterface):
    name = "mi_prueba"
    description = "Descripción de mi prueba"
    
    def run_test(self):
        # Lógica de la prueba
        return {
            'success': True,
            'message': 'Prueba exitosa',
            'details': 'Detalles adicionales...'
        }
```

3. La interfaz estará disponible automáticamente en el panel de pruebas.

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
