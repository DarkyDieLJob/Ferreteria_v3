import os
import re
import subprocess
import tempfile
import shutil
import datetime
import json
import logging
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, JsonResponse, FileResponse
from django.contrib import messages
from django.urls import reverse
from django.apps import apps
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from .project_analyzer import ProjectAnalyzer

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(settings.BASE_DIR, 'uml_visualizer.log')
)

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def uml_dashboard(request):
    """
    Vista del panel de control que muestra todas las aplicaciones instaladas.
    """
    logger.info("Iniciando vista uml_dashboard")
    
    if not request.user.is_staff:
        logger.warning(f"Intento de acceso no autorizado a uml_dashboard por el usuario {request.user}")
        messages.error(request, 'Acceso denegado. Se requieren permisos de administrador.')
        return redirect('admin:login')
    
    try:
        logger.debug("Inicializando analizador de proyecto")
        analyzer = ProjectAnalyzer()
        project_structure = analyzer.get_project_structure()
        
        # Obtener información de las aplicaciones
        installed_apps = []
        total_models = 0
        total_views = 0
        total_forms = 0
        
        logger.debug("Obteniendo configuración de aplicaciones")
        for app_config in apps.get_app_configs():
            # Saltar aplicaciones del sistema y de terceros
            if any(app_config.name.startswith(pkg) for pkg in 
                  ['django.', 'rest_framework', 'debug_toolbar', 'allauth']):
                logger.debug(f"Saltando aplicación del sistema: {app_config.name}")
                continue
            
            try:
                app_path = Path(app_config.path)
                if not analyzer._is_in_project_dir(app_path):
                    logger.debug(f"Saltando aplicación fuera del directorio del proyecto: {app_config.name}")
                    continue
                
                # Obtener estadísticas de la aplicación
                app_stats = {
                    'label': app_config.label,
                    'name': app_config.verbose_name or app_config.label.title(),
                    'models': [],
                    'model_count': 0,
                    'view_count': 0,
                    'form_count': 0,
                    'has_diagram': False
                }
                
                logger.debug(f"Procesando aplicación: {app_stats['name']}")
                
                # Contar modelos
                try:
                    app_models = list(app_config.get_models())
                    app_stats['model_count'] = len(app_models)
                    app_stats['models'] = [{
                        'name': model.__name__,
                        'verbose_name': getattr(model._meta, 'verbose_name', model.__name__)
                    } for model in app_models]
                    total_models += app_stats['model_count']
                    logger.debug(f"  - Modelos encontrados: {app_stats['model_count']}")
                    
                    # Contar vistas (asumiendo que están en views.py)
                    try:
                        views_path = os.path.join(app_config.path, 'views.py')
                        if os.path.exists(views_path):
                            with open(views_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Contar clases de vista (simplificado)
                                view_count = content.count('class ') - content.count('class Meta')
                                app_stats['view_count'] = max(0, view_count)
                                total_views += app_stats['view_count']
                    except Exception as e:
                        logger.warning(f"No se pudieron contar las vistas para {app_config.name}: {str(e)}")
                    
                    # Contar formularios (asumiendo que están en forms.py)
                    try:
                        forms_path = os.path.join(app_config.path, 'forms.py')
                        if os.path.exists(forms_path):
                            with open(forms_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                # Contar clases de formulario (simplificado)
                                form_count = content.count('class ')
                                app_stats['form_count'] = max(0, form_count)
                                total_forms += app_stats['form_count']
                    except Exception as e:
                        logger.warning(f"No se pudieron contar los formularios para {app_config.name}: {str(e)}")
                        
                except Exception as e:
                    logger.error(f"Error al obtener modelos para {app_config.name}: {str(e)}", exc_info=True)
                
                # Verificar si existe el diagrama
                diagram_path = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams', f"{app_config.label}_diagram.png")
                app_stats['has_diagram'] = os.path.exists(diagram_path)
                
                installed_apps.append(app_stats)
            except Exception as e:
                logger.error(f"Error al procesar la aplicación {app_config.name}: {str(e)}", exc_info=True)
                continue
    
        # Ordenar aplicaciones por nombre
        installed_apps.sort(key=lambda x: x['name'].lower())
        
        # Obtener estadísticas generales
        context = {
            'installed_apps': installed_apps,
            'total_apps': len(installed_apps),  # Añadido contador de aplicaciones
            'total_models': total_models,
            'total_views': total_views,
            'total_forms': total_forms,
            'title': 'Dashboard de Visualización UML',
            'current_page': 'dashboard',
            'site_title': 'Visualizador UML',
            'site_header': 'Visualizador UML',
        }
        
        logger.info(f"Dashboard generado con éxito. Aplicaciones: {len(installed_apps)}, Modelos: {total_models}")
        return render(request, 'uml_visualizer/dashboard.html', context)
        
    except Exception as e:
        logger.error(f"Error en uml_dashboard: {str(e)}", exc_info=True)
        messages.error(request, 'Ocurrió un error al cargar el dashboard.')
        return redirect('admin:index')

def generate_app_diagram(app_label, output_file):
    """
    Genera un diagrama UML para una aplicación específica.
    
    Args:
        app_label (str): Etiqueta de la aplicación
        output_file (str): Ruta completa del archivo de salida
        
    Returns:
        bool: True si se generó correctamente, False en caso contrario
        str: Mensaje de error en caso de fallo
    """
    try:
        # Verificar que la aplicación existe
        apps.get_app_config(app_label)
        
        # Crear directorio si no existe
        output_dir = os.path.dirname(output_file)
        os.makedirs(output_dir, exist_ok=True)
        
        # Comando para generar el diagrama
        cmd = [
            'python', 'manage.py', 'graph_models',
            app_label,  # Only include the specified app
            '--output', output_file,
            '--pydot',
            '--group-models',
            '--exclude-models=ContentType,Permission,Group,User,Session,LogEntry',
            '--verbose-names',
            '--rankdir=TB',
            '--arrow-shape=normal',
            '--disable-sort-fields',
            '--hide-relations-from-fields',
            '--no-inheritance'  # Cleaner diagrams for single apps
        ]
        
        # Ejecutar el comando
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            error_msg = result.stderr or 'Error desconocido al generar el diagrama'
            return False, error_msg
            
        if not os.path.exists(output_file):
            return False, 'No se pudo generar el archivo del diagrama'
            
        return True, None
        
    except LookupError:
        return False, f'No se encontró la aplicación: {app_label}'
    except Exception as e:
        return False, f'Error inesperado: {str(e)}'

def generate_diagram(app_label, output_file_base, all_apps=False):
    """
    Genera tres diagramas UML para una aplicación o para todo el proyecto:
    1. Diagrama de modelos
    2. Diagrama de vistas
    3. Diagrama de formularios
    
    Args:
        app_label (str): Nombre de la aplicación o None para todo el proyecto
        output_file_base (str): Ruta base del archivo de salida (sin extensión)
        all_apps (bool): Si es True, genera el diagrama de todo el proyecto
        
    Returns:
        tuple: (éxito, mensaje_de_error, diagramas)
    """
    # Configurar logging para esta función
    import logging
    logger = logging.getLogger('uml_visualizer')
    handler = logging.FileHandler('/home/fedora/Documentos/GitHub/Ferreteria_v3/logs/uml_visualizer/diagram_generation.log')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    
    logger.info("=" * 80)
    logger.info(f"INICIANDO GENERACIÓN DE DIAGRAMAS")
    logger.info(f"app_label: {app_label}")
    logger.info(f"output_file_base: {output_file_base}")
    logger.info(f"all_apps: {all_apps}")
    logger.info("-" * 80)
    
    # Crear directorio si no existe
    output_dir = os.path.dirname(output_file_base)
    os.makedirs(output_dir, exist_ok=True)
    
    # Diccionario para almacenar las rutas de los diagramas generados
    diagram_paths = {
        'models': None,
        'views': None,
        'forms': None
    }
    
    # 1. Generar diagrama de modelos
    models_output = f"{output_file_base}_models.png"
    temp_dot_file = os.path.join(tempfile.gettempdir(), f'temp_models_{os.getpid()}.dot')
    
    logger.info("1/3 - Generando diagrama de modelos...")
    success, error_msg = _generate_models_diagram(app_label, temp_dot_file, models_output, all_apps)
    if not success:
        return False, error_msg, diagram_paths
    diagram_paths['models'] = models_output
    
    # 2. Generar diagrama de vistas
    views_output = f"{output_file_base}_views.png"
    logger.info("2/3 - Generando diagrama de vistas...")
    success, error_msg = _generate_views_diagram(app_label, views_output, all_apps)
    if not success:
        logger.warning(f"Advertencia al generar diagrama de vistas: {error_msg}")
        # Continuamos aunque falle la generación de vistas
    else:
        diagram_paths['views'] = views_output
    
    # 3. Generar diagrama de formularios
    forms_output = f"{output_file_base}_forms.png"
    logger.info("3/3 - Generando diagrama de formularios...")
    success, error_msg = _generate_forms_diagram(app_label, forms_output, all_apps)
    if not success:
        logger.warning(f"Advertencia al generar diagrama de formularios: {error_msg}")
        # Continuamos aunque falle la generación de formularios
    else:
        diagram_paths['forms'] = forms_output
    
    logger.info("Generación de diagramas completada exitosamente")
    return True, "Diagramas generados correctamente", diagram_paths

def _generate_models_diagram(app_label, temp_dot_file, output_file, all_apps):
    """Genera el diagrama de modelos usando django-extensions graph_models"""
    logger = logging.getLogger('uml_visualizer')
    
    # Comando base para modelos
    cmd_models = [
        'python', 'manage.py', 'graph_models',
        '--output', temp_dot_file,
        '--pydot',
        '--group-models',
        '--exclude-models=ContentType,Permission,Group,User,Session,LogEntry',
        '--verbose-names',
        '--rankdir=TB',
        '--arrow-shape=normal',
        '--disable-sort-fields',
        '--hide-relations-from-fields',
        '--disable-abstract-fields'
    ]
    
    if all_apps:
        cmd_models.append('--all-applications')
    else:
        cmd_models.append(app_label)
    
    logger.info(f"Ejecutando comando de modelos: {' '.join(cmd_models)}")
    
    try:
        result = subprocess.run(
            cmd_models, 
            capture_output=True, 
            text=True, 
            cwd=settings.BASE_DIR,
            check=False
        )
        
        if result.returncode != 0 or not os.path.exists(temp_dot_file):
            error_msg = result.stderr or 'Error desconocido al generar el diagrama de modelos'
            logger.error(f"Error en graph_models: {error_msg}")
            return False, error_msg
            
        # Convertir el archivo DOT a PNG
        _convert_dot_to_png(temp_dot_file, output_file)
        return True, ""
        
    except Exception as e:
        error_msg = f"Error al generar diagrama de modelos: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_dot_file):
            os.remove(temp_dot_file)

def _generate_views_diagram(app_label, output_file, all_apps):
    """Genera un diagrama de las vistas de la aplicación"""
    logger = logging.getLogger('uml_visualizer')
    temp_dot_file = os.path.join(tempfile.gettempdir(), f'temp_views_{os.getpid()}.dot')
    
    try:
        # Obtener todas las aplicaciones o solo la especificada
        if all_apps:
            apps_to_check = [app_config for app_config in apps.get_app_configs() 
                           if app_config.name != 'django.contrib.admin']
        else:
            apps_to_check = [apps.get_app_config(app_label)]
        
        # Generar contenido DOT para las vistas
        dot_content = ['digraph views_diagram {',
                      '  rankdir=TB;',
                      '  node [fontname=Roboto, fontsize=10, shape=box, style=filled, color=lightblue];',
                      '  edge [fontname=Roboto, fontsize=8];',
                      '  graph [fontname=Roboto, fontsize=12];',
                      '  subgraph cluster_views {',
                      '    label = "Vistas";',
                      '    style=filled;',
                      '    color=lightgrey;',
                      '    node [style=filled, color=white];']
        
        # Buscar vistas en cada aplicación
        for app_config in apps_to_check:
            views_path = os.path.join(app_config.path, 'views.py')
            if os.path.exists(views_path):
                with open(views_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Buscar clases de vista (incluyendo vistas basadas en clases y funciones)
                    view_patterns = [
                        # Vistas basadas en clases (que heredan de View o mixins)
                        r'class\s+([A-Za-z0-9_]+)\s*\(\s*([a-zA-Z0-9_.]*\s*,\s*)*([a-zA-Z0-9_.]*View|TemplateView|ListView|DetailView|CreateView|UpdateView|DeleteView|FormView|View|LoginView|LogoutView|RedirectView)',
                        # Vistas basadas en funciones con decorador @login_required o @permission_required
                        r'@(login_required|permission_required|require_http_methods).*?\n\s*def\s+([a-z0-9_]+)\s*\('
                    ]
                    
                    view_names = set()
                    
                    # Buscar vistas basadas en clases
                    class_pattern = view_patterns[0]
                    class_matches = re.findall(class_pattern, content)
                    for match in class_matches:
                        view_name = match[0]
                        view_names.add((view_name, 'class'))
                    
                    # Buscar vistas basadas en funciones con decoradores comunes
                    func_pattern = view_patterns[1]
                    func_matches = re.findall(func_pattern, content, re.DOTALL)
                    for match in func_matches:
                        if isinstance(match, tuple):
                            view_name = match[1]  # El nombre de la función está en el segundo grupo
                        else:
                            view_name = match
                        view_names.add((view_name, 'function'))
                    
                    # Agregar las vistas encontradas al diagrama
                    for view_name, view_type in view_names:
                        node_id = f"{app_config.label}_{view_name}"
                        color = "#d4f1f9" if view_type == 'class' else "#e8f5e9"
                        dot_content.append(f'    {node_id} [label="{view_name}\n({app_config.label} - {view_type})", style="filled", color="{color}"];')
        
        dot_content.extend(['  }', '}'])
        
        # Verificar si se encontraron vistas
        if len(dot_content) <= 10:  # Solo hay elementos de formato, no hay vistas
            logger.warning(f"No se encontraron vistas en la aplicación {app_label}")
            # Crear un archivo DOT vacío con un mensaje
            dot_content = [
                'digraph no_views {',
                '  node [fontname=Roboto, fontsize=12, shape=box, style=filled, color=lightgrey];',
                '  label = "No se encontraron vistas en esta aplicación";',
                '  "No hay vistas" [label="No se encontraron vistas\n(verifique el archivo views.py)"];',
                '}'
            ]
        
        # Guardar archivo DOT
        with open(temp_dot_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dot_content))
        
        # Convertir a PNG
        _convert_dot_to_png(temp_dot_file, output_file)
        return True, ""
        
    except Exception as e:
        error_msg = f"Error al generar diagrama de vistas: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
    finally:
        if os.path.exists(temp_dot_file):
            os.remove(temp_dot_file)

def _generate_forms_diagram(app_label, output_file, all_apps):
    """Genera un diagrama de los formularios de la aplicación"""
    logger = logging.getLogger('uml_visualizer')
    temp_dot_file = os.path.join(tempfile.gettempdir(), f'temp_forms_{os.getpid()}.dot')
    
    try:
        # Obtener todas las aplicaciones o solo la especificada
        if all_apps:
            apps_to_check = [app_config for app_config in apps.get_app_configs() 
                           if app_config.name != 'django.contrib.admin']
        else:
            apps_to_check = [apps.get_app_config(app_label)]
        
        # Generar contenido DOT para los formularios
        dot_content = ['digraph forms_diagram {',
                      '  rankdir=TB;',
                      '  node [fontname=Roboto, fontsize=10, shape=ellipse, style=filled, color=lightgreen];',
                      '  edge [fontname=Roboto, fontsize=8];',
                      '  graph [fontname=Roboto, fontsize=12];',
                      '  subgraph cluster_forms {',
                      '    label = "Formularios";',
                      '    style=filled;',
                      '    color=lightgrey;',
                      '    node [style=filled, color=white];']
        
        # Buscar formularios en cada aplicación
        for app_config in apps_to_check:
            forms_path = os.path.join(app_config.path, 'forms.py')
            if os.path.exists(forms_path):
                with open(forms_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Buscar clases de formulario
                    form_pattern = r'class\s+([A-Za-z0-9_]+)\s*\(\s*([a-zA-Z0-9_.]*\s*,\s*)*(forms\.ModelForm|forms\.Form|ModelForm|Form)'
                    form_matches = re.findall(form_pattern, content)
                    
                    for match in form_matches:
                        form_name = match[0]
                        node_id = f"{app_config.label}_{form_name}"
                        dot_content.append(f'    {node_id} [label="{form_name}\n({app_config.label})"];')
        
        dot_content.extend(['  }', '}'])
        
        # Guardar archivo DOT
        with open(temp_dot_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(dot_content))
        
        # Convertir a PNG
        _convert_dot_to_png(temp_dot_file, output_file)
        return True, ""
        
    except Exception as e:
        error_msg = f"Error al generar diagrama de formularios: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
    finally:
        if os.path.exists(temp_dot_file):
            os.remove(temp_dot_file)

def _convert_dot_to_png(dot_file, output_file):
    """Convierte un archivo DOT a PNG"""
    try:
        # Usar el comando dot para convertir a PNG
        cmd = ['dot', '-Tpng', '-o', output_file, dot_file]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error al convertir DOT a PNG: {e.stderr}")
        return False
            
        logger.info(f"Archivo DOT generado correctamente: {os.path.getsize(temp_dot_file)} bytes")
        
    except Exception as e:
        error_msg = f"Error al ejecutar graph_models: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
        
    # Leer el contenido del archivo DOT generado
    try:
        with open(temp_dot_file, 'r', encoding='utf-8') as f:
            dot_content = f.read()
        
        logger.info(f"Tamaño del archivo DOT original: {len(dot_content)} caracteres")
        logger.debug(f"Primeros 200 caracteres del DOT: {dot_content[:200]}...")
        
        if not dot_content.strip():
            error_msg = "El archivo DOT generado está vacío"
            logger.error(error_msg)
            return False, error_msg
            
    except Exception as e:
        error_msg = f"Error al leer el archivo DOT temporal: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return False, error_msg
    
    # Procesar el contenido para agregar vistas y formularios
    logger.info("="*50 + " INICIO DE GENERACIÓN DE DIAGRAMA " + "="*50)
    logger.info("Iniciando análisis del proyecto para encontrar vistas y formularios...")
    logger.info(f"Directorio de trabajo actual: {os.getcwd()}")
    logger.info(f"Directorio del proyecto: {settings.BASE_DIR}")
    
    # Obtener la estructura del proyecto
    analyzer = ProjectAnalyzer()
    project_structure = analyzer.get_project_structure()
    
    # Registrar información sobre las aplicaciones encontradas
    apps_found = project_structure.get('apps', {})
    logger.info(f"Aplicaciones encontradas: {len(apps_found)}")
    for app_name, app_data in apps_found.items():
        logger.info(f"- {app_name}: {app_data.get('path', 'sin ruta')}")
    
    # Guardar la estructura completa en el log de depuración
    debug_log_path = os.path.join(settings.BASE_DIR, 'logs', 'uml_visualizer', 'project_structure_debug.log')
    os.makedirs(os.path.dirname(debug_log_path), exist_ok=True)
    with open(debug_log_path, 'w', encoding='utf-8') as f:
        json.dump(project_structure, f, indent=2, default=str, ensure_ascii=False)
    
    logger.info(f"Estructura completa del proyecto guardada en: {debug_log_path}")
    logger.info("-"*100)
    
    # Procesar vistas
    views_dot = '\n  // Vistas\n  subgraph cluster_views {\n    label = "Vistas";\n    node [shape=box, style=filled, color=lightblue, fontname=Arial];\n'
    # Inicializar DOT para formularios
    forms_dot = '\n  // Formularios\n  subgraph cluster_forms {\n    label = "Formularios";\n    node [shape=ellipse, style=filled, color=lightgreen, fontname=Arial];\n'
    view_count = 0
    form_count = 0
    apps_with_views = 0
    apps_with_forms = 0
    
    for app_name, app_data in project_structure.get('apps', {}).items():
        # Procesar vistas
        views_path = os.path.join(app_data['path'], 'views.py')
        logger.debug(f"Buscando vistas en: {views_path}")
        
        if os.path.exists(views_path):
            try:
                with open(views_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Buscar clases de vista (patrón mejorado)
                    import re
                    # Patrón para encontrar clases que heredan de vistas de Django
                    view_pattern = r'class\s+([A-Za-z0-9_]+)\s*\(\s*([a-zA-Z0-9_.]*\s*,\s*)*([a-zA-Z0-9_.]*View|TemplateView|ListView|DetailView|CreateView|UpdateView|DeleteView|FormView)'
                    view_matches = re.findall(view_pattern, content)
                    view_classes = [v[0] for v in view_matches]  # Tomar solo el nombre de la clase
                    
                    if view_classes:
                        apps_with_views += 1
                        logger.info(f"Aplicación {app_name} - Vistas encontradas: {view_classes}")
                        
                        for view_class in view_classes:
                            node_id = f"{app_name}_{view_class}"
                            node_label = f"{view_class}\n({app_name}.views)"
                            views_dot += f'    {node_id} [label="{node_label}"];\n'
                            # Agregar relaciones con los modelos que usa la vista
                            model_refs = re.findall(r'(?:model|queryset)\s*=\s*([A-Za-z0-9_]+)|get_queryset\s*\([^)]*\)\s*{[^}]*\.objects\.(?:all|filter)\([^)]*\b([A-Za-z0-9_]+)', content, re.DOTALL)
                            for ref in model_refs:
                                model_ref = next((m for m in ref if m), None)
                                if model_ref and not model_ref.startswith(('self', 'cls')):
                                    views_dot += f'    {node_id} -> "{model_ref}" [style=dashed, color=blue, arrowhead=vee];\n'
                            view_count += 1
                    else:
                        logger.debug(f"No se encontraron vistas en {views_path} que coincidan con el patrón")
            except Exception as e:
                logger.error(f"Error al procesar vistas en {views_path}: {str(e)}", exc_info=True)
        
        # Procesar formularios
        forms_path = os.path.join(app_data['path'], 'forms.py')
        logger.debug(f"Buscando formularios en: {forms_path}")
        
        if os.path.exists(forms_path):
            try:
                with open(forms_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Buscar clases de formulario
                    # Patrón para encontrar clases que heredan de formularios de Django
                    form_pattern = r'class\s+([A-Za-z0-9_]+)\s*\(\s*([a-zA-Z0-9_.]*\s*,\s*)*(forms\.ModelForm|forms\.Form|ModelForm|Form)'
                    form_matches = re.findall(form_pattern, content)
                    form_classes = [f[0] for f in form_matches]  # Tomar solo el nombre de la clase
                    
                    if form_classes:
                        apps_with_forms += 1
                        logger.info(f"Aplicación {app_name} - Formularios encontrados: {form_classes}")
                        
                        for form_class in form_classes:
                            node_id = f"{app_name}_{form_class}"
                            node_label = f"{form_class}\n({app_name}.forms)"
                            forms_dot += f'    {node_id} [label="{node_label}"];\n'
                            # Buscar relaciones con modelos
                            model_refs = re.findall(r'class\s+Meta[^:]*:\s*model\s*=\s*([A-Za-z0-9_]+)', content, re.DOTALL)
                            for model_ref in model_refs:
                                if model_ref and not model_ref.startswith(('self', 'cls')):
                                    forms_dot += f'    {node_id} -> "{model_ref}" [style=dashed, color=green, arrowhead=vee];\n'
                            form_count += 1
                    else:
                        logger.debug(f"No se encontraron formularios en {forms_path} que coincidan con el patrón")
            except Exception as e:
                logger.error(f"Error al procesar formularios en {forms_path}: {str(e)}", exc_info=True)
    
    # Cerrar los subgrafos
    views_dot += '  }\n'
    # Si no se encontraron formularios, no incluir el subgrafo
    if form_count > 0:
        forms_dot += '  }\n'
    else:
        forms_dot = '  // No se encontraron formularios\n'
    logger.info(f"Total de aplicaciones con vistas: {apps_with_views}")
    logger.info(f"Total de vistas encontradas: {view_count}")
    logger.info(f"Total de aplicaciones con formularios: {apps_with_forms}")
    logger.info(f"Total de formularios encontrados: {form_count}")
                    
    # Insertar las definiciones de vistas y formularios antes del cierre del grafo
    if '}' in dot_content:
        try:
            # Guardar una copia del contenido original para depuración
            original_content = dot_content
            
            # Guardar el contenido original en un archivo de depuración
            debug_original_path = os.path.join(settings.BASE_DIR, 'logs', 'uml_visualizer', 'original_dot_content.dot')
            with open(debug_original_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            logger.info(f"Contenido DOT original guardado en: {debug_original_path}")
            
            # Guardar las definiciones de vistas y formularios
            debug_views_path = os.path.join(settings.BASE_DIR, 'logs', 'uml_visualizer', 'views_dot_content.dot')
            with open(debug_views_path, 'w', encoding='utf-8') as f:
                f.write(views_dot)
            logger.info(f"Definiciones de vistas guardadas en: {debug_views_path}")
            
            debug_forms_path = os.path.join(settings.BASE_DIR, 'logs', 'uml_visualizer', 'forms_dot_content.dot')
            with open(debug_forms_path, 'w', encoding='utf-8') as f:
                f.write(forms_dot)
            logger.info(f"Definiciones de formularios guardadas en: {debug_forms_path}")
            
            # Dividir el contenido en líneas para mejor manipulación
            lines = dot_content.splitlines()
            logger.info(f"Archivo DOT original: {len(lines)} líneas")
            
            # Encontrar la última llave de cierre
            last_brace_idx = len(lines) - 1 - lines[::-1].index('}')
            logger.info(f"Última llave de cierre encontrada en la línea {last_brace_idx + 1}")
            
            # Insertar las definiciones antes de la última llave
            modified_lines = lines[:last_brace_idx]
            modified_lines.append('')  # Línea en blanco
            modified_lines.extend(['  // Secciones agregadas por el visualizador UML', ''])
            modified_lines.extend(views_dot.splitlines())
            modified_lines.extend(forms_dot.splitlines())
            modified_lines.append('}')  # Cerrar el grafo
            
            # Unir todo de nuevo
            dot_content = '\n'.join(modified_lines)
            
            # Guardar el contenido modificado
            debug_modified_path = os.path.join(settings.BASE_DIR, 'logs', 'uml_visualizer', 'modified_dot_content.dot')
            with open(debug_modified_path, 'w', encoding='utf-8') as f:
                f.write(dot_content)
            logger.info(f"Contenido DOT modificado guardado en: {debug_modified_path}")
            
            logger.info(f"Tamaño del archivo DOT modificado: {len(dot_content)} caracteres")
            logger.info("-"*100)
            logger.info("VISTAS ENCONTRADAS:" + "\n" + views_dot)
            logger.info("-"*100)
            logger.info("FORMULARIOS ENCONTRADOS:" + "\n" + forms_dot)
            logger.info("-"*100)
            
        except Exception as e:
            logger.error(f"Error al modificar el contenido DOT: {str(e)}", exc_info=True)
            # Continuar con el contenido original si hay un error
            dot_content = original_content
    
    # Escribir el contenido modificado al archivo final
    dot_output_file = output_file
    if dot_output_file.endswith('.png'):
        dot_output_file = os.path.splitext(dot_output_file)[0] + '.dot'
    
    try:
        with open(dot_output_file, 'w', encoding='utf-8') as f_out:
            f_out.write(dot_content)
        
        logger.info(f"Archivo DOT guardado en: {dot_output_file} - Tamaño: {os.path.getsize(dot_output_file)} bytes")
        
        # Si el archivo de salida es PNG, convertir el DOT a PNG
        if output_file.endswith('png'):
            logger.info(f"Convirtiendo {dot_output_file} a PNG: {output_file}")
            
            try:
                # Verificar si dot está instalado
                dot_check = subprocess.run(['which', 'dot'], capture_output=True, text=True)
                if dot_check.returncode != 0:
                    raise Exception("El comando 'dot' no está instalado. Instala Graphviz.")
                
                dot_cmd = ['dot', '-Tpng', '-o', output_file, dot_output_file]
                logger.info(f"Ejecutando: {' '.join(dot_cmd)}")
                
                result = subprocess.run(
                    dot_cmd, 
                    capture_output=True, 
                    text=True,
                    cwd=os.path.dirname(output_file) or None
                )
                
                if result.returncode != 0:
                    error_msg = f'Error al convertir DOT a PNG: {result.stderr}'
                    logger.error(error_msg)
                    return False, f'Error al generar la imagen: {error_msg}'
                
                logger.info(f"Archivo PNG generado correctamente: {output_file} - Tamaño: {os.path.getsize(output_file)} bytes")
                
            except Exception as e:
                error_msg = f'Error al ejecutar el comando dot: {str(e)}'
                logger.error(error_msg, exc_info=True)
                return False, f'Error al generar el diagrama: {error_msg}'
            
            # Eliminar el archivo temporal
            try:
                if os.path.exists(temp_dot_file):
                    os.remove(temp_dot_file)
                    logger.debug(f"Archivo temporal eliminado: {temp_dot_file}")
            except Exception as e:
                logger.warning(f'No se pudo eliminar el archivo temporal {temp_dot_file}: {str(e)}')
            
            logger.info("Proceso de generación de diagrama completado con éxito")
            return True, None
        
        return True, None
            
    except Exception as e:
        error_msg = f'Error al escribir el archivo de salida: {str(e)}'
        logger.error(error_msg, exc_info=True)
        return False, error_msg

@user_passes_test(is_admin)
def app_diagram(request, app_label):
    """
    Vista para mostrar los diagramas de una aplicación específica.
    Muestra tres diagramas: modelos, vistas y formularios.
    """
    # Inicializar variables
    success = True
    error_msg = None
    diagrams = {}
    
    try:
        app_config = apps.get_app_config(app_label)
        app_name = app_config.verbose_name or app_label
        
        # Obtener información de los modelos de forma segura
        model_info = []
        for model in app_config.get_models():
            model_info.append({
                'name': model.__name__,
                'verbose_name': getattr(model._meta, 'verbose_name', model.__name__),
                'verbose_name_plural': getattr(model._meta, 'verbose_name_plural', f"{model.__name__}s"),
            })
        
        # Configuración de rutas
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams')
        os.makedirs(output_dir, exist_ok=True)
        
        # Base del nombre de archivo sin extensión
        output_file_base = os.path.join(output_dir, app_label)
        
        # Verificar si se solicitó generar los diagramas
        generate = request.GET.get('generate', 'false').lower() == 'true'
        
        # Diccionario para almacenar las URLs de los diagramas
        diagram_urls = {
            'models': None,
            'views': None,
            'forms': None
        }
        
        # Generar los diagramas solo si se solicita o si no existen
        if generate or not all(os.path.exists(f"{output_file_base}_{diag_type}.png") for diag_type in diagram_urls.keys()):
            success, error_msg, diagrams = generate_diagram(app_label, output_file_base, all_apps=False)
            if not success:
                messages.error(request, f"Error al generar los diagramas: {error_msg}")
        else:
            # Si los archivos existen, solo construimos las rutas
            diagrams = {}
            for diag_type in diagram_urls.keys():
                diag_path = f"{output_file_base}_{diag_type}.png"
                if os.path.exists(diag_path):
                    diagrams[diag_type] = diag_path
        
        # Construir las URLs de los diagramas generados
        for diag_type, diag_path in diagrams.items():
            if diag_path and os.path.exists(diag_path):
                rel_path = os.path.relpath(diag_path, settings.MEDIA_ROOT)
                diagram_urls[diag_type] = os.path.join(settings.MEDIA_URL, rel_path)
        
        # Obtener fechas de modificación para cache-busting
        last_modified = {}
        for diag_type in diagram_urls:
            diag_path = f"{output_file_base}_{diag_type}.png"
            if os.path.exists(diag_path):
                last_modified[diag_type] = os.path.getmtime(diag_path)
        
        context = {
            'title': f'Diagramas - {app_name}',
            'app_label': app_label,
            'app_name': app_name,
            'models': model_info,
            'diagram_urls': diagram_urls,
            'last_modified': last_modified,
            'site_title': 'Visualizador UML',
            'site_header': 'Visualizador UML',
            'site_url': '/uml/',
            'is_app_diagram': True,
            'has_diagrams': any(diagram_urls.values())  # Para saber si hay al menos un diagrama
        }
        
        if not success:
            messages.error(request, f"Error al generar el diagrama: {error_msg}")
        
        return render(request, 'uml_visualizer/diagram.html', context)
        
    except LookupError:
        raise Http404(f"La aplicación '{app_label}' no existe")

@user_passes_test(is_admin)
def download_diagram(request, app_label):
    """
    Vista para descargar el diagrama de una aplicación o del proyecto completo.
    
    Args:
        request: Objeto HttpRequest
        app_label: Nombre de la aplicación o 'project' para el diagrama completo
    """
    try:
        is_project = app_label.lower() == 'project'
        
        if is_project:
            # Ruta al archivo del diagrama del proyecto
            filename = 'project_diagram.png'
            output_file = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams', filename)
            
            # Si el archivo no existe, generarlo
            if not os.path.exists(output_file):
                success, error_msg = generate_diagram(None, output_file, all_apps=True)
                if not success:
                    messages.error(request, f"Error al generar el diagrama: {error_msg}")
                    return redirect('uml_visualizer:project_diagram')
        else:
            # Verificar que la aplicación existe
            app_config = apps.get_app_config(app_label)
            
            # Ruta al archivo del diagrama de la aplicación
            filename = f'{app_label}_diagram.png'
            output_file = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams', filename)
            
            # Si el archivo no existe, generarlo
            if not os.path.exists(output_file):
                success, error_msg = generate_diagram(app_label, output_file, all_apps=False)
                if not success:
                    messages.error(request, f"Error al generar el diagrama: {error_msg}")
                    return redirect('uml_visualizer:app_diagram', app_label=app_label)
        
        # Leer el archivo y devolverlo como respuesta
        with open(output_file, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/png')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
    except LookupError:
        raise Http404(f"La aplicación '{app_label}' no existe")
    except Exception as e:
        messages.error(request, f"Error al descargar el diagrama: {str(e)}")
        if is_project:
            return redirect('uml_visualizer:project_diagram')
        return redirect('uml_visualizer:app_diagram', app_label=app_label)

@user_passes_test(is_admin)
def project_diagram(request):
    """
    Vista para mostrar el diagrama completo del proyecto con información detallada.
    """
    try:
        # Ruta al archivo del diagrama del proyecto
        filename = 'project_diagram.png'
        output_file = os.path.join(settings.MEDIA_ROOT, 'uml_diagrams', filename)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Verificar si se debe regenerar el diagrama
        generate = request.GET.get('generate', 'false').lower() == 'true'
        
        # Generar el diagrama si no existe o se solicita regenerar
        if generate or not os.path.exists(output_file):
            success, error_msg = generate_diagram(None, output_file, all_apps=True)
            if not success:
                messages.error(request, f"Error al generar el diagrama: {error_msg}")
                return redirect('uml_visualizer:dashboard')
        
        # Obtener información de la última modificación
        last_modified = None
        if os.path.exists(output_file):
            last_modified = os.path.getmtime(output_file)
        
        # Obtener información detallada del proyecto
        analyzer = ProjectAnalyzer()
        project_structure = analyzer.get_project_structure()
        
        # Ordenar aplicaciones por nombre
        if 'apps' in project_structure:
            project_structure['apps'] = dict(sorted(
                project_structure['apps'].items(),
                key=lambda x: x[1].get('name', x[0]).lower()
            ))
        
        # Generar documentación si se solicita
        if request.GET.get('generate_docs') == 'true':
            docs_file = analyzer.generate_project_documentation()
            if docs_file and os.path.exists(docs_file):
                messages.success(request, "Documentación generada correctamente.")
        
        # Obtener la ruta relativa para la plantilla
        diagram_url = os.path.join(settings.MEDIA_URL, 'uml_diagrams', filename)
        
        # Obtener aplicaciones instaladas para la navegación
        installed_apps = [
            app_config for app_config in apps.get_app_configs() 
            if not app_config.name.startswith(('django.', 'rest_framework', 'debug_toolbar'))
        ]
        
        # Configurar el contexto
        context = {
            'title': 'Diagrama del Proyecto',
            'is_project_diagram': True,
            'diagram_url': diagram_url,
            'last_modified': last_modified,
            'project_structure': project_structure,
            'site_title': 'Visualizador UML',
            'site_header': 'Diagrama del Proyecto',
            'docs_file': os.path.join(settings.MEDIA_ROOT, 'project_docs.md') 
                      if os.path.exists(os.path.join(settings.MEDIA_ROOT, 'project_docs.md')) else None,
            'installed_apps': installed_apps,
            'stats': project_structure.get('stats', {
                'total_apps': len(project_structure.get('apps', {})),
                'total_models': len(project_structure.get('models', [])),
                'total_views': len(project_structure.get('views', [])),
                'total_forms': len(project_structure.get('forms', [])),
                'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        }
        
        return render(request, 'uml_visualizer/diagram.html', context)
        
    except Exception as e:
        import traceback
        messages.error(request, f"Error al cargar el diagrama del proyecto: {str(e)}")
        return redirect('uml_visualizer:dashboard')

@user_passes_test(is_admin)
def download_docs(request):
    """
    Vista para descargar la documentación del proyecto en formato Markdown.
    """
    docs_file = os.path.join(settings.BASE_DIR, 'PROJECT_DOCS.md')
    
    # Si el archivo no existe, generarlo primero
    if not os.path.exists(docs_file):
        analyzer = ProjectAnalyzer()
        analyzer.generate_project_documentation(docs_file)
    
    if not os.path.exists(docs_file):
        raise Http404("No se pudo generar la documentación")
    
    with open(docs_file, 'rb') as f:
        response = HttpResponse(f.read(), content_type='text/markdown')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(docs_file)}"'
        return response
