"""
Vistas para el módulo de testing.
Proporciona las vistas necesarias para interactuar con las interfaces de testing.
"""
import importlib
from django.db.models import Avg
import inspect
import logging
import os
import pkgutil
from typing import Type, Dict, List, Any, Optional

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.module_loading import import_string
from django.conf import settings

from core_testing.models import TestRun, TestCase, TestCoverage
from core_testing.testing_interfaces.base import TestingInterface, TestingView
from core_testing.storage import TestResultStorage

logger = logging.getLogger(__name__)


class InterfaceTestingView(LoginRequiredMixin, View):
    """Vista para interactuar con una interfaz de testing específica."""
    template_name = 'core_testing/interface.html'
    interface_class = None  # Debe ser sobreescrito por las clases hijas
    
    def get(self, request: HttpRequest, interface_name: str) -> HttpResponse:
        """
        Muestra la interfaz de testing específica.
        
        Args:
            request: Objeto HttpRequest
            interface_name: Nombre de la interfaz de testing a cargar
            
        Returns:
            HttpResponse con la interfaz de testing renderizada
        """
        interface_class = self.get_interface_class()
        if not interface_class:
            return render(
                request, 
                'core_testing/interface.html', 
                {'error': f'Interfaz {interface_name} no encontrada'}, 
                status=404
            )
            
        interface = self.get_interface()
        tests = interface.get_available_tests()
        
        context = self.get_context_data()
        context.update({
            'interface_name': interface_name,
            'tests': tests,
            'interface': interface,
        })
        return render(request, self.template_name, context)
    
    def get_interface_class(self):
        """
        Obtiene la clase de la interfaz de testing.
        
        Returns:
            Clase de la interfaz de testing
            
        Raises:
            Http404: Si la interfaz no existe o no se puede cargar
        """
        if hasattr(self, 'interface_class') and self.interface_class is not None:
            return self.interface_class
            
        if not hasattr(self, 'kwargs') or 'interface_name' not in self.kwargs:
            raise Http404("No se especificó la interfaz de testing")
            
        interface_name = self.kwargs['interface_name']
        module_path = f'core_testing.testing_interfaces.{interface_name}'
        
        try:
            module = importlib.import_module(module_path)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if (issubclass(obj, TestingInterface) and 
                    obj != TestingInterface and 
                    obj.__module__ == module_path):
                    return obj
        except (ImportError, AttributeError) as e:
            logger.error(f"Error al cargar la interfaz {interface_name}: {e}")
            
        raise Http404(f"Interfaz de testing no encontrada: {interface_name}")
    
    def get_interface(self):
        """
        Obtiene una instancia de la interfaz de testing.
        
        Returns:
            Instancia de la interfaz de testing
            
        Raises:
            Http404: Si la interfaz no existe o no se puede cargar
        """
        interface_class = self.get_interface_class()
        return interface_class()
    
    def get_context_data(self, **kwargs):
        """
        Retorna el contexto para la plantilla.
        
        Returns:
            dict: Contexto para la plantilla
        """
        context = {}
        context.update(kwargs)
        return context


class TestRunDetailView(LoginRequiredMixin, View):
    """Vista para mostrar los detalles de una ejecución de pruebas."""
    template_name = 'core_testing/testrun_detail.html'
    
    def get(self, request: HttpRequest, run_id: int) -> HttpResponse:
        """Muestra los detalles de una ejecución de pruebas.
        
        Args:
            request: Objeto HttpRequest
            run_id: ID de la ejecución de pruebas
            
        Returns:
            HttpResponse con los detalles de la ejecución
        """
        test_run = get_object_or_404(TestRun, id=run_id)
        test_cases = test_run.testcase_set.all()
        coverage = TestCoverage.objects.filter(test_run=test_run).first()
        
        return render(request, self.template_name, {
            'test_run': test_run,
            'test_cases': test_cases,
            'coverage': coverage,
        })


