# 🏗️ Arquitectura del Sistema de Pruebas

## Visión General

`core_testing` es un sistema completo de gestión de pruebas para la aplicación de Ferretería que incluye:

- 🖥️ **Dashboard Interactivo**: Visualización en tiempo real del estado de las pruebas
- 📊 **Reportes de Cobertura**: Análisis detallado de la cobertura de código
- ⚡ **Ejecución de Pruebas**: Herramientas para ejecutar pruebas de forma controlada
- 📈 **Métricas y Análisis**: Seguimiento de tendencias y rendimiento de pruebas

## Objetivos del Sistema

1. Proporcionar visibilidad en tiempo real del estado de las pruebas
2. Facilitar la identificación de problemas de calidad del código
3. Integrarse con el flujo de desarrollo existente
4. Ofrecer métricas útiles para la toma de decisiones

## 🗂️ Estructura del Proyecto (Actualizada: 06/07/2025)

```
core_testing/
├── models.py               # Modelos de datos para pruebas y cobertura
├── views/                  # Vistas del sistema de pruebas
│   ├── __init__.py         # Exportación de vistas
│   ├── views.py            # Vistas principales
│   └── views_test.py       # Pruebas de las vistas
│
├── templates/              # Plantillas del dashboard
│   ├── core_testing/       # Plantillas específicas del módulo
│   │   ├── dashboard.html  # Panel principal
│   │   ├── testrun_list.html  # Lista de ejecuciones
│   │   └── ...
│
├── tests/                  # Pruebas unitarias
│   ├── __init__.py
│   ├── test_basic.py       # Pruebas básicas
│   └── ...
│
├── utils/                  # Utilidades
├── management/             # Comandos personalizados
└── testing_interfaces/     # Interfaces de prueba personalizadas
│   ├── core_testing/
│   │   ├── base_testing.html    # Plantilla base para el área de testing
│   │   ├── dashboard.html       # Vista principal del dashboard
│   │   ├── coverage_report.html # Reporte detallado de cobertura
│   │   ├── testrun_detail.html  # Detalle de ejecución de pruebas
│   │   └── testrun_list.html    # Listado histórico de ejecuciones
│   └── includes/                # Componentes reutilizables
│       ├── _test_metrics.html   # Widget de métricas
│       └── _coverage_chart.html # Gráficos de cobertura
│
├── static/
│   └── core_testing/
│       ├── css/
│       │   └── dashboard.css    # Estilos del dashboard
│       └── js/
│           └── dashboard.js     # Lógica del frontend
│
├── management/
│   └── commands/
│       ├── run_tests.py         # Comando para ejecutar pruebas
│       └── update_coverage.py   # Actualización de métricas
│
├── templatetags/           # Filtros y tags personalizados
│   ├── __init__.py
│   └── testing_filters.py  # Filtros para templates
│
├── tests/                  # Pruebas del módulo
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   └── test_commands.py
│
├── views/                 # Vistas del dashboard
│   ├── __init__.py
│   └── views.py
│
├── urls.py                # Rutas del módulo
├── admin.py              # Configuración de admin
├── apps.py               # Configuración de la aplicación
└── signals.py            # Señales para eventos del sistema
```

## 🧩 Componentes Clave

### 1. Modelos de Datos

#### TestRun
- **Propósito**: Almacena información sobre ejecuciones de pruebas
- **Campos Principales**:
  - `start_time`, `end_time`: Marca de tiempo de inicio/fin
  - `status`: Estado de la ejecución (en progreso, completado, fallido)
  - `total_tests`, `passed`, `failed`, `skipped`: Estadísticas
  - `coverage_percentage`: Cobertura de código
  - `duration`: Duración total de la ejecución
- **Relaciones**:
  - `test_cases`: Relación uno a muchos con TestCase
  - `module`: Módulo bajo prueba

#### TestCase
- **Propósito**: Detalles de casos de prueba individuales
- **Campos Principales**:
  - `name`: Nombre descriptivo del caso
  - `status`: Estado (passed, failed, skipped, error)
  - `duration`: Tiempo de ejecución
  - `error_message`: Mensaje de error (si aplica)
  - `stack_trace`: Traza de pila (en caso de fallo)
