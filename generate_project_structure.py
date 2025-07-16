import os
import inspect
from pathlib import Path

# Configuración
PROJECT_ROOT = Path(__file__).parent
OUTPUT_FILE = PROJECT_ROOT / 'PROJECT_STRUCTURE.md'
EXCLUDE_DIRS = {'__pycache__', 'venv', '.git', 'migrations', 'static', 'media', 'templates'}
EXCLUDE_FILES = {'__init__.py', 'settings.py', 'local_settings.py'}

def get_project_structure():
    """Genera la estructura del proyecto en formato Markdown."""
    output = ["# Estructura del Proyecto\n"]
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Filtrar directorios excluidos
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        # Nivel de indentación basado en la profundidad
        level = root.replace(str(PROJECT_ROOT), '').count(os.sep)
        indent = '  ' * level
        
        # Añadir directorio actual
        dir_name = os.path.basename(root)
        if dir_name and not root.endswith(str(PROJECT_ROOT)):
            output.append(f"{indent}- **{dir_name}/**")
        
        # Añadir archivos Python
        py_files = [f for f in files if f.endswith('.py') and f not in EXCLUDE_FILES]
        for file in py_files:
            file_path = Path(root) / file
            module_path = str(file_path.relative_to(PROJECT_ROOT).with_suffix('')).replace('/', '.')
            output.append(f"{indent}  - `{file}`")
            
            # Analizar el módulo para extraer clases y funciones
            try:
                module = __import__(module_path, fromlist=['*'])
                output.extend(analyze_module(module, indent + '    '))
            except Exception as e:
                output.append(f"{indent}    - *Error al analizar el módulo: {e}*")
    
    return '\n'.join(output)

def analyze_module(module, indent=''):
    """Analiza un módulo y devuelve sus clases y funciones."""
    output = []
    
    # Obtener clases
    classes = [m[1] for m in inspect.getmembers(module, inspect.isclass) 
              if m[1].__module__ == module.__name__]
    
    # Obtener funciones
    functions = [m[1] for m in inspect.getmembers(module, inspect.isfunction)
                if m[1].__module__ == module.__name__]
    
    # Documentar clases
    if classes:
        output.append(f"{indent}- **Clases:**")
        for cls in classes:
            # Documentar métodos de la clase
            methods = [m[0] for m in inspect.getmembers(cls, inspect.isfunction)
                      if not m[0].startswith('_') or m[0] == '__init__']
            methods_str = ', '.join(f'`{m}()`' for m in methods)
            docstring = inspect.getdoc(cls) or "Sin documentación"
            output.append(f"{indent}  - `{cls.__name__}`: {docstring}")
            if methods_str:
                output.append(f"{indent}    - *Métodos:* {methods_str}")
    
    # Documentar funciones
    if functions:
        output.append(f"{indent}- **Funciones:**")
        for func in functions:
            docstring = inspect.getdoc(func) or "Sin documentación"
            signature = str(inspect.signature(func))
            output.append(f"{indent}  - `{func.__name__}{signature}`: {docstring}")
    
    return output

def main():
    """Función principal."""
    try:
        structure = get_project_structure()
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(structure)
        print(f"✅ Estructura del proyecto generada en: {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Error al generar la estructura: {e}")

if __name__ == "__main__":
    main()