def discover_testing_interfaces() -> Dict[str, Type[TestingInterface]]:
    """
    Descubre automáticamente todas las interfaces de testing disponibles.
    
    Returns:
        Dict[str, Type[TestingInterface]]: Diccionario con las interfaces encontradas
    """
    interfaces = {}
    logger = logging.getLogger(__name__)
    logger.info("=" * 80)
    logger.info("INICIANDO BÚSQUEDA DE INTERFACES DE TESTING")
    logger.info("=" * 80)
    
    try:
        # Obtener la ruta del directorio de interfaces
        import os
        from django.conf import settings
        
        # Ruta al directorio de interfaces
        interfaces_dir = os.path.join(settings.BASE_DIR, 'core_testing', 'testing_interfaces')
        logger.info(f"Buscando interfaces en: {interfaces_dir}")
        
        # Verificar si el directorio existe
        if not os.path.exists(interfaces_dir):
            logger.error(f"ERROR: El directorio de interfaces no existe: {interfaces_dir}")
            return {}
        
        # Verificar permisos del directorio
        logger.info(f"Permisos del directorio: {oct(os.stat(interfaces_dir).st_mode)[-3:]}")
        logger.info(f"Contenido del directorio: {os.listdir(interfaces_dir)}")
            
        # Listar archivos en el directorio
        for filename in os.listdir(interfaces_dir):
            logger.info(f"Procesando archivo: {filename}")
            
            # Ignorar archivos que no son módulos de Python
            if not filename.endswith('.py'):
                logger.info(f"  - Ignorando (no es .py): {filename}")
                continue
                
            if filename in ['__init__.py', 'base.py', '__pycache__']:
                logger.info(f"  - Ignorando (archivo especial): {filename}")
                continue
                
            # Obtener el nombre del módulo sin la extensión
            module_name = filename[:-3]
            full_module_name = f'core_testing.testing_interfaces.{module_name}'
            
            logger.info(f"  - Intentando cargar módulo: {full_module_name}")
            
            try:
                # Importar el módulo dinámicamente
                module = importlib.import_module(full_module_name)
                logger.info(f"  - Módulo importado correctamente: {module.__name__}")
                
                # Buscar clases que hereden de TestingInterface
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    logger.info(f"  - Examinando clase: {name} (módulo: {getattr(obj, '__module__', 'desconocido')})")
                    
                    # Verificar si es una clase de interfaz de prueba válida
                    try:
                        is_testing_interface = (
                            inspect.isclass(obj) and 
                            issubclass(obj, TestingInterface) and 
                            obj != TestingInterface and
                            obj.__module__ == module.__name__
                        )
                        
                        if is_testing_interface:
                            logger.info(f"  - CLASE VÁLIDA ENCONTRADA: {name} en {module_name}")
                            logger.info(f"     - Módulo: {obj.__module__}")
                            logger.info(f"     - Base classes: {[b.__name__ for b in obj.__bases__]}")
                            logger.info(f"     - Atributos: {dir(obj)}")
                            
                            # Usar el nombre de la interfaz o el nombre de la clase como clave
                            interface_name = getattr(obj, 'name', name)
                            logger.info(f"  - Registrando interfaz: {interface_name} (clase: {obj.__name__})")
                            
                            # Asegurarse de que el nombre sea único
                            if interface_name in interfaces:
                                logger.warning(f"  - ATENCIÓN: Nombre de interfaz duplicado: {interface_name}")
                                interface_name = f"{interface_name}_{module_name}"
                                
                            interfaces[interface_name] = obj
                            logger.info(f"  - Interfaz registrada: {interface_name}")
                        else:
                            logger.info(f"  - Clase ignorada (no es una interfaz de testing válida): {name}")
                            
                    except Exception as e:
                        logger.error(f"  - ERROR al procesar la clase {name}: {str(e)}", exc_info=True)
                        
            except ImportError as e:
                logger.error(f"  - ERROR al importar el módulo {full_module_name}: {str(e)}", exc_info=True)
            except Exception as e:
                logger.error(f"  - ERROR inesperado al procesar {full_module_name}: {str(e)}", exc_info=True)
        
        logger.info("=" * 80)
        logger.info(f"BÚSQUEDA COMPLETADA. Interfaces encontradas: {list(interfaces.keys())}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"ERROR CRÍTICO en discover_testing_interfaces: {str(e)}", exc_info=True)
        logger.error("=" * 80)
    
    return interfaces


class TestingDashboardView(LoginRequiredMixin, View):
    """Vista principal del dashboard de testing."""
    template_name = 'core_testing/dashboard.html'
    
    def get(self, request, *args, **kwargs):
        """Maneja las solicitudes GET para el dashboard de testing."""
        context = self.get_context_data()
        return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        """Obtiene el contexto para la plantilla del dashboard."""
        context = {}
        
        # Obtener las interfaces de testing disponibles
        interfaces = discover_testing_interfaces()
        
        # Agregar el nombre del módulo a cada interfaz
        for name, interface in interfaces.items():
            # Usar el nombre del módulo de la clase si está disponible, de lo contrario usar el nombre de la clase en minúsculas
            if hasattr(interface, '__module__'):
                module_name = interface.__module__.split('.')[-1]
            else:
                module_name = interface.__name__.lower()
            
            # Agregar el nombre del módulo como un atributo a la clase
            interface.module_name = module_name
        
        try:
            # Obtener las últimas ejecuciones de pruebas desde archivos
            recent_runs = TestResultStorage.list_test_runs(limit=10)
            
            # Asegurarse de que cada run tenga los campos necesarios
            for run in recent_runs:
                # Si el run tiene un campo 'results', usamos esos datos
                if 'results' in run and isinstance(run['results'], dict):
                    run.update({
                        'tests_passed': run['results'].get('passed', 0),
                        'tests_failed': run['results'].get('failed', 0),
                        'tests_error': run['results'].get('error', 0),
                        'tests_skipped': run['results'].get('skipped', 0),
                    })
                # Si no, intentamos obtener los valores directamente
                else:
                    run.update({
                        'tests_passed': run.get('passed', run.get('tests_passed', 0)),
                        'tests_failed': run.get('failed', run.get('tests_failed', 0)),
                        'tests_error': run.get('error', run.get('tests_error', 0)),
                        'tests_skipped': run.get('skipped', run.get('tests_skipped', 0)),
                    })
                
                # Asegurar que los valores sean enteros
                run['tests_passed'] = int(run['tests_passed'])
                run['tests_failed'] = int(run['tests_failed'])
                run['tests_error'] = int(run['tests_error'])
                run['tests_skipped'] = int(run['tests_skipped'])
            
            # Obtener estadísticas desde archivos
            stats = TestResultStorage.get_test_stats()
            
            # Calcular total de pruebas para porcentajes
            total_tests = max(1, sum([
                stats.get('total_passed', 0),
                stats.get('total_failed', 0),
                stats.get('total_errors', 0),
                stats.get('total_skipped', 0)
            ]))
            
            # Calcular porcentajes
            context.update({
                'interfaces': interfaces,
                'recent_runs': recent_runs,
                'total_runs': stats.get('total_runs', 0),
                'total_passed': stats.get('total_passed', 0),
                'total_failed': stats.get('total_failed', 0),
                'total_errors': stats.get('total_errors', 0),
                'total_skipped': stats.get('total_skipped', 0),
                'passed_percent': int((stats.get('total_passed', 0) / total_tests) * 100) if total_tests > 0 else 0,
                'failed_percent': int((stats.get('total_failed', 0) / total_tests) * 100) if total_tests > 0 else 0,
                'error_percent': int((stats.get('total_errors', 0) / total_tests) * 100) if total_tests > 0 else 0,
                'skipped_percent': int((stats.get('total_skipped', 0) / total_tests) * 100) if total_tests > 0 else 0,
            })
            
            # Agregar logs para depuración
            print(f"Interfaces encontradas: {len(interfaces)}")
            print(f"Ejecuciones recientes: {len(recent_runs)}")
            if recent_runs:
                print(f"Ejemplo de datos de ejecución: {recent_runs[0]}")
            print(f"Total de pruebas pasadas: {context['total_passed']}")
            print(f"Total de pruebas fallidas: {context['total_failed']}")
            print(f"Total de errores: {context['total_errors']}")
            
        except Exception as e:
            logger.error(f"Error al cargar datos de pruebas: {str(e)}", exc_info=True)
            # Si hay un error, mostrar datos vacíos
            context.update({
                'interfaces': interfaces,
                'recent_runs': [],
                'total_runs': 0,
                'total_passed': 0,
                'total_failed': 0,
                'total_errors': 0,
                'total_skipped': 0,
                'error_message': f"Error al cargar los datos: {str(e)}"
            })
        
        return context


class InterfaceTestingView(TestingView):
    """
    Vista para interactuar con una interfaz de testing específica.
    Esta vista se encarga de cargar dinámicamente la interfaz solicitada.
    
    Nota: Ya incluye LoginRequiredMixin a través de TestingView.
    """
    template_name = 'core_testing/interface.html'
    
    def get_interface_class(self) -> Type[TestingInterface]:
        """
        Obtiene la clase de la interfaz de testing solicitada.
        
        Returns:
            Type[TestingInterface]: Clase de la interfaz de testing
            
        Raises:
            Http404: Si la interfaz no se encuentra
        """
        # Si la clase ya está definida como atributo, usarla
        if hasattr(self, 'interface_class') and self.interface_class is not None:
            return self.interface_class
            
        # Si no, intentar cargarla dinámicamente
        interface_name = self.kwargs.get('interface_name')
        if not interface_name:
            raise Http404("No se especificó una interfaz de testing")
            
        interfaces = discover_testing_interfaces()
        
        # Buscar la interfaz por nombre de módulo
        for name, interface in interfaces.items():
            if hasattr(interface, 'module_name') and interface.module_name == interface_name:
                return interface
        
        # Si no se encuentra por module_name, intentar por el nombre de la clase
        for name, interface in interfaces.items():
            if name.lower() == interface_name.lower():
                return interface
        
        raise Http404(f"Interfaz de testing no encontrada: {interface_name}")
    
    def get_context_data(self, **kwargs):
        """Agrega información adicional al contexto."""
        context = super().get_context_data(**kwargs)
        context['interface_name'] = self.kwargs.get('interface_name')
        return context


def get_test_form(request: HttpRequest, interface_name: str) -> JsonResponse:
    """
    Vista que devuelve el formulario HTML para un test específico.
    
    Args:
        request: Objeto HttpRequest
        interface_name: Nombre de la interfaz de testing
        
    Returns:
        JsonResponse con el formulario HTML o un mensaje de error
    """
    interfaces = discover_testing_interfaces()
    
    if interface_name not in interfaces:
        return JsonResponse(
            {'error': f'Interfaz de testing no encontrada: {interface_name}'}, 
            status=404
        )
    
    test_id = request.GET.get('test_id')
    if not test_id:
        return JsonResponse(
            {'error': 'Se requiere el parámetro test_id'}, 
            status=400
        )
    
    interface = interfaces[interface_name]()
    form_html = interface.get_test_form(test_id, request)
    
    return JsonResponse({'form': form_html})


def run_test_api(request: HttpRequest, interface_name: str) -> JsonResponse:
    """
    API para ejecutar un test y devolver los resultados en formato JSON.
    
    Args:
        request: Objeto HttpRequest
        interface_name: Nombre de la interfaz de testing
        
    Returns:
        JsonResponse con los resultados del test
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'Se requiere autenticación'}, 
            status=403
        )
    
    interfaces = discover_testing_interfaces()
    
    if interface_name not in interfaces:
        return JsonResponse(
            {'error': f'Interfaz de testing no encontrada: {interface_name}'}, 
            status=404
        )
    
    test_id = request.POST.get('test_id')
    if not test_id:
        return JsonResponse(
            {'error': 'Se requiere el parámetro test_id'}, 
            status=400
        )
    
    # Crear un nuevo registro de ejecución
    test_run = TestRun.objects.create(
        name=f"{interface_name} - {test_id}",
        started_by=request.user,
        status='running'
    )
    
    try:
        interface = interfaces[interface_name]()
        
        # Ejecutar el test con los parámetros del formulario
        result = interface.run_test(test_id, request=request)
        
        # Actualizar el estado de la ejecución
        test_run.status = 'completed' if result.get('success') else 'failed'
        test_run.save()
        
        # Registrar el caso de prueba
        test_case = TestCase.objects.create(
            test_run=test_run,
            name=result.get('test_name', test_id),
            description=result.get('message', ''),
            status='passed' if result.get('success') else 'failed',
            execution_time=result.get('duration', 0),
            metadata={
                'test_id': test_id,
                'interface': interface_name,
                'result': result
            }
        )
        
        # Si hay datos de cobertura, guardarlos
        if 'coverage' in result:
            TestCoverage.objects.create(
                test_run=test_run,
                percent_covered=result['coverage'].get('percent_covered', 0),
                total_statements=result['coverage'].get('total_statements', 0),
                missing_statements=result['coverage'].get('missing_statements', 0),
                excluded_statements=result['coverage'].get('excluded_statements', 0),
                coverage_data=result['coverage'].get('coverage_data', {})
            )
        
        return JsonResponse(result)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        # Registrar el error
        test_run.status = 'error'
        test_run.save()
        
        TestCase.objects.create(
            test_run=test_run,
            name=f"{interface_name} - {test_id}",
            description=f"Error al ejecutar el test: {str(e)}",
            status='error',
            execution_time=0,
            metadata={
                'test_id': test_id,
                'interface': interface_name,
                'error': str(e),
                'traceback': error_trace
            }
        )
        
        return JsonResponse(
            {
                'success': False,
                'message': f'Error al ejecutar el test: {str(e)}',
                'traceback': error_trace if settings.DEBUG else None
            },
            status=500
        )


class TestRunDetailView(LoginRequiredMixin, View):
    """Vista para mostrar los detalles de una ejecución de tests."""
    template_name = 'core_testing/testrun_detail.html'
    
    def get(self, request: HttpRequest, run_id: int) -> HttpResponse:
        """
        Muestra los detalles de una ejecución de tests.
        
        Args:
            request: Objeto HttpRequest
            run_id: ID de la ejecución de tests a mostrar
            
        Returns:
            HttpResponse con los detalles de la ejecución
        """
        test_run = get_object_or_404(TestRun, id=run_id)
        test_cases = test_run.testcase_set.all()
        
        # Obtener cobertura si existe
        coverage = TestCoverage.objects.filter(test_run=test_run).first()
        
        context = {
            'test_run': test_run,
            'test_cases': test_cases,
            'coverage': coverage,
        }
        
        return render(request, self.template_name, context)


class TestCoverageReportView(LoginRequiredMixin, View):
    """Vista para mostrar informes de cobertura de pruebas."""
    template_name = 'core_testing/coverage_report.html'
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra un informe de cobertura de pruebas.
        """
        # Obtener las últimas ejecuciones con cobertura
        coverage_reports = TestCoverage.objects.select_related('test_run').order_by('-test_run__created_at')[:50]
        
        # Calcular estadísticas generales
        total_runs = TestCoverage.objects.count()
        avg_coverage = TestCoverage.objects.aggregate(avg=Avg('percent_covered'))['avg'] or 0
        
        context = {
            'coverage_reports': coverage_reports,
            'total_runs': total_runs,
            'avg_coverage': round(avg_coverage, 2),
        }
        
        return render(request, self.template_name, context)


# Importar las vistas de las interfaces de testing específicas
# Esto permite que se registren automáticamente
import core_testing.testing_interfaces  # noqa