- **Relaciones**:
  - `test_run`: Ejecución a la que pertenece
  - `test_suite`: Suite de pruebas relacionada

#### CoverageData
- **Propósito**: Almacena métricas de cobertura de código
- **Campos Principales**:
  - `module`: Módulo analizado
  - `line_coverage`: Porcentaje de cobertura de líneas
  - `branch_coverage`: Porcentaje de cobertura de ramas
  - `timestamp`: Fecha de generación del reporte

### 2. Vistas y API

#### DashboardView
- **URL**: `/testing/dashboard/`
- **Métodos**: GET
- **Descripción**: Vista principal del dashboard con resumen de métricas

#### TestRunDetailView
- **URL**: `/testing/runs/<int:pk>/`
- **Métodos**: GET
- **Descripción**: Detalle de una ejecución de pruebas específica

#### CoverageReportView
- **URL**: `/testing/coverage/`
- **Métodos**: GET
- **Descripción**: Reporte detallado de cobertura de código

### 3. Comandos de Gestión

#### run_tests
```bash
python manage.py run_tests [opciones]
```
**Opciones**:
- `--module`: Ejecutar pruebas de un módulo específico
- `--coverage`: Generar reporte de cobertura
- `--parallel`: Ejecutar pruebas en paralelo
- `--keepdb`: Preservar la base de datos de pruebas

#### update_coverage
```bash
python manage.py update_coverage
```
**Propósito**: Actualiza las métricas de cobertura sin ejecutar pruebas

### 4. Sistema de Eventos

El módulo utiliza señales de Django para reaccionar a eventos importantes:

1. **post_test_run**: Después de ejecutar pruebas
   - Actualiza métricas
   - Genera notificaciones
   - Actualiza el dashboard

2. **coverage_updated**: Cuando se actualiza la cobertura
   - Almacena métricas históricas
   - Actualiza las estadísticas del proyecto

#### CoverageData
- Métricas de cobertura de código
- Desglose por archivo y módulo
- Tendencias históricas

### 2. Vistas del Dashboard

#### Dashboard Principal
- Resumen general del estado de las pruebas
- Gráficos de tendencias
- Indicadores clave de rendimiento

#### Vistas por Módulo
- Desglose detallado por aplicación
- Historial de ejecuciones
- Cobertura de código específica

#### Documentación
- Guías de implementación de pruebas
- Ejemplos de código
- Buenas prácticas

## Flujo de Datos

1. **Ejecución de Pruebas**:
   - Las pruebas se ejecutan mediante comandos de gestión o CI/CD
   - Los resultados se guardan en formato estándar (JUnit, Coverage.py)

2. **Procesamiento**:
   - Los comandos de gestión procesan los resultados
   - Se actualizan los modelos de datos
   - Se generan métricas agregadas

3. **Visualización**:
   - Las vistas consultan los modelos de datos
   - Se presentan los datos de forma clara y accesible
   - Los usuarios pueden navegar entre diferentes niveles de detalle

## Integración con el Proyecto

### Configuración Requerida

1. **settings.py**:
   ```python
   INSTALLED_APPS += ['core_testing']
   
   # Configuración de rutas para informes de pruebas
   TEST_RUNNER = 'core_testing.runner.PytestTestRunner'
   TEST_OUTPUT_DIR = BASE_DIR / 'test_results'
   ```

2. **CI/CD**:
   - Configurar para ejecutar pruebas y actualizar el dashboard
   - Ejemplo para GitHub Actions:
     ```yaml
     - name: Run Tests
       run: |
         python manage.py test
         python manage.py update_test_results
     ```

## Próximos Pasos

1. Implementar los modelos de datos actualizados
2. Desarrollar las vistas del dashboard
3. Crear comandos de gestión para actualización automática
4. Documentar el proceso de integración

2. **Refactorización (si es necesario)**:
   - Extraer lógica de negocio a funciones/métodos más pequeños
   - Aplicar principios SOLID
   - Asegurar bajo acoplamiento y alta cohesión

