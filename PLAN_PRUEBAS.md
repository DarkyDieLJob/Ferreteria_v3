# Plan de Pruebas - Ferretería Paoli v3

## 1. Configuración Inicial

### 1.1 Verificar cobertura actual

```bash
# Ejecutar pruebas con cobertura
python manage.py run_tests --coverage
```

### 1.2 Estructura de directorios propuesta

```
tests/
  __init__.py
  conftest.py           # Configuración común
  factories.py          # Factory Boy para crear datos de prueba
  unit/
    test_models/        # Pruebas de modelos
    test_views/         # Pruebas de vistas
    test_forms/         # Pruebas de formularios
    test_utils/         # Pruebas de utilidades
  integration/
    test_workflows/     # Flujos completos
  e2e/                  # Pruebas de extremo a extremo
```

## 2. Estrategia de Pruebas

### 2.1 Pruebas Unitarias (Objetivo: 80%+ cobertura)
- [ ] Modelos
- [ ] Vistas
- [ ] Formularios
- [ ] Utilidades

### 2.2 Pruebas de Integración
- [ ] Flujos completos
- [ ] Integración con servicios externos

### 2.3 Pruebas de Interfaz
- [ ] Componentes de UI
- [ ] Flujos de usuario críticos

## 3. Herramientas

- [x] pytest-django
- [ ] factory-boy
- [x] pytest-cov
- [ ] pytest-mock

## 4. Siguientes Pasos

1. [x] Crear este documento de planificación
2. [ ] Ejecutar pruebas iniciales para establecer línea base de cobertura
3. [ ] Configurar `factories.py` para generar datos de prueba
4. [ ] Implementar pruebas para modelos principales
5. [ ] Implementar pruebas para vistas principales
6. [ ] Implementar pruebas de integración
7. [ ] Configurar CI/CD para ejecutar pruebas automáticamente

## 5. Comandos Útiles

```bash
# Ejecutar todas las pruebas
python manage.py run_tests --coverage

# Ejecutar pruebas específicas
python manage.py run_tests tests/unit/test_models/test_producto.py

# Generar reporte de cobertura HTML
coverage html
# Abrir en navegador:
xdg-open htmlcov/index.html
```

## 6. Notas

- Usar `@pytest.mark.django_db` para pruebas que necesiten base de datos
- Usar `factory-boy` para crear datos de prueba consistentes
- Mantener las pruebas rápidas y aisladas
- Documentar casos de prueba importantes

## 7. Estado Actual

- Fecha: 2025-07-05
- Cobertura actual: Por determinar
- Próximos pasos: Ejecutar pruebas iniciales para establecer línea base
