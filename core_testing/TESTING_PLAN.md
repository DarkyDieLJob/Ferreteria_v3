# Plan de Pruebas para core_testing

## Objetivo
Mejorar la cobertura y calidad de las pruebas en el módulo core_testing, asegurando que las pruebas sean relevantes para la implementación actual del dashboard simplificado.

## Estado Actual (07/07/2025)
- ✅ Se ha implementado cobertura completa de pruebas para los modelos de facturación
  - Cliente: 7 pruebas (creación, representación, métodos de responsabilidad y tipo de documento)
  - ArticuloVendido: 6 pruebas (creación con/sin ítem, método get_item)
  - MetodoPago: 4 pruebas (creación, valores por defecto, representación)
  - Transaccion: 5 pruebas (creación, fechas automáticas, relaciones)
  - CierreZ: 4 pruebas (creación, valores por defecto, zeta_numero)
- ✅ Se ha corregido el comportamiento de zeta_numero en CierreZ
- ✅ Se ha mejorado la estructura de pruebas con archivos separados por modelo
- ✅ Se ha actualizado la documentación del plan de pruebas
- ✅ Se ha asegurado la integración con el flujo de trabajo documentation → pre-release

## Fase 1: Limpieza de Pruebas Obsoletas (Completada ✅)

### 1.1 Identificación de Pruebas Obsoletas
- [x] Revisar pruebas existentes en `test_views.py`
- [x] Identificar pruebas que ya no son relevantes para la implementación actual
- [x] Documentar las pruebas que serán eliminadas

### 1.2 Eliminación de Pruebas
- [x] Eliminar pruebas de interfaces de prueba obsoletas
  - Se eliminaron pruebas relacionadas con `InterfaceTestingView`
  - Se eliminaron pruebas de `RunTestApiTest` que ya no son relevantes
- [x] Eliminar pruebas de API que ya no existen
  - Se eliminaron pruebas de endpoints de API obsoletos
- [x] Verificar que las pruebas restantes sigan siendo válidas
  - Se actualizaron las pruebas restantes para que funcionen con la implementación actual

## Fase 2: Pruebas del Dashboard (En Progreso 🚧)

### 2.1 Pruebas de Vista Principal
- [x] Pruebas para `TestingDashboardView`
  - [x] Carga correcta del template
  - [x] Contexto con estadísticas básicas
  - [x] Manejo de autenticación

### 2.2 Pruebas de Componentes
- [x] Pruebas para el resumen de cobertura (`CoverageReportView`)
  - [x] Carga del template correcto
  - [x] Contexto con datos de cobertura
  - [x] Manejo de filtros personalizados
- [ ] Pruebas para la visualización de tendencias
- [x] Pruebas para la lista de pruebas recientes (`TestRunDetailView`)
  - [x] Visualización de detalles de ejecución
  - [x] Manejo de test runs inexistentes

## Fase 3: Pruebas de Facturación (Completado ✅)

### 3.1 Pruebas de Modelos de Facturación
- [x] **Modelo Cliente**
  - [x] Creación y validación de campos
  - [x] Métodos de responsabilidad y tipo de documento
  - [x] Representación en string

- [x] **Modelo ArticuloVendido**
  - [x] Creación con ítem registrado
  - [x] Creación con artículo sin registrar
  - [x] Método get_item()

- [x] **Modelo MetodoPago**
  - [x] Valores por defecto
  - [x] Representación en string

- [x] **Modelo Transaccion**
  - [x] Creación con relaciones
  - [x] Fechas automáticas
  - [x] Método get_cliente_id()

- [x] **Modelo CierreZ**
  - [x] Comportamiento de zeta_numero
  - [x] Valores por defecto
  - [x] Fechas automáticas

## Fase 4: Pruebas de Integración (Próximos Pasos ⏭️)

### 3.1 Integración con Modelos
- [ ] Pruebas de consultas a `TestRun`
  - [ ] Creación de instancias de prueba
  - [ ] Consultas agregadas
  - [ ] Relaciones con otros modelos
- [ ] Pruebas de consultas a `ModuleCoverage`
  - [ ] Cálculo de cobertura
  - [ ] Actualización de datos

### 3.2 Integración con Templates
- [x] Pruebas de renderizado de templates básicos
- [ ] Pruebas de visualización de datos complejos
  - [ ] Gráficos de tendencias
  - [ ] Tablas de resultados

## Fase 4: Pruebas de Rendimiento (Pendiente)

### 4.1 Rendimiento de Consultas
- [ ] Optimización de consultas a la base de datos
- [ ] Pruebas de carga para el dashboard
- [ ] Monitoreo de uso de memoria

## Métricas de Éxito

- [x] Aumentar la cobertura de código al 80%
- [ ] Reducir el tiempo de ejecución de pruebas en un 20%
- [x] Tener al menos una prueba por vista y modelo
- [ ] Implementar pruebas de integración continua (CI/CD)

## Herramientas

- [x] pytest-django
- [x] coverage
- [ ] factory-boy (para datos de prueba)
- [ ] pytest-xdist (para paralelización de pruebas)

## Próximos Pasos

1. Implementar pruebas de integración para los modelos `TestRun` y `ModuleCoverage`
2. Agregar pruebas para la visualización de tendencias
3. Optimizar el rendimiento de las consultas existentes
4. Configurar integración continua para ejecutar pruebas automáticamente
