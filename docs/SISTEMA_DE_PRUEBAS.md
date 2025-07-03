# Sistema de Pruebas - Ferretería

## Visión General

El módulo `core_testing` proporciona un sistema completo para la ejecución y gestión de pruebas en la aplicación de Ferretería. Este documento detalla la arquitectura, configuración y uso del sistema de pruebas.

## Tabla de Contenidos

1. [Arquitectura](#arquitectura)
2. [Configuración](#configuración)
3. [Uso del Panel de Pruebas](#uso-del-panel-de-pruebas)
4. [Creación de Pruebas Personalizadas](#creación-de-pruebas-personalizadas)
5. [Ejecución de Pruebas](#ejecución-de-pruebas)
6. [Solución de Problemas](#solución-de-problemas)

## Arquitectura

El sistema de pruebas sigue una arquitectura modular con los siguientes componentes principales:

- **Panel de Control**: Interfaz web para ejecutar y monitorear pruebas.
- **Interfaces de Prueba**: Módulos que implementan lógica de prueba específica.
- **Motor de Ejecución**: Gestiona la ejecución de pruebas y recopila resultados.
- **Sistema de Reportes**: Genera informes detallados de las pruebas ejecutadas.

## Configuración

### Requisitos Previos

- Python 3.8+
- Django 4.0+
- Dependencias del proyecto instaladas

### Instalación

1. Asegúrate de que el módulo esté en `INSTALLED_APPS`:

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
