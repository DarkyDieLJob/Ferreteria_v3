import os
import ast
import inspect
import datetime
from pathlib import Path
from django.apps import apps
from django.conf import settings
from django.views.generic import View
from django.forms import Form, ModelForm

class ProjectAnalyzer:
    """
    Analiza la estructura del proyecto Django y extrae información sobre
    modelos, vistas, formularios y otras clases importantes.
    """
    
    def __init__(self, project_root=None):
        self.project_root = Path(project_root or settings.BASE_DIR).resolve()
        self.exclude_dirs = {
            '__pycache__', 'migrations', 'templates', 
            'static', 'venv', '.git', 'media', 'env',
            'node_modules', '.github', '.idea', '.vscode'
        }
        self.exclude_files = {'__init__.py', 'apps.py', 'admin.py', 'tests.py'}
        self.site_packages_dirs = [
            Path(p).resolve() for p in __import__('sys').path 
            if 'site-packages' in p and Path(p).is_dir()
        ]
        
    def get_project_structure(self):
        """
        Obtiene la estructura completa del proyecto con información detallada de cada aplicación.
        
        Returns:
            dict: Estructura del proyecto con información de aplicaciones, modelos, vistas y formularios
        """
        structure = {
            'apps': {},
            'views': [],
            'forms': [],
            'models': [],
            'utils': [],
            'other_classes': [],
            'stats': {
                'total_apps': 0,
                'total_models': 0,
                'total_views': 0,
                'total_forms': 0,
                'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        
        # Obtener todas las aplicaciones instaladas
        all_apps = []
        for app_config in apps.get_app_configs():
            # Saltar aplicaciones del sistema y de terceros
            if any(app_config.name.startswith(pkg) for pkg in 
                  ['django.', 'rest_framework', 'debug_toolbar', 'allauth', 'crispy_forms', 'bootstrap']):
                continue
                
            try:
                app_path = Path(app_config.path)
                
                # Saltar si la aplicación no está en el directorio del proyecto
                if not self._is_in_project_dir(app_path):
                    continue
                    
                all_apps.append(app_config)
            except Exception as e:
                continue
                
        # Actualizar estadísticas
        structure['stats']['total_apps'] = len(all_apps)
        
        # Procesar cada aplicación
        for app_config in all_apps:
            try:
                app_path = Path(app_config.path)
                app_label = app_config.label
                app_name = app_config.verbose_name or app_config.label.title()
                
                # Inicializar estructura de la aplicación
                structure['apps'][app_label] = {
                    'name': app_name,
                    'path': str(app_path),
                    'models': [],
                    'views': [],
                    'forms': [],
                    'templates': [],
                    'urls': [],
                    'admin': None,
                    'apps': None
                }
                    
                app_name = app_config.verbose_name or app_config.label
                
                # Obtener información de modelos
                try:
                    models_info = self._get_models_info(app_config)
                    structure['apps'][app_label]['models'] = models_info
                    structure['models'].extend(models_info)
                    structure['stats']['total_models'] += len(models_info)
                    
                    # Obtener información de vistas
                    views_info = self._get_views_info(app_path)
                    structure['apps'][app_label]['views'] = views_info
                    structure['views'].extend(views_info)
                    structure['stats']['total_views'] += len(views_info)
                    
                    # Obtener información de formularios
                    forms_info = self._get_forms_info(app_path)
                    structure['apps'][app_label]['forms'] = forms_info
                    structure['forms'].extend(forms_info)
                    structure['stats']['total_forms'] += len(forms_info)
                    
                    # Buscar archivos de URLs
                    urls_file = app_path / 'urls.py'
                    if urls_file.exists():
                        urls_info = self._get_urls_info(app_path)
                        structure['apps'][app_label]['urls'] = urls_info
                        
                    # Buscar archivo admin.py
                    admin_file = app_path / 'admin.py'
                    if admin_file.exists():
                        admin_info = self._get_admin_info(app_path)
                        structure['apps'][app_label]['admin'] = admin_info
                        
                    # Buscar archivo apps.py
                    apps_file = app_path / 'apps.py'
                    if apps_file.exists():
                        structure['apps'][app_label]['apps'] = str(apps_file.relative_to(self.project_root))
                        
                except Exception as e:  # noqa: BLE001
                    structure['apps'][app_label].update({
                        'error': str(e),
                        'models': [],
                        'views': [],
                        'forms': []
                    })
                    
            except Exception as e:  # noqa: BLE001
                # Skip this app if there's an error getting its path
                continue
            
            # Only add models if the app was successfully added to structure['apps']
            if app_config.label in structure['apps']:
                structure['models'].extend(structure['apps'][app_config.label]['models'])
            
        return structure
    
    def _get_models_info(self, app_config):
        """Obtiene información sobre los modelos de una aplicación."""
        models = []
        try:
            app_models = app_config.get_models()
        except Exception as e:  # noqa: BLE001
            print(f"Error obteniendo modelos para {app_config.label}: {str(e)}")
            return models
            
        for model in app_models:
            try:
                # Obtener el módulo del modelo
                model_module = getattr(model, '__module__', '')
                
                # Saltar modelos de paquetes externos
                if not model_module or any(ext in model_module for ext in ['django.', 'allauth.']):
                    continue
                
                # Obtener metadatos del modelo
                model_name = getattr(model, '__name__', 'Unknown')
                model_meta = getattr(model, '_meta', None)
                
                # Obtener verbose_name con valor por defecto
                verbose_name = getattr(model_meta, 'verbose_name', model_name)
                if isinstance(verbose_name, str) and verbose_name.islower():
                    verbose_name = verbose_name.capitalize()
                    
                # Obtener verbose_name_plural con valor por defecto
                verbose_name_plural = getattr(model_meta, 'verbose_name_plural', f"{model_name}s")
                if isinstance(verbose_name_plural, str) and verbose_name_plural.islower():
                    verbose_name_plural = verbose_name_plural.capitalize()
                
                # Construir información del modelo
                model_info = {
                    'name': model_name,
                    'module': model_module,
                    'verbose_name': verbose_name,
                    'verbose_name_plural': verbose_name_plural,
                    'app_label': getattr(model_meta, 'app_label', app_config.label),
                    'fields': [],
                    'methods': self._get_class_methods(model) if hasattr(model, '__dict__') else [],
                    'docstring': (inspect.getdoc(model) or "").strip()
                }
                
                # Safely get model fields
                try:
                    fields = model._meta.get_fields()
                except Exception as e:
                    fields = []
                
                for field in fields:
                    try:
                        if getattr(field, 'auto_created', False) and not getattr(field, 'concrete', False):
                            continue
                            
                        # Safely get field attributes with fallbacks
                        field_name = getattr(field, 'name', 'unknown')
                        field_type = getattr(field, 'get_internal_type', lambda: 'Unknown')()
                        
                        # Safely get related model information
                        related_model_str = None
                        try:
                            related_model = getattr(field, 'related_model', None)
                            if callable(related_model):
                                related_model = related_model()
                            if related_model is not None:
                                related_app = getattr(getattr(related_model, '_meta', None), 'app_label', 'unknown')
                                related_name = getattr(related_model, '__name__', 'Unknown')
                                related_model_str = f"{related_app}.{related_name}"
                        except Exception:
                            related_model_str = None
                        
                        # Build field info with safe attribute access
                        field_info = {
                            'name': field_name,
                            'type': field_type,
                            'related_model': related_model_str,
                            'many_to_many': getattr(field, 'many_to_many', False),
                            'null': getattr(field, 'null', False),
                            'blank': getattr(field, 'blank', False),
                            'help_text': str(getattr(field, 'help_text', ''))
                        }
                        model_info['fields'].append(field_info)
                        
                    except Exception as field_error:
                        # Skip this field if there's an error
                        continue
                
                models.append(model_info)
                
            except Exception as model_error:
                # Skip this model if there's an error
                continue
            
        return models
    
    def _is_in_project_dir(self, path):
        """Check if a path is within the project directory."""
        try:
            if path is None:
                return False
                
            path = Path(path).resolve()
            
            # Check if path is in site-packages
            try:
                if any(str(path).startswith(str(sp)) for sp in self.site_packages_dirs):
                    return False
            except (ValueError, RuntimeError):
                pass
                
            # Check if path is in project root using string comparison
            try:
                project_path = str(self.project_root)
                current_path = str(path)
                return current_path.startswith(project_path)
            except (ValueError, RuntimeError):
                return False
                
        except Exception:  # noqa: BLE001 - Broad exception is okay here
            return False

    def _get_views_info(self, app_path):
        """Obtiene información sobre las vistas de una aplicación."""
        if not self._is_in_project_dir(app_path):
            return []
            
        views = []
        
        # Buscar en el directorio de la aplicación
        for root, dirs, files in os.walk(app_path):
            # Saltar directorios excluidos
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if not file.endswith('.py') or file in self.exclude_files:
                    continue
                    
                file_path = Path(root) / file
                if not self._is_in_project_dir(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            tree = ast.parse(f.read(), str(file_path))
                        except SyntaxError:
                            continue
                            
                    for node in ast.walk(tree):
                        if not isinstance(node, ast.ClassDef):
                            continue
                            
                        # Verificar si es una vista
                        is_view = False
                        base_classes = []
                        
                        # Obtener las clases base
                        for base in node.bases:
                            if hasattr(base, 'id'):
                                base_classes.append(base.id)
                            elif hasattr(base, 'attr'):
                                base_classes.append(base.attr)
                        
                        # Verificar si hereda de View o tiene decoradores de vista
                        view_bases = {'View', 'TemplateView', 'ListView', 'DetailView', 
                                    'CreateView', 'UpdateView', 'DeleteView', 'FormView', 
                                    'RedirectView', 'APIView', 'GenericAPIView'}
                        
                        if any(base in view_bases for base in base_classes):
                            is_view = True
                        else:
                            # Verificar decoradores en métodos
                            for item in node.body:
                                if (isinstance(item, ast.FunctionDef) and 
                                    any(isinstance(decorator, ast.Name) and 
                                        decorator.id in ['login_required', 'permission_required', 
                                                       'staff_member_required', 'method_decorator']
                                        for decorator in getattr(item, 'decorator_list', []))):
                                    is_view = True
                                    break
                        
                        if is_view:
                            # Obtener docstring
                            docstring = ast.get_docstring(node) or ""
                            
                            # Obtener métodos
                            methods = []
                            for item in node.body:
                                if isinstance(item, ast.FunctionDef):
                                    method_doc = ast.get_docstring(item) or ""
                                    decorators = []
                                    for d in getattr(item, 'decorator_list', []):
                                        if hasattr(d, 'id'):
                                            decorators.append(d.id)
                                        elif hasattr(d, 'func') and hasattr(d.func, 'id'):
                                            decorators.append(d.func.id)
                                    
                                    methods.append({
                                        'name': item.name,
                                        'docstring': method_doc,
                                        'decorators': decorators
                                    })
                            
                            views.append({
                                'name': node.name,
                                'docstring': docstring,
                                'methods': methods,
                                'base_classes': base_classes,
                                'file': str(file_path.relative_to(self.project_root)),
                                'module': file_path.stem
                            })
                            
                except Exception as e:
                    # Si hay un error al procesar el archivo, continuar con el siguiente
                    continue
        
        return views
    
    def _get_forms_info(self, app_path):
        """Obtiene información sobre los formularios de una aplicación."""
        if not self._is_in_project_dir(app_path):
            return []
            
        forms = []
        
        # Buscar en el directorio de la aplicación
        for root, dirs, files in os.walk(app_path):
            # Saltar directorios excluidos
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if not file.endswith('.py') or file in self.exclude_files:
                    continue
                    
                file_path = Path(root) / file
                if not self._is_in_project_dir(file_path):
                    continue
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        try:
                            tree = ast.parse(f.read(), str(file_path))
                        except SyntaxError:
                            continue
                            
                    for node in ast.walk(tree):
                        if not isinstance(node, ast.ClassDef):
                            continue
                            
                        # Verificar si es un formulario
                        is_form = False
                        base_classes = []
                        
                        # Obtener las clases base
                        for base in node.bases:
                            if hasattr(base, 'id'):
                                base_classes.append(base.id)
                            elif hasattr(base, 'attr'):
                                base_classes.append(base.attr)
                            elif hasattr(base, 'value') and hasattr(base.value, 'id'):
                                # Para casos como forms.Form
                                base_classes.append(f"{base.value.id}.{base.attr}")
                        
                        # Verificar si hereda de Form o ModelForm
                        form_bases = {'Form', 'ModelForm', 'forms.Form', 'forms.ModelForm',
                                    'BaseForm', 'forms.BaseForm', 'forms.BaseModelForm'}
                        
                        if any(base in form_bases or 
                              any(fb in str(base) for fb in form_bases) 
                              for base in base_classes):
                            is_form = True
                            
                        if is_form:
                            # Obtener docstring
                            docstring = ast.get_docstring(node) or ""
                            
                            # Obtener campos
                            fields = []
                            for item in node.body:
                                if isinstance(item, ast.Assign) and len(item.targets) == 1:
                                    field_name = getattr(item.targets[0], 'id', None)
                                    if field_name and not field_name.startswith('_'):
                                        field_type = ""
                                        
                                        # Obtener el tipo de campo
                                        if isinstance(item.value, ast.Call):
                                            if hasattr(item.value.func, 'id'):
                                                field_type = item.value.func.id
                                            elif hasattr(item.value.func, 'attr'):
                                                field_type = item.value.func.attr
                                            elif hasattr(item.value.func, 'value') and hasattr(item.value.func, 'attr'):
                                                field_type = f"{item.value.func.value.id}.{item.value.func.attr}"
                                        elif hasattr(item.value, 'id'):
                                            field_type = item.value.id
                                            
                                        # Obtener argumentos del campo
                                        field_args = {}
                                        if hasattr(item.value, 'keywords'):
                                            for kw in item.value.keywords:
                                                if hasattr(kw, 'value') and hasattr(kw, 'arg'):
                                                    if isinstance(kw.value, ast.Str):
                                                        field_args[kw.arg] = f"'{kw.value.s}'"
                                                    elif hasattr(kw.value, 'id'):
                                                        field_args[kw.arg] = kw.value.id
                                                    elif hasattr(kw.value, 'n'):
                                                        field_args[kw.arg] = str(kw.value.n)
                                                    elif hasattr(kw.value, 'value'):
                                                        field_args[kw.arg] = str(kw.value.value)
                                        
                                        fields.append({
                                            'name': field_name,
                                            'type': field_type,
                                            'args': field_args,
                                            'line': getattr(item, 'lineno', 0)
                                        })
                            
                            forms.append({
                                'name': node.name,
                                'docstring': docstring,
                                'fields': fields,
                                'base_classes': base_classes,
                                'file': str(file_path.relative_to(self.project_root)),
                                'module': file_path.stem
                            })
                            
                except Exception as e:
                    # Si hay un error al procesar el archivo, continuar con el siguiente
                    continue
        
        return forms
    
    def _get_admin_info(self, app_path):
        """Obtiene información sobre la configuración de admin de una aplicación."""
        if not self._is_in_project_dir(app_path):
            return []
            
        admin_file = app_path / 'admin.py'
        if not admin_file.exists() or not self._is_in_project_dir(admin_file):
            return []
            
        return self._get_classes_from_file(admin_file, parent_class='ModelAdmin')
    
    def _get_urls_info(self, app_path):
        """Obtiene información sobre las URLs de una aplicación."""
        if not self._is_in_project_dir(app_path):
            return []
            
        urls_file = app_path / 'urls.py'
        if not urls_file.exists() or not self._is_in_project_dir(urls_file):
            return []
            
        return self._get_url_patterns_from_file(urls_file)
    
    def _get_classes_from_file(self, file_path, parent_class=None):
        """Extrae información de las clases de un archivo Python."""
        classes = []
        if not self._is_in_project_dir(file_path):
            return classes
            
        try:
            # Check if file exists and is readable
            file_path = Path(file_path)
            if not file_path.exists() or not file_path.is_file():
                return classes
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError, OSError):
                return classes
                
            try:
                tree = ast.parse(content, str(file_path))
            except (SyntaxError, TypeError, ValueError):
                return classes
                
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                    
                # Get class name safely
                class_name = getattr(node, 'name', 'UnknownClass')
                
                # Check for parent class if specified
                if parent_class:
                    has_parent = False
                    try:
                        has_parent = any(
                            hasattr(base, 'id') and base.id == parent_class 
                            for base in getattr(node, 'bases', [])
                        )
                    except (AttributeError, TypeError):
                        pass
                        
                    if not has_parent:
                        continue
                
                # Get class docstring
                docstring = ""
                try:
                    docstring = ast.get_docstring(node) or ""
                    if not isinstance(docstring, str):
                        docstring = str(docstring)
                except Exception:  # noqa: BLE001 - Broad exception is okay here as we're just trying to get a docstring
                    pass
                
                # Get class methods
                methods = []
                try:
                    methods = self._get_class_methods(node)
                except Exception:  # noqa: BLE001 - Broad exception is okay here as we're just trying to get methods
                    pass
                
                class_info = {
                    'name': class_name,
                    'docstring': docstring,
                    'methods': methods
                }
                classes.append(class_info)
                    
        except Exception as e:
            # Catch any other exceptions to prevent the entire process from failing
            pass
            
        return classes
    
    def _get_methods_from_ast(self, class_node):
        """Extrae información de los métodos de una clase desde el AST."""
        methods = []
        if not hasattr(class_node, 'body') or not isinstance(class_node.body, list):
            return methods
            
        for node in class_node.body:
            if not isinstance(node, ast.FunctionDef):
                continue
                
            # Get method name safely
            method_name = getattr(node, 'name', 'unknown_method')
            
            # Get method arguments
            args = []
            try:
                args = [
                    arg.arg for arg in getattr(getattr(node, 'args', None), 'args', []) 
                    if hasattr(arg, 'arg')
                ]
            except (AttributeError, TypeError):
                pass
            
            # Get method docstring
            docstring = ""
            try:
                docstring = ast.get_docstring(node) or ""
                if not isinstance(docstring, str):
                    docstring = str(docstring)
            except Exception:  # noqa: BLE001 - Broad exception is okay here as we're just trying to get a docstring
                pass
            
            method_info = {
                'name': method_name,
                'args': args,
                'docstring': docstring
            }
            
            methods.append(method_info)
            
        return methods

    def generate_project_documentation(self, output_file=None):
        """
        Genera documentación detallada del proyecto.
        
        Args:
            output_file: Ruta del archivo de salida. Si es None, se usa PROJECT_DOCS.md
        """
        structure = self.get_project_structure()
        
        if not output_file:
            output_file = os.path.join(settings.BASE_DIR, 'PROJECT_DOCS.md')
        
        # Obtener el nombre del proyecto de settings o usar uno por defecto
        project_name = getattr(settings, 'PROJECT_NAME', 'Mi Proyecto Django')
        
        # Generar contenido Markdown
        content = [
            f"# Documentación del Proyecto: {project_name}\n",
            f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        ]
        
        # Resumen de la aplicación
        content.append("## Resumen\n")
        content.append(f"- **Aplicaciones:** {len(structure['apps'])}")
        content.append(f"- **Modelos:** {sum(len(app['models']) for app in structure['apps'].values())}")
        content.append(f"- **Vistas:** {sum(len(app['views']) for app in structure['apps'].values())}")
        content.append(f"- **Formularios:** {sum(len(app['forms']) for app in structure['apps'].values())}\n")
        
        # Por cada aplicación
        for app_label, app_info in structure['apps'].items():
            content.append(f"### {app_info['name']} (`{app_label}`)\n")
            
            # Modelos
            if app_info['models']:
                content.append("#### Modelos\n")
                for model in app_info['models']:
                    content.append(f"- **{model['name']}**")
                    if model['docstring']:
                        first_line = model['docstring'].split('\n')[0]
                        content.append(f"  > {first_line}")
                    
                    # Campos del modelo
                    if model['fields']:
                        content.append("  - **Campos:**")
                        for field in model['fields']:
                            field_desc = f"    - `{field['name']}` ({field['type']})"
                            if field['related_model']:
                                field_desc += f" → `{field['related_model'].__name__}`"
                            if field['help_text']:
                                field_desc += f" - {field['help_text']}"
                            content.append(field_desc)
                    content.append("")
            
            # Vistas
            if app_info['views']:
                content.append("#### Vistas\n")
                for view in app_info['views']:
                    content.append(f"- **{view['name']}**")
                    if view['docstring']:
                        first_line = view['docstring'].split('\n')[0]
                        content.append(f"  > {first_line}")
                    
                    # Métodos de la vista
                    if view['methods']:
                        content.append("  - **Métodos:**")
                        for method in view['methods']:
                            # Usar los argumentos disponibles para construir la firma
                            args_str = f"({', '.join(method['args'])})" if method.get('args') else "()"
                            content.append(f"    - `{method['name']}{args_str}`")
                            if method.get('docstring'):
                                first_line = method['docstring'].split('\n')[0]
                                content.append(f"      > {first_line}")
                    content.append("")
        
        # Escribir el archivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"Documentación generada en: {output_file}")
        return output_file
