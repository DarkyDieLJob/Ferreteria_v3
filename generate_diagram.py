import os
import sys
import django
from django.conf import settings
from django.core.management import call_command

def generate_diagram():
    # Configurar el entorno de Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
    django.setup()
    
    print("Generando diagrama para la aplicación 'bdd'...")
    
    # Crear directorio para diagramas si no existe
    output_dir = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'bdd_diagram.png')
    
    # Generar el diagrama usando el comando call_command
    try:
        from django.core.management import call_command
        call_command(
            'graph_models',
            'bdd',
            outputfile=output_file,
            group_models=True,
            all_applications=False,
            exclude_models='BaseModel,TimeStampedModel',
            verbose_name=True,
            inheritance=True,
            use_pygraphviz=True,
            layout='dot'
        )
        print(f"¡Diagrama generado exitosamente en: {output_file}")
        return True
    except Exception as e:
        print(f"Error al generar el diagrama: {e}")
        # Intentar con un enfoque alternativo
        try:
            print("Intentando con enfoque alternativo...")
            from django_extensions.management.commands.graph_models import generate_dot_data
            from django.apps import apps
            
            # Obtener los modelos de la aplicación
            app_models = apps.get_app_config('bdd').get_models()
            
            # Generar el diagrama
            dot_data = generate_dot_data(
                app_models,
                disable_abstract_fields=True,
                group_models=True,
                verbose_names=True,
                inheritance=True
            )
            
            # Guardar el diagrama
            with open(output_file, 'wb') as f:
                import subprocess
                proc = subprocess.Popen(
                    ['dot', '-Tpng', '-o', output_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                proc.communicate(input=dot_data.encode('utf-8'))
                
            print(f"¡Diagrama generado exitosamente (método alternativo) en: {output_file}")
            return True
            
        except Exception as e2:
            print(f"Error con el método alternativo: {e2}")
            return False

def main():
    if generate_diagram():
        print("Proceso completado exitosamente.")
    else:
        print("No se pudo generar el diagrama. Verifica los mensajes de error.")
        sys.exit(1)

if __name__ == "__main__":
    main()
