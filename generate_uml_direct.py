#!/usr/bin/env python3
"""
Script para generar diagramas UML de la aplicación 'bdd' usando pygraphviz.
"""
import os
import sys
import django
from django.conf import settings
from django.apps import apps
from django.db import models

def configure_django():
    """Configura Django para poder usar sus utilidades."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
    django.setup()

def get_model_fields(model):
    """Obtiene los campos de un modelo en formato para el diagrama."""
    fields = []
    for field in model._meta.get_fields():
        if field.auto_created and not field.concrete:
            continue
            
        field_type = field.get_internal_type()
        field_name = field.name
        
        # Manejar diferentes tipos de campos
        if hasattr(field, 'related_model') and field.related_model:
            if field.many_to_many:
                field_type = f"ManyToMany({field.related_model.__name__})"
            elif field.one_to_many or field.one_to_one:
                field_type = f"ForeignKey({field.related_model.__name__})"
        
        field_info = f"{field_name}: {field_type}"
        if field.primary_key:
            field_info = f"<u>{field_info}</u>"
            
        fields.append(field_info)
    
    return fields

def generate_bdd_uml(output_file=None):
    """
    Genera un diagrama UML para la aplicación 'bdd'.
    
    Args:
        output_file (str, optional): Ruta del archivo de salida. Si es None, 
                                   se usará 'media/uml_diagrams/bdd_diagram.png'
    """
    try:
        import pygraphviz as pgv
        
        # Configurar la ruta de salida
        if output_file is None:
            output_dir = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, 'bdd_diagram.png')
        
        print(f"Generando diagrama UML para la aplicación 'bdd'...")
        
        # Crea un nuevo grafo
        graph = pgv.AGraph(directed=True, rankdir='TB', splines='ortho')
        graph.node_attr.update(shape='record', style='filled', fillcolor='lightblue')
        
        # Obtiene todos los modelos
        all_models = apps.get_models()
        
        # Añade cada modelo como un nodo
        for model in all_models:
            # Obtiene el nombre de la aplicación y el modelo
            app_label = model._meta.app_label
            model_name = model.__name__
            
            # Obtiene los campos del modelo
            fields = get_model_fields(model)
            
            # Crea la etiqueta para el nodo
            label = f'{{ {model_name} | ' + '\l'.join(fields) + '\l }'
            
            # Añade el nodo al grafo
        
        # Segunda pasada: agregar las relaciones
        print("\nProcesando relaciones entre modelos...")
        for model in models:
            model_name = model.__name__
            for field in model._meta.get_fields():
                # Manejar relaciones ForeignKey
                if (hasattr(field, 'related_model') and 
                    field.related_model and 
                    field.related_model in model_nodes and
                    field.related_model != model):  # Evitar autorreferencias
                    
                    related_model_name = field.related_model.__name__
                    print(f"  Relación encontrada: {model_name} -> {related_model_name} ({field.name})")
                    # Determinar el tipo de relación
                    if field.many_to_many:
                        # Relación muchos a muchos
                        graph.add_edge(
                            model_nodes[model],
                            model_nodes[field.related_model],
                            label=field.name,
                            dir='both',
                            arrowtail='crow',
                            arrowhead='crow',
                            labeldistance='2.0',
                            labelangle='25.0',
                            fontcolor='blue'
                        )
                    elif field.one_to_many:
                        # Relación uno a muchos (ForeignKey)
                        graph.add_edge(
                            model_nodes[model],
                            model_nodes[field.related_model],
                            label=field.name,
                            dir='forward',
                            arrowtail='none',
                            arrowhead='crow',
                            labeldistance='2.0',
                            labelangle='25.0',
                            fontcolor='green'
                        )
                    elif field.one_to_one:
                        # Relación uno a uno
                        graph.add_edge(
                            model_nodes[model],
                            model_nodes[field.related_model],
                            label=field.name,
                            dir='both',
                            arrowtail='tee',
                            arrowhead='tee',
                            labeldistance='2.0',
                            fontcolor='red'
                        )
        
        # Ajustar el diseño del grafo
        graph.layout(prog='dot')
        
        # Generar la imagen
        graph.draw(output_file, format='png')
        
        print(f"¡Diagrama generado exitosamente en: {output_file}")
        return True
        
    except ImportError:
        print("Error: pygraphviz no está instalado. Instálalo con: pip install pygraphviz")
        return False
    except Exception as e:
        import traceback
        print(f"Error al generar el diagrama: {e}")
        print("Detalles:")
        traceback.print_exc()
        return False

def main():
    print("Configurando Django...")
    configure_django()
    
    # Generar el diagrama
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    if not generate_bdd_uml(output_file):
        sys.exit(1)

if __name__ == "__main__":
    main()
