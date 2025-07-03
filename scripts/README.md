# Scripts de Automatización

Este directorio contiene scripts útiles para automatizar tareas comunes en el proyecto.

## Scripts Disponibles

### documentation_workflow.py

Automatiza el flujo de trabajo de documentación siguiendo las mejores prácticas de Git.

#### Requisitos

- Python 3.6+
- Git
- GitHub CLI (`gh`) para crear PRs automáticamente (opcional)

#### Uso

1. **Iniciar el flujo de documentación**:
   ```bash
   python3 scripts/documentation_workflow.py
   ```

2. **Sigue las instrucciones en pantalla** para:
   - Crear una rama de documentación
   - Confirmar cambios
   - Crear un Pull Request

3. **Flujo completo**:
   - Crea una rama de feature para documentación
   - Haz tus cambios de documentación
   - Confirma los cambios
   - Crea un PR a la rama `documentation`
   - Luego, crea un PR de `documentation` a `develop`

#### Características

- Crea automáticamente la rama `documentation` si no existe
- Guía paso a paso a través del proceso de documentación
- Soporta la creación de PRs automáticos con GitHub CLI
- Verifica el estado del repositorio antes de realizar cambios

## Convenciones de Nombrado

- Para ramas de documentación: `feature/documentation-*`
- Para mensajes de commit: Usar prefijos como `docs:`, `chore:`, etc.

## Contribuir

1. Crea una rama para tu script: `feature/script-nombre`
2. Asegúrate de documentar el script
3. Incluye ejemplos de uso
4. Haz un PR a la rama `documentation`
