# Flujo de Trabajo con Documentación Integrada

## Visión General

Este documento describe el flujo de trabajo para integrar cambios de código y documentación de manera coordinada, asegurando que la documentación siempre esté actualizada y en sincronía con el código.

## Ramas Principales

1. **main**
   - Código estable y probado en producción
   - Solo se actualiza mediante Pull Requests desde `develop`
   - Debe contener documentación actualizada

2. **develop**
   - Rama de integración para nuevas características
   - Debe ser estable en todo momento
   - Contiene la última versión de características completadas

3. **documentation**
   - Rama dedicada a la documentación
   - Se actualiza antes de los PRs a `develop`
   - Contiene la documentación más reciente

## Flujo de Trabajo Detallado

### 1. Iniciar una Nueva Característica

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nueva-funcionalidad
```

### 2. Desarrollo de la Característica

1. **Implementación del Código**
   - Desarrolla la funcionalidad en la rama de feature
   - Realiza commits atómicos con mensajes descriptivos

2. **Documentación**
   - Actualiza o crea la documentación necesaria
   - Usa el formato estándar definido en `docs/ESTRUCTURA_DOCUMENTACION.md`
   - Incluye ejemplos de uso cuando sea relevante

### 3. Actualizar Documentación

Antes de hacer un PR a `develop`:

```bash
# Mientras estás en tu rama de feature
git checkout documentation
git pull origin documentation
git merge feature/nueva-funcionalidad --no-ff
# Resuelve conflictos si es necesario
git push origin documentation
```

### 4. Crear PR de Documentación

1. Crea un PR desde `feature/nueva-funcionalidad` a `documentation`
2. Revisa los cambios de documentación
3. Asegúrate de que la documentación sea clara y completa
4. Obtén aprobación del equipo
5. Fusiona el PR

### 5. Actualizar la Rama de Feature

```bash
git checkout feature/nueva-funcionalidad
git merge documentation --no-ff
# Resuelve conflictos si es necesario
```

### 6. Crear PR a Develop

1. Crea un PR desde `feature/nueva-funcionalidad` a `develop`
2. Incluye en la descripción:
   - Resumen de los cambios
   - Impacto en la documentación
   - Cómo probar los cambios
3. Espera la revisión del código
4. Asegúrate de que pasen todas las pruebas
5. Obtén al menos una aprobación
6. Fusiona el PR

### 7. Pruebas de Integración

Después de fusionar en `develop`:

1. El sistema de CI/CD ejecuta pruebas de integración
2. Se verifica que la documentación esté actualizada
3. Se generan reportes de cobertura

## Buenas Prácticas

### Para Documentación

- Documenta los cambios al mismo tiempo que el código
- Usa un lenguaje claro y conciso
- Incluye ejemplos de uso
- Actualiza el CHANGELOG.md para cambios relevantes

### Para Código

- Sigue las guías de estilo del proyecto
- Escribe pruebas unitarias
- Documenta funciones y clases importantes
- Mantén los commits atómicos y descriptivos

## Manejo de Conflictos

### Al Actualizar Documentación

Si hay conflictos al fusionar con `documentation`:

1. Resuelve los conflictos manualmente
2. Asegúrate de no perder cambios importantes
3. Verifica que la documentación siga siendo coherente
4. Haz commit de los cambios resueltos

### Al Actualizar Develop

Si hay conflictos al fusionar con `develop`:

1. Resuelve los conflictos en el código
2. Actualiza la documentación si es necesario
3. Verifica que todo funcione correctamente
4. Haz commit de los cambios resueltos

## Ejemplo de Flujo Completo

1. **Inicio**
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/nuevo-modulo
   ```

2. **Desarrollo**
   ```bash
   # Implementa la funcionalidad
   git add .
   git commit -m "feat(modulo): agregar funcionalidad X"
   ```

3. **Documentación**
   ```bash
   # Actualiza documentación
   git add docs/
   git commit -m "docs(modulo): documentar funcionalidad X"
   ```

4. **Actualizar Rama de Documentación**
   ```bash
   git checkout documentation
   git pull
   git merge feature/nuevo-modulo --no-ff
   # Resolver conflictos si es necesario
   git push origin documentation
   ```

5. **Actualizar Feature con Documentación**
   ```bash
   git checkout feature/nuevo-modulo
   git merge documentation
   ```

6. **PR a Develop**
   - Crea PR desde `feature/nuevo-modulo` a `develop`
   - Espera aprobación
   - Fusiona cuando esté aprobado

## Preguntas Frecuentes

**¿Qué pasa si la documentación necesita cambios después de la revisión?**
1. Haz los cambios necesarios en tu rama de feature
2. Repite el proceso de actualización de documentación
3. Actualiza el PR existente

**¿Cómo manejar documentación para hotfixes?**
1. Crea una rama desde `main`
2. Aplica el hotfix
3. Actualiza la documentación si es necesario
4. Crea PRs tanto a `documentation` como a `main`

**¿Con qué frecuencia debo actualizar la rama de documentación?**
- Idealmente, cada vez que hagas cambios significativos en la documentación
- Como mínimo, antes de crear el PR a `develop`
