import os
import subprocess
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from django.contrib import messages
from django.apps import apps

def is_admin(user):
    """Verifica si el usuario es administrador."""
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def uml_dashboard(request):
    """Vista principal del panel de visualización UML."""
    # Obtener todas las aplicaciones instaladas
    installed_apps = [
        app_config for app_config in apps.get_app_configs() 
        if not app_config.name.startswith(('django.', 'rest_framework'))
    ]
    
    context = {
        'installed_apps': installed_apps,
        'title': 'Visualizador UML',
    }
    return render(request, 'uml_visualizer/dashboard.html', context)

@user_passes_test(is_admin)
def generate_diagram(request, app_label):
    """Genera un diagrama UML para una aplicación específica."""
    try:
        # Verificar que la aplicación existe
        app_config = apps.get_app_config(app_label)
        
        # Crear directorio para guardar los diagramas si no existe
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams')
        os.makedirs(output_dir, exist_ok=True)
        
        # Ruta del archivo de salida
        output_file = os.path.join(output_dir, f'{app_label}_diagram.png')
        
        # Comando para generar el diagrama
        command = [
            'python', 'manage.py', 'graph_models',
            app_label,
            '--output', output_file,
            '--pydot',  # Usar pydot para mejor compatibilidad
            '--group-models',  # Agrupar modelos por aplicación
            '--all-applications',  # Incluir relaciones con otras aplicaciones
            '--exclude-models=ContentType,Permission,Group,User,Session,LogEntry',  # Excluir modelos de auth
            '--verbose-names',  # Usar verbose_name en los modelos
            '--rankdir=TB'  # Orientación del gráfico (Top to Bottom)
        ]
        
        # Ejecutar el comando
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR
        )
        
        if result.returncode != 0:
            raise Exception(f"Error al generar el diagrama: {result.stderr}")
        
        # URL relativa al archivo generado
        diagram_url = f"{settings.MEDIA_URL}uml_diagrams/{app_label}_diagram.png"
        
        return render(request, 'uml_visualizer/diagram.html', {
            'app_name': app_config.verbose_name,
            'diagram_url': diagram_url,
            'title': f'Diagrama UML - {app_config.verbose_name}'
        })
        
    except Exception as e:
        messages.error(request, f"Error al generar el diagrama: {str(e)}")
        return redirect('uml_visualizer:uml_dashboard')

@user_passes_test(is_admin)
def project_diagram(request):
    """Genera un diagrama UML de todo el proyecto."""
    try:
        # Crear directorio para guardar los diagramas si no existe
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams')
        os.makedirs(output_dir, exist_ok=True)
        
        # Ruta del archivo de salida
        output_file = os.path.join(output_dir, 'project_diagram.png')
        
        # Comando para generar el diagrama completo
        command = [
            'python', 'manage.py', 'graph_models',
            '--output', output_file,
            '--pydot',
            '--group-models',
            '--all-applications',
            '--exclude-models=ContentType,Permission,Group,User,Session,LogEntry',
            '--verbose-names',
            '--rankdir=LR'  # Orientación de izquierda a derecha para diagramas grandes
        ]
        
        # Ejecutar el comando
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=settings.BASE_DIR
        )
        
        if result.returncode != 0:
            raise Exception(f"Error al generar el diagrama del proyecto: {result.stderr}")
        
        # URL relativa al archivo generado
        diagram_url = f"{settings.MEDIA_URL}uml_diagrams/project_diagram.png"
        
        return render(request, 'uml_visualizer/diagram.html', {
            'app_name': 'Proyecto Completo',
            'diagram_url': diagram_url,
            'title': 'Diagrama UML - Proyecto Completo',
            'is_project_diagram': True
        })
        
    except Exception as e:
        messages.error(request, f"Error al generar el diagrama del proyecto: {str(e)}")
        return redirect('uml_visualizer:uml_dashboard')
