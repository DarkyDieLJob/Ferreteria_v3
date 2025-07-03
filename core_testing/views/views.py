"""
Vistas para el módulo de testing.
Proporciona las vistas necesarias para interactuar con las interfaces de testing.
"""
import importlib
import inspect
import pkgutil
from typing import Type, Dict, List, Any, Optional

from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils.module_loading import import_string
from django.conf import settings

from core_testing.models import TestRun, TestCase, TestCoverage
from core_testing.testing_interfaces.base import TestingInterface, TestingView


class InterfaceTestingView(LoginRequiredMixin, View):
    """Vista para interactuar con una interfaz de testing específica."""
    template_name = 'core_testing/interface.html'
    
    def get(self, request: HttpRequest, interface_name: str) -> HttpResponse:
        """
        Muestra la interfaz de testing específica.
        
        Args:
            request: Objeto HttpRequest
            interface_name: Nombre de la interfaz de testing a cargar
            
        Returns:
            HttpResponse con la interfaz de testing renderizada
        """
        interface_class = self._get_interface_class(interface_name)
        if not interface_class:
            return render(
                request, 
                'core_testing/interface.html', 
                {'error': f'Interfaz {interface_name} no encontrada'}, 
                status=404
            )
            
        interface = interface_class()
        tests = interface.get_available_tests()
        
        context = {
            'interface_name': interface_name,
            'tests': tests,
            'interface': interface,
        }
        return render(request, self.template_name, context)
    
    def _get_interface_class(
        self, 
        interface_name: str
    ) -> Optional[Type[TestingInterface]]:
        """
        Obtiene la clase de la interfaz de testing por su nombre.
        
        Args:
            interface_name: Nombre de la interfaz a cargar
            
        Returns:
            Clase de la interfaz de testing o None si no se encuentra
        """
        try:
            module = importlib.import_module(
                f'core_testing.testing_interfaces.{interface_name}'
            )
            for name, obj in inspect.getmembers(module, inspect.isclass):
                is_interface = (
                    issubclass(obj, TestingInterface) and 
                    obj != TestingInterface and 
                    obj.__module__ == f'core_testing.testing_interfaces.{interface_name}'
                )
                if is_interface:
                    return obj
        except (ImportError, AttributeError) as e:
            print(f"Error loading interface {interface_name}: {e}")
            return None
        return None


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
    
    try:
        # Obtener todos los módulos en el directorio testing_interfaces
        package = importlib.import_module('core_testing.testing_interfaces')
        
        # Manejar el caso en que estemos en un entorno de prueba con mocks
        if hasattr(package, '__path__'):
            package_path = package.__path__
        else:
            # En caso de que no haya __path__ (como en un mock), usar una ruta por defecto
            import os
            package_path = [os.path.join(os.path.dirname(__file__), 'testing_interfaces')]
        
        # Iterar sobre todos los módulos en el paquete
        for finder, module_name, _ in pkgutil.iter_modules(package_path):
            # No cargar el módulo base
            if module_name == 'base' or module_name == '__pycache__':
                continue
                
            try:
                # Importar el módulo
                full_module_name = f'core_testing.testing_interfaces.{module_name}'
                module = importlib.import_module(full_module_name)
                
                # Buscar clases que hereden de TestingInterface
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Verificar si es una clase de interfaz de prueba válida
                    if (
                        issubclass(obj, TestingInterface) and 
                        obj != TestingInterface
                    ):
                        # Verificar si el módulo coincide o si estamos en un entorno de prueba
                        if (
                            hasattr(obj, '__module__') and 
                            (obj.__module__ == module.__name__ or 'unittest.mock' in str(type(obj)))
                        ):
                            # Usar el nombre del módulo como clave, a menos que la clase tenga un nombre específico
                            interface_name = getattr(obj, 'interface_name', module_name)
                            interfaces[interface_name] = obj
                            
            except (ImportError, AttributeError) as e:
                # Log the error
                logger = logging.getLogger(__name__)
                logger.error("Error al cargar el módulo %s: %s", module_name, e, exc_info=True)
                
    except ImportError as e:
        # Log the error if we can't import the package at all
        logger = logging.getLogger(__name__)
        logger.error("Error al importar el paquete core_testing.testing_interfaces: %s", e, exc_info=True)
    
    return interfaces


class TestingDashboardView(LoginRequiredMixin, View):
    """Vista principal del dashboard de testing."""
    template_name = 'core_testing/dashboard.html'
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Muestra el dashboard con todas las interfaces de testing disponibles.
        """
        interfaces = discover_testing_interfaces()
        
        # Obtener estadísticas de ejecución
        test_runs = TestRun.objects.order_by('-started_at')[:10]
        
        # Preparar el contexto con las interfaces y estadísticas
        context = {
            'interfaces': [
                {
                    'name': interface_class.name,
                    'description': getattr(interface_class, 'description', ''),
                    'version': getattr(interface_class, 'version', '1.0.0'),
                    'module': module_name,
                }
                for module_name, interface_class in interfaces.items()
            ],
            'recent_runs': test_runs,
            'total_runs': TestRun.objects.count(),
            'total_passed': TestCase.objects.filter(status='passed').count(),
            'total_failed': TestCase.objects.filter(status='failed').count(),
            'total_errors': TestCase.objects.filter(status='error').count(),
        }
        
        return render(request, self.template_name, context)


class InterfaceTestingView(TestingView):
    """
    Vista para interactuar con una interfaz de testing específica.
    Esta vista se encarga de cargar dinámicamente la interfaz solicitada.
    """
    template_name = 'core_testing/interface.html'
    
    def get_interface_class(self) -> Type[TestingInterface]:
        """
        Obtiene la clase de la interfaz de testing solicitada.
        
        Returns:
            Type[TestingInterface]: Clase de la interfaz de testing
        """
        interface_name = self.kwargs.get('interface_name')
        interfaces = discover_testing_interfaces()
        
        if interface_name not in interfaces:
            raise Http404(f"Interfaz de testing no encontrada: {interface_name}")
            
        return interfaces[interface_name]
    
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
        coverage_reports = TestCoverage.objects.select_related('test_run').order_by('-test_run__started_at')[:50]
        
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
