# Guía de Documentación del Proyecto

## Estructura de Documentación

Cada aplicación del proyecto debe seguir la siguiente estructura de documentación:

```
cada_aplicacion/
├── docs/                 # Documentación detallada
│   ├── ARQUITECTURA.md   # Diseño de la aplicación
│   └── FLUJOS.md        # Flujos de trabajo principales
├── README.md            # Documentación básica
└── OBJETIVOS.md         # Objetivos y roadmap
```

## Generación Automática de Documentación

Hemos creado un script para generar automáticamente la estructura de documentación en todas las aplicaciones del proyecto.

### Uso del Generador de Documentación

1. Navega al directorio raíz del proyecto:
   ```bash
   cd /ruta/al/proyecto
   ```

2. Ejecuta el script de generación:
   ```bash
   python3 scripts/crear_documentacion.py
   ```

### Qué hace el script

- Crea automáticamente los archivos de documentación estándar en cada aplicación
- No sobrescribe archivos existentes
- Genera documentación solo para aplicaciones Django válidas (que tengan archivo apps.py)

### Archivos Generados

1. **README.md**
   - Descripción general de la aplicación
   - Instrucciones de instalación y uso
   - Enlaces a otra documentación

2. **OBJETIVOS.md**
   - Objetivos generales y específicos
   - Métricas de éxito
   - Roadmap de desarrollo

3. **docs/ARQUITECTURA.md**
   - Diagrama de componentes
   - Modelos principales
   - Dependencias
   - Consideraciones de diseño

4. **docs/FLUJOS.md**
   - Flujos de trabajo principales
   - Diagramas de secuencia
   - Estados y transiciones

## Mantenimiento de la Documentación

1. **Actualización**
   - Actualiza la documentación cuando modifiques el código
   - Mantén los ejemplos sincronizados con la implementación
   - Revisa periódicamente la exactitud de la documentación

2. **Buenas Prácticas**
   - Usa un lenguaje claro y conciso
   - Incluye ejemplos de código cuando sea relevante
   - Documenta las decisiones de diseño importantes
   - Mantén los diagramas actualizados

## Plantillas y Ejemplos

Puedes encontrar plantillas completas en:
- `docs/ESTRUCTURA_DOCUMENTACION.md`
- Los archivos generados automáticamente por el script

## Herramientas Recomendadas

- **Editores de Markdown**: VS Code, Typora, o cualquier editor de texto
- **Diagramas**: Mermaid, PlantUML, o dibujos en formato imagen
- **Validación**: Usa un linter de Markdown para mantener la consistencia

## Contribución

1. Crea una rama para tus cambios en la documentación
2. Actualiza la documentación relevante
3. Envía un pull request con una descripción clara de los cambios

## Preguntas Frecuentes

**¿Qué hago si necesito agregar un nuevo tipo de documento?**
1. Actualiza el script `scripts/crear_documentacion.py`
2. Agrega una nueva plantilla al diccionario `TEMPLATES`
3. Documenta el nuevo formato en esta guía

**¿Cómo manejo la documentación de APIs?**
- Para APIs REST, usa el estándar OpenAPI/Swagger
- Documenta los endpoints, parámetros y respuestas
- Incluye ejemplos de solicitudes y respuestas
