import os
import sys
import django
from django.conf import settings

def test_graph_models():
    # Configurar el entorno de Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
    django.setup()
    
    # Verificar si django_extensions está instalado
    try:
        from django_extensions.management.commands import graph_models
        print("¡El comando graph_models está disponible!")
        
        # Intentar generar un diagrama de prueba
        from django.core.management import call_command
        print("\nGenerando diagrama de prueba...")
        call_command('graph_models', 'bdd', '-o', 'test_diagram.png')
        print("¡Diagrama generado exitosamente como 'test_diagram.png'!")
        
    except ImportError as e:
        print(f"Error al importar graph_models: {e}")
    except Exception as e:
        print(f"Error al generar el diagrama: {e}")

if __name__ == "__main__":
    test_graph_models()
