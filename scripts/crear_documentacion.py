#!/usr/bin/env python3
"""
Script para generar la estructura de documentación estándar en las aplicaciones del proyecto.
"""
import os
from pathlib import Path

# Plantillas de documentos
TEMPLATES = {
    'README.md': """# {app_name}

## Descripción
[Breve descripción del propósito de la aplicación]

## Características Principales
- Característica 1
- Característica 2
- Característica 3

## Requisitos
- Python 3.8+
- Dependencias (listar)
- Configuración necesaria

## Instalación
```bash
pip install -r requirements.txt
python manage.py migrate
```

## Uso
[Ejemplos de uso básico]

## Documentación Adicional
- [Arquitectura](docs/ARQUITECTURA.md)
- [Flujos de Trabajo](docs/FLUJOS.md)
- [Objetivos](OBJETIVOS.md)
""",

    'OBJETIVOS.md': """# Objetivos de {app_name}

## Objetivo General
[Objetivo principal de la aplicación]

## Objetivos Específicos
- [ ] Objetivo 1
- [ ] Objetivo 2
- [ ] Objetivo 3

## Métricas de Éxito
| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Métrica 1 | Valor | - |
| Métrica 2 | Valor | - |

## Roadmap
- [x] Tarea completada
- [ ] Próxima tarea
- [ ] Tarea futura
""",

    'docs/ARQUITECTURA.md': """# Arquitectura de {app_name}

## Diagrama de Componentes
[Incluir diagrama o descripción de los componentes principales]

## Modelos Principales
- **Modelo1**: Descripción
- **Modelo2**: Descripción

## Dependencias
- Dependencia 1
- Dependencia 2

## Consideraciones de Diseño
[Detalles importantes sobre el diseño]
""",

    'docs/FLUJOS.md': """# Flujos de Trabajo de {app_name}

## Flujo Principal
1. Paso 1
2. Paso 2
3. Paso 3

## Estados y Transiciones
```mermaid
stateDiagram-v2
    [*] --> Estado1
    Estado1 --> Estado2: Evento
    Estado2 --> [*]
```
"""
}

def crear_documentacion(app_name, app_path):
    """Crea la estructura de documentación para una aplicación."""
    print(f"\nCreando documentación para: {app_name}")
    
    # Crear directorio de documentación si no existe
    docs_dir = os.path.join(app_path, 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    
    # Crear archivos de documentación
    for rel_path, content in TEMPLATES.items():
        # Reemplazar nombre de la aplicación en el contenido
        content = content.format(app_name=app_name)
        
        # Crear directorios necesarios
        file_path = os.path.join(app_path, rel_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # No sobrescribir archivos existentes
        if os.path.exists(file_path):
            print(f"  - {rel_path} ya existe, omitiendo...")
            continue
            
        # Escribir el archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  - Creado: {rel_path}")

def main():
    # Directorio raíz del proyecto
    root_dir = Path(__file__).parent.parent
    
    # Obtener todas las aplicaciones de Django
    apps_dir = root_dir
    
    # Excluir directorios que no son aplicaciones
    exclude_dirs = {
        '.git', '.github', '__pycache__', 'venv', '.vscode',
        '.pytest_cache', 'media', 'static', 'logs', 'docs', 'scripts'
    }
    
    print("Iniciando generación de documentación...")
    
    # Procesar cada directorio que parezca una aplicación Django
    for item in os.listdir(apps_dir):
        item_path = os.path.join(apps_dir, item)
        
        # Verificar si es un directorio y no está excluido
        if (
            os.path.isdir(item_path) and 
            not item.startswith('.') and 
            item not in exclude_dirs
        ):
            # Verificar si parece una aplicación Django
            if os.path.exists(os.path.join(item_path, 'apps.py')):
                crear_documentacion(item, item_path)
            else:
                print(f"\nOmitiendo {item} - No parece una aplicación Django")
    
    print("\n¡Documentación generada exitosamente!")
    print("Por favor, completa la información en los archivos generados.")

if __name__ == "__main__":
    main()
