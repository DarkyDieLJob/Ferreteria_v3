# 🧪 Sistema de Pruebas - Ferretería

## Visión General

El módulo `core_testing` proporciona un sistema completo para la ejecución, monitoreo y gestión de pruebas en la aplicación de Ferretería. Incluye un dashboard interactivo, reportes de cobertura y herramientas para la ejecución de pruebas tanto en desarrollo como en producción.

## Tabla de Contenidos

1. [Arquitectura](#arquitectura)
2. [Configuración](#configuración)
3. [Dashboard de Pruebas](#dashboard-de-pruebas)
4. [Uso del Panel de Pruebas](#uso-del-panel-de-pruebas)
5. [Comando run_tests](#comando-run_tests)
6. [Creación de Pruebas Personalizadas](#creación-de-pruebas-personalizadas)
7. [Ejecución de Pruebas](#ejecución-de-pruebas)
8. [Solución de Problemas](#solución-de-problemas)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

## 🏗️ Arquitectura

El sistema de pruebas sigue una arquitectura modular y extensible con los siguientes componentes principales:

- **Dashboard de Pruebas**: Interfaz web interactiva para monitorear y ejecutar pruebas.
- **Interfaces de Prueba**: Módulos que implementan lógica de prueba específica siguiendo el patrón `TestingInterface`.
- **Motor de Ejecución**: Gestiona la ejecución asíncrona de pruebas y recopilación de resultados.
- **Sistema de Reportes**: Genera informes detallados incluyendo cobertura de código.
- **API REST**: Endpoints para integración con sistemas CI/CD y monitoreo.

### Diagrama de Componentes

```mermaid
graph TD
    A[Dashboard Web] -->|Ejecuta| B[Motor de Pruebas]
    B -->|Usa| C[Interfaces de Prueba]
    C -->|Ejecuta| D[Pruebas Unitarias]
    C -->|Ejecuta| E[Pruebas de Integración]
    B -->|Almacena| F[Base de Datos]
    A -->|Visualiza| G[Reportes y Métricas]
    H[Comando run_tests] -->|Interactúa con| B
```

## ⚙️ Configuración

### Requisitos Previos

- Python 3.8+
- Django 4.0+
- Dependencias del proyecto instaladas
- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Node.js (opcional, para desarrollo de componentes frontend)

## 🖥️ Dashboard de Pruebas

El dashboard de pruebas proporciona una interfaz visual para monitorear y gestionar las pruebas del sistema.

### Características Principales

- **Vista General**: Muestra un resumen del estado actual de las pruebas
- **Reportes de Cobertura**: Visualización interactiva de la cobertura de código
- **Historial de Ejecuciones**: Registro detallado de pruebas pasadas
- **Filtros y Búsqueda**: Para encontrar rápidamente pruebas específicas
- **Exportación de Resultados**: Genera informes en varios formatos

### Acceso al Dashboard

1. Inicia el servidor de desarrollo:
   ```bash
   python manage.py runserver
   ```

2. Navega a:
   ```
   http://localhost:8000/testing/dashboard/
   ```

## 🛠️ Comando run_tests

El comando `run_tests` es la forma recomendada de ejecutar pruebas en el proyecto, ya que garantiza que los resultados se registren correctamente en el dashboard y se generen los reportes necesarios.

### Uso Básico

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

### Comportamiento por Defecto

Por defecto, el comando `run_tests`:
1. Busca pruebas en los directorios: `tests/`, `core_testing/`, `facturacion/`, `articulos/`
2. Ejecuta las pruebas con cobertura de código
3. Genera informes en formato XML y HTML en el directorio `htmlcov/`
4. Registra los resultados en la base de datos para el dashboard
5. Muestra un resumen de los resultados en la consola

### Integración con el Dashboard

Los resultados de las pruebas ejecutadas con `run_tests` se registran automáticamente en la base de datos y están disponibles en el dashboard de pruebas en:
```
http://localhost:8000/testing/dashboard/
```

### Opciones Avanzadas

| Opción | Descripción |
|--------|-------------|
| `--no-coverage` | Desactiva la generación de informes de cobertura |
| `--parallel=N` | Ejecuta pruebas en N procesos paralelos |
| `--keepdb` | Preserva la base de datos de pruebas entre ejecuciones |
| `--no-failfast` | Continúa la ejecución después de fallos |
| `-v, --verbosity` | Controla la cantidad de salida (0-2) |
| `--test-path=RUTA` | Especifica una ruta personalizada para buscar pruebas |

### Ejemplos Prácticos

```bash
# Ejecutar solo pruebas de facturación con cobertura detallada
python manage.py run_tests facturacion

# Ejecutar pruebas en paralelo sin cobertura
python manage.py run_tests --parallel=4 --no-coverage

# Ejecutar una prueba específica con salida detallada
python manage.py run_tests facturacion.tests.test_models.ClienteModelTest -v 2
```

### Notas Importantes

1. **No usar pytest directamente**: Siempre usa `python manage.py run_tests` en lugar de `pytest` para garantizar la integración con el dashboard.
2. **Base de datos de pruebas**: Por defecto se usa SQLite en memoria. Usa `--keepdb` para acelerar ejecuciones posteriores.
3. **Cobertura**: Los informes de cobertura se generan en `htmlcov/`. Usa `--no-coverage` para desactivar si no los necesitas.
4. **Variables de entorno**: El comando respeta la configuración de Django, incluyendo `DJANGO_SETTINGS_MODULE`.

❌ **No uses `pytest` directamente**, ya que:
- No registrará los resultados en el dashboard
- No generará reportes de cobertura consistentes
- No respetará la configuración personalizada del proyecto

✅ **Siempre usa** `python manage.py run_tests` para garantizar:
- Registro adecuado de resultados
- Generación de reportes
- Consistencia en la ejecución de pruebas

### Opciones Disponibles

| Opción | Descripción |
|--------|-------------|
| `--coverage` | Genera reporte de cobertura |
| `--parallel=N` | Ejecuta pruebas en N procesos paralelos |
| `--keepdb` | Preserva la base de datos de pruebas entre ejecuciones |
| `--failfast` | Detiene la ejecución al primer fallo |
| `--verbosity=2` | Nivel de detalle en la salida (0-3) |

### Integración con CI/CD

#### GitHub Actions

Ejemplo de configuración para GitHub Actions que utiliza `run_tests` para ejecutar las pruebas:

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests with coverage
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
        DJANGO_SETTINGS_MODULE: core.settings.test
      run: |
        # Ejecutar pruebas con cobertura
        python manage.py run_tests --coverage --parallel=4
        
        # Opcional: Subir cobertura a un servicio como Codecov
        # bash <(curl -s https://codecov.io/bash)
```

#### GitLab CI

Ejemplo para GitLab CI/CD:

```yaml
image: python:3.10

services:
  - postgres:13-alpine

variables:
  POSTGRES_DB: test_db
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  DATABASE_URL: "postgres://postgres:postgres@postgres:5432/test_db"

before_script:
  - apt-get update
  - apt-get install -y python3-dev libpq-dev
  - pip install -r requirements.txt

test:
  script:
    - python manage.py run_tests --coverage --parallel=4
  artifacts:
    when: always
    paths:
      - htmlcov/
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## ⚙️ Configuración

### Requisitos Previos

- Python 3.8+
- Django 4.0+
- Dependencias del proyecto instaladas
- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Node.js (opcional, para desarrollo de componentes frontend)

### Instalación

1. Asegúrate de que el módulo esté en `INSTALLED_APPS`:

```python
INSTALLED_APPS += [
    'core_testing',
]
```

2. Configura la base de datos para pruebas en `local_settings.py`:

```python
# Configuración para pruebas
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
}
```

3. Ejecuta las migraciones:

```bash
python manage.py migrate core_testing
```

## Uso del Panel de Pruebas

El panel de pruebas está disponible en `/testing/` después de iniciar el servidor de desarrollo.

### Características Principales

- Vista general de todas las pruebas disponibles
- Ejecución individual o por lotes
- Historial de ejecuciones
- Filtrado y búsqueda de pruebas
- Exportación de resultados

## Creación de Pruebas Personalizadas

### Estructura Básica

Crea un nuevo archivo en `core_testing/testing_interfaces/` con la siguiente estructura:

```python
from core_testing.testing_interfaces.base import TestingInterface

class MiPruebaPersonalizada(TestingInterface):
    """Documentación de la prueba."""
    
    name = "nombre_unico_prueba"
    description = "Descripción detallada de la prueba"
    category = "Categoría"  # Opcional
    
    def run_test(self):
        """
        Implementación de la lógica de prueba.
        
        Returns:
            dict: Resultados de la prueba con el siguiente formato:
                {
                    'success': bool,
                    'message': str,
                    'details': Any,  # Datos adicionales
                    'execution_time': float  # Tiempo de ejecución en segundos
                }
        """
        try:
            # Lógica de la prueba
            resultado = realizar_operacion()
            
            return {
                'success': True,
                'message': 'Prueba exitosa',
                'details': resultado,
                'execution_time': 0.0  # Reemplazar con tiempo real
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error en la prueba: {str(e)}',
                'details': str(e),
                'execution_time': 0.0
            }
```

### Buenas Prácticas

1. **Nombres Descriptivos**: Usa nombres claros y descriptivos para las pruebas.
2. Una Aserción por Prueba: Cada prueba debe verificar una sola condición.
3. Manejo de Errores: Siempre incluye manejo de excepciones.
4. Documentación: Documenta claramente el propósito y uso de cada prueba.
5. Aislamiento: Las pruebas deben ser independientes entre sí.

## Ejecución de Pruebas

### Desde el Navegador

1. Navega a `http://localhost:8000/testing/`
2. Selecciona las pruebas a ejecutar
3. Haz clic en "Ejecutar Pruebas"

### Desde la Línea de Comandos

```bash
# Todas las pruebas
python manage.py test core_testing

# Pruebas específicas
python manage.py test core_testing.tests.test_interfaces

# Con mayor verbosidad
python manage.py test core_testing --verbosity=2

# Ejecutar pruebas que coincidan con un patrón
python manage.py test core_testing.tests.test_interfaces -k "test_pattern"
```

### Configuración de Pruebas

Puedes configurar el comportamiento de las pruebas mediante las siguientes variables en `local_settings.py`:

```python
# Configuración de pruebas
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
TEST_DISCOVER_TOP_LEVEL = BASE_DIR
TEST_DISCOVER_PATTERN = 'test_*.py'
```

## Flujo de Trabajo del Dashboard

El dashboard de pruebas proporciona una interfaz centralizada para gestionar y ejecutar pruebas. A continuación, se describe el flujo de trabajo típico:

### 1. Descubrimiento de Interfaces de Prueba

El sistema descubre automáticamente las interfaces de prueba siguiendo estos pasos:

1. **Búsqueda en `core_testing/testing_interfaces/`**:
   - Busca archivos Python que contengan clases que hereden de `TestingInterface`
   - Ignora archivos que comiencen con guión bajo (`_`)

2. **Registro de Interfaces**:
   - Cada interfaz se registra con un nombre único
   - Se valida que implemente los métodos requeridos
   - Se carga en memoria para su uso en el dashboard

### 2. Estructura de una Interfaz de Prueba

Cada interfaz debe seguir esta estructura básica:

```python
from core_testing.testing_interfaces.base import TestingInterface
from django import forms

class MiPruebaForm(forms.Form):
    """Formulario de configuración para la prueba."""
    parametro = forms.CharField(required=False, help_text="Descripción del parámetro")

class MiInterfazDePrueba(TestingInterface):
    """Documentación de la interfaz de prueba."""
    
    # Metadatos requeridos
    name = "nombre_unico"
    description = "Descripción detallada"
    category = "Categoría"  # Opcional
    
    def get_available_tests(self):
        """Devuelve las pruebas disponibles en esta interfaz."""
        return [{
            'name': 'nombre_prueba',
            'description': 'Descripción de la prueba',
            'form_class': MiPruebaForm,  # Opcional
            'requires_form': True  # Si requiere configuración
        }]
    
    def run_test(self, test_name, **kwargs):
        """Ejecuta la prueba especificada."""
        if test_name == 'nombre_prueba':
            try:
                # Lógica de la prueba
                return {
                    'success': True,
                    'message': 'Prueba exitosa',
                    'details': {}
                }
            except Exception as e:
                return {
                    'success': False,
                    'message': f'Error: {str(e)}',
                    'details': {}
                }
        
        raise ValueError(f'Prueba no encontrada: {test_name}')
    
    def get_test_form(self, test_name):
        """Devuelve el formulario para configurar la prueba."""
        tests = self.get_available_tests()
        test = next((t for t in tests if t['name'] == test_name), None)
        if test and test.get('requires_form', False):
            return test['form_class']
        return None
```

### 3. Ciclo de Vida de una Prueba

1. **Inicio**:
   - El usuario accede al dashboard en `/testing/`
   - El sistema carga todas las interfaces disponibles

2. **Configuración**:
   - El usuario selecciona una interfaz
   - Si la prueba requiere configuración, se muestra un formulario
   - El usuario completa los parámetros necesarios

3. **Ejecución**:
   - El usuario hace clic en "Ejecutar Prueba"
   - El sistema crea un nuevo `TestRun`
   - Se ejecuta la prueba en un hilo separado
   - Los resultados se actualizan en tiempo real

4. **Resultados**:
   - Se muestran los resultados en el dashboard
   - Se guarda el historial en la base de datos
   - Se generan métricas y estadísticas

### 4. Personalización del Dashboard

Puedes personalizar la apariencia del dashboard:

1. **Plantillas**:
   - Sobrescribe `core_testing/dashboard.html`
   - Usa `{% extends 'core_testing/base_testing.html' %}`
   - Personaliza los bloques necesarios

2. **Estilos CSS**:
   - Agrega estilos personalizados en `static/core_testing/css/`
   - Sobrescribe las clases existentes o agrega nuevas

3. **JavaScript**:
   - Agrega scripts personalizados en `static/core_testing/js/`
   - Usa eventos del DOM para interactuar con el dashboard

## Solución de Problemas

### Problemas Comunes

1. **Pruebas No Encontradas**
   - Verifica que los archivos de prueba sigan el patrón `test_*.py`
   - Asegúrate de que las clases de prueba hereden de `unittest.TestCase`

2. **Problemas de Importación**
   - Verifica que todos los módulos importados estén instalados
   - Asegúrate de que los imports usen rutas absolutas

3. **Errores de Base de Datos**
   - Verifica la configuración de la base de datos de pruebas
   - Ejecuta `python manage.py migrate` para aplicar migraciones pendientes

### Depuración

Para depurar pruebas:

1. Usa `pdb` o el depurador de tu IDE
2. Ejecuta pruebas con `--pdb` para entrar en modo depuración al fallar:
   ```bash
   python manage.py test core_testing --pdb
   ```
3. Revisa los logs de la aplicación para mensajes de error detallados

## Integración Continua

Para integrar las pruebas en un flujo de CI/CD, agrega un paso como este en tu configuración:

```yaml
# Ejemplo para GitHub Actions
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgres://postgres:postgres@localhost:5432/test_db
      run: |
        python manage.py test core_testing --noinput --parallel
```

## Mantenimiento

### Actualización de Pruebas

1. Actualiza regularmente las pruebas para reflejar cambios en el código
2. Elimina pruebas obsoletas
3. Refactoriza pruebas para mejorar la legibilidad y mantenimiento

### Monitoreo

- Revisa regularmente los resultados de las pruebas
- Establece alertas para pruebas que fallen
- Documenta los casos de prueba existentes y su cobertura

## Recursos Adicionales

- [Documentación de Pruebas de Django](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Guía de Buenas Prácticas de Pruebas](https://realpython.com/python-testing/)
- [Estrategias de Pruebas para Aplicaciones Django](https://www.obeythetestinggoat.com/)

---

*Última actualización: 2025-07-03*
