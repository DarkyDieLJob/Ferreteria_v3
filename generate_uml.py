#!/usr/bin/env python3
"""
Script para generar diagramas UML del proyecto Django.
"""
import os
import sys
import django
from django.conf import settings
from django.apps import apps

def configure_django():
    """Configura Django para poder usar sus utilidades."""
    # Configura el módulo de configuración de Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
    
    # Configura la ruta del proyecto
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Configura Django
    django.setup()

def generate_uml(output_file='uml_diagram.png'):
    """Genera un diagrama UML del proyecto."""
    try:
        from django_extensions.management.commands.graph_models import Command as GraphModelsCommand
        from django_extensions.management.modelviz import ModelGraph, generate_dot
        
        print("Generando diagrama UML...")
        
        # Configura las opciones para graph_models
        args = []
        options = {
            'all_applications': True,
            'output': output_file,
            'exclude_models': 'LogEntry,Permission,Group,User,ContentType,Session',
            'verbose_names': True,
            'group_models': True,
            'rankdir': 'TB',
            'arrow_shape': 'normal',
        }
        
        # Crea y ejecuta el comando
        cmd = GraphModelsCommand()
        cmd.handle(*args, **options)
        
        print(f"Diagrama generado exitosamente: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error al generar el diagrama: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Configurando Django...")
    configure_django()
    
    output_file = 'uml_diagram.png'
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    success = generate_uml(output_file)
    sys.exit(0 if success else 1)