3. **Implementación de Pruebas**:
   - Crear pruebas que verifiquen el comportamiento actual
   - Asegurar que las pruebas fallen si el comportamiento cambia

## Integración con Aplicaciones Existentes

### Para Aplicaciones Nuevas

1. Crear directorio `tests/` en la raíz de la aplicación
2. Importar las utilidades de `core_testing`
3. Seguir la estructura de pruebas establecida

### Para Aplicaciones Existentes

1. Evaluar la necesidad de refactorización
2. Crear pruebas para la funcionalidad crítica primero
3. Refactorizar gradualmente siguiendo las pruebas

## Buenas Prácticas

1. **Nombrado de Pruebas**:
   - Usar nombres descriptivos que expliquen el comportamiento probado
   - Seguir el patrón: `test_<método>_<condición>_<resultado_esperado>`

2. **Organización**:
   - Agrupar pruebas relacionadas en clases
   - Usar fixtures de pytest para datos de prueba comunes
   - Mantener las pruebas independientes entre sí

## 🔧 Mantenimiento y Mejoras

### Mantenimiento Regular

1. **Actualización de Pruebas**
   - Revisar y actualizar pruebas al modificar funcionalidades existentes
   - Eliminar pruebas obsoletas o redundantes
   - Mantener la cobertura de código por encima del 80%

2. **Rendimiento**
   - Monitorear el tiempo de ejecución de las pruebas
   - Optimizar pruebas lentas
   - Considerar el uso de fixtures para datos de prueba

3. **Documentación**
   - Mantener actualizada la documentación del sistema
   - Documentar nuevas características y cambios
   - Incluir ejemplos de uso

### Mejoras Futuras

1. **Integración con CI/CD**
   - Configuración para GitHub Actions/GitLab CI
   - Notificaciones en tiempo real
   - Reportes automatizados

2. **Análisis Avanzado**
   - Detección de pruebas frágiles
   - Análisis de tendencias
   - Alertas automáticas

3. **Mejoras en la Interfaz**
   - Filtros avanzados
   - Exportación de reportes
   - Vistas personalizables

## 📊 Métricas Clave de Rendimiento (KPI)

1. **Cobertura de Código**
   - Objetivo: >80% de cobertura
   - Actual: [Por determinar]%

2. **Tiempo de Ejecución**
   - Tiempo promedio: [Por determinar] segundos
   - Objetivo: < 5 minutos para todo el conjunto

3. **Estabilidad**
   - Tasa de éxito: >95%
   - Pruebas inestables: <5%

## Ejemplo de Uso

### 1. Definir una Interfaz de Prueba

```python
# core_testing/testing_interfaces/ventas.py
from core_testing.testing_interfaces.base import TestingInterface

class VentaTestingInterface(TestingInterface):
    name = "ventas"
    description = "Pruebas para el módulo de ventas"
    
    def test_crear_venta(self, cliente, productos):
        """Prueba la creación de una nueva venta"""
        # Implementación de la prueba
        pass
```

### 2. Usar en una Aplicación

```python
# ventas/tests/test_models.py
import pytest
from core_testing.testing_interfaces.ventas import VentaTestingInterface

class TestVentaModel(VentaTestingInterface):
    
    def test_crear_venta(self):
        # Configuración
        cliente = ClienteFactory()
        productos = [ProductoFactory() for _ in range(3)]
        
        # Ejecutar prueba de la interfaz
        resultado = super().test_crear_venta(cliente, productos)
        
        # Aserciones específicas
        assert resultado.estado == 'completada'
        assert resultado.total > 0
```

## Consideraciones de Rendimiento

- Ejecutar pruebas en paralelo cuando sea posible
- Usar bases de datos en memoria para pruebas unitarias
- Limpiar datos de prueba después de cada ejecución
- Monitorear el tiempo de ejecución de las pruebas

## Seguridad

- No incluir datos sensibles en las pruebas
- Validar entradas incluso en pruebas
- Probar casos de error y condiciones de borde
- Verificar permisos y autenticación

## Mantenimiento

- Revisar periódicamente las dependencias de testing
- Actualizar las pruebas al actualizar versiones de Django
- Documentar cambios en las interfaces de prueba
