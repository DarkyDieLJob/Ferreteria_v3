"""
Pruebas para las vistas del módulo core_testing.
"""
import os
import sys
import django
from typing import List, Dict, Any, Optional
from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import Http404, HttpResponse, JsonResponse, HttpRequest
from django.conf import settings
from django.utils import timezone
from unittest.mock import patch, MagicMock, ANY

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
django.setup()

# Importar las vistas desde el módulo correcto
from core_testing.views.views import (
    TestingDashboardView,
    InterfaceTestingView,
    TestRunDetailView,
    TestCoverageReportView,
    run_test_api,
    get_test_form
)

# Importar modelos
from core_testing.models import TestRun, TestCoverage
from core_testing.testing_interfaces.base import TestingInterface

# Obtener el modelo de usuario
User = get_user_model()

# Configuración para las pruebas
TEST_SETTINGS = {
    'DATABASES': {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    },
    'PASSWORD_HASHERS': [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ],
}

# Mock implementation of TestingInterface for testing
class MockTestingInterface(TestingInterface):
    """Mock implementation of TestingInterface for testing purposes."""
    
    name = "Mock Interface"
    description = "A mock testing interface for unit tests"
    version = "1.0.0"
    
    def get_available_tests(self) -> List[Dict[str, Any]]:
        """Return a list of available tests."""
        return [
            {
                'id': 'test1', 
                'name': 'Test 1', 
                'description': 'First test',
                'parameters': [
                    {'name': 'param1', 'type': 'text', 'required': True, 'label': 'Parameter 1'}
                ]
            },
            {
                'id': 'test2', 
                'name': 'Test 2', 
                'description': 'Second test',
                'parameters': [
                    {'name': 'param2', 'type': 'number', 'required': False, 'label': 'Parameter 2'}
                ]
            },
        ]
    
    def get_test_form(self, test_id: str, request: Optional[HttpRequest] = None) -> str:
        """Return HTML form for the specified test."""
        tests = self.get_available_tests()
        test = next((t for t in tests if t['id'] == test_id), None)
        
        if not test:
            return "<div class='error'>Test not found</div>"
            
        form_fields = ""
        for param in test.get('parameters', []):
            required = 'required' if param.get('required', False) else ''
            form_fields += f"""
            <div class='form-group'>
                <label for='{param['name']}'>{param.get('label', param['name'])}</label>
                <input type='{param['type']}' id='{param['name']}' name='{param['name']}' {required}>
            </div>
            """
            
        return f"""
        <form id='test-form' method='post'>
            {form_fields}
            <button type='submit' class='btn btn-primary'>Run Test</button>
        </form>
        """
    
    def run_test(self, test_id: str, **kwargs) -> Dict[str, Any]:
        """Execute the specified test with the given parameters."""
        tests = self.get_available_tests()
        test = next((t for t in tests if t['id'] == test_id), None)
        
        if not test:
            return {
                'success': False,
                'test_id': test_id,
                'message': f'Test {test_id} not found',
                'details': {}
            }
            
        # Simulate test execution
        return {
            'success': True,
            'test_id': test_id,
            'message': f'Test {test_id} executed successfully',
            'details': {
                'parameters': kwargs,
                'execution_time': 0.5,  # Simulated execution time in seconds
                'timestamp': timezone.now().isoformat()
            }
        }

@override_settings(**TEST_SETTINGS)
class TestingDashboardViewTest(TestCase):
    """Pruebas para la vista TestingDashboardView."""
    
    @classmethod
    def setUpTestData(cls):
        # Crear un usuario de prueba
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_dashboard_view_requires_login(self):
        """Verifica que la vista requiera autenticación."""
        url = reverse('core_testing:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirección a login
    
    def test_dashboard_view_authenticated(self):
        """Verifica que la vista funcione para usuarios autenticados."""
        self.client.force_login(self.user)
        url = reverse('core_testing:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core_testing/dashboard.html')
    
    @patch('core_testing.views.views.discover_testing_interfaces')
    def test_get_context_data(self, mock_discover):
        """Verifica que el contexto incluya las interfaces disponibles."""
        # Configurar el mock para devolver nuestra interfaz de prueba
        mock_interface = MockTestingInterface()
        mock_discover.return_value = {'mock_interface': mock_interface}
        
        # Crear una solicitud autenticada
        request = self.factory.get('/')
        request.user = self.user
        
        # Llamar a la vista
        view = TestingDashboardView()
        view.request = request
        context = view.get_context_data()
        
        # Verificar que el contexto tenga los datos esperados
        self.assertIn('interfaces', context)
        self.assertIn('mock_interface', context['interfaces'])
        self.assertEqual(context['interfaces']['mock_interface'].name, "Mock Interface")


class TestInterface(TestingInterface):
    """Interfaz de prueba para las pruebas unitarias."""
    name = "Test Interface"
    description = "Interfaz de prueba para pruebas unitarias"
    
    def get_available_tests(self):
        return [{'id': 'test1', 'name': 'Test 1', 'description': 'Test de prueba'}]
    
    def get_test_form(self, test_id, request=None, initial=None):
        return "<form>Test Form</form>"
    
    def run_test(self, test_id, **kwargs):
        return {'status': 'success', 'message': 'Test ejecutado correctamente'}


class TestInterfaceView(InterfaceTestingView):
    """Vista de prueba que implementa InterfaceTestingView."""
    interface_class = TestInterface
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.kwargs = {}


@override_settings(**TEST_SETTINGS)
class InterfaceTestingViewTest(TestCase):
    """Pruebas para la vista InterfaceTestingView."""
    
    @classmethod
    def setUpTestData(cls):
        # Crear un usuario de prueba
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get_interface_class_success(self):
        """Verifica que se pueda obtener correctamente una clase de interfaz."""
        # Crear una instancia de la vista de prueba que ya tiene el interface_class definido
        view = TestInterfaceView()
        
        # Llamar al método bajo prueba
        interface_class = view.get_interface_class()
        
        # Verificar que se devuelve la clase correcta
        self.assertEqual(interface_class, TestInterface)
    
    def test_get_interface(self):
        """Verifica que se pueda obtener una instancia de la interfaz."""
        # Crear una instancia de la vista de prueba
        view = TestInterfaceView()
        view.kwargs = {'interface_name': 'test_interface'}
        
        # Llamar al método bajo prueba
        interface = view.get_interface()
        
        # Verificar que se devuelve una instancia de la interfaz
        self.assertIsInstance(interface, TestInterface)
    
    def test_get_context_data(self):
        """Verifica que el contexto incluya los datos necesarios."""
        # Crear una instancia de la vista de prueba
        view = TestInterfaceView()
        view.kwargs = {'interface_name': 'test_interface'}
        
        # Llamar al método bajo prueba
        context = view.get_context_data(test_key='test_value')
        
        # Verificar que el contexto incluya los datos esperados
        self.assertIn('test_key', context)
        self.assertEqual(context['test_key'], 'test_value')
    
    def test_get_request(self):
        """Verifica que la vista responda correctamente a una petición GET."""
        # Crear una petición GET autenticada
        request = self.factory.get('/testing/interface/test_interface/')
        request.user = self.user
        
        # Llamar a la vista usando as_view()
        response = TestInterfaceView.as_view()(request, interface_name='test_interface')
        
        # Renderizar la respuesta
        response.render()
        
        # Verificar la respuesta
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Interface', response.content)


@override_settings(**TEST_SETTINGS)
class RunTestApiTest(TestCase):
    """Pruebas para la vista run_test_api."""
    
    @classmethod
    def setUpTestData(cls):
        # Crear un usuario de prueba
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
    
    def setUp(self):
        self.factory = RequestFactory()
    
    @patch('core_testing.views.views.import_module')
    def test_run_test_api_success(self, mock_import):
        """Verifica que se pueda ejecutar una prueba correctamente."""
        # Usar nuestra implementación mock de TestingInterface
        mock_interface = MockTestingInterface()
        
        # Configurar el mock para import_module
        mock_module = MagicMock()
        mock_module.TestInterface = MagicMock(return_value=mock_interface)
        mock_import.return_value = mock_module
        
        # Crear una solicitud POST
        url = reverse('core_testing:run_test', args=['mock_interface'])
        test_data = {'test_id': 'test1', 'param1': 'value1'}
        request = self.factory.post(
            url,
            data=test_data,
            content_type='application/json'
        )
        request.user = self.user
        
        # Llamar a la vista
        response = run_test_api(request, 'mock_interface')
        
        # Verificar resultados
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['test_id'], 'test1')
        self.assertIn('Test test1 executed successfully', response_data['message'])
        self.assertEqual(response_data['details'], {'param1': 'value1'})
    
    @patch('core_testing.views.views.import_module')
    def test_run_test_api_invalid_interface(self, mock_import):
        """Verifica que se maneje correctamente una interfaz inválida."""
        # Configurar el mock para simular un error de importación
        mock_import.side_effect = ImportError("No module named 'invalid_interface'")
        
        url = reverse('core_testing:run_test', args=['invalid_interface'])
        request = self.factory.post(
            url,
            data={'test_id': 'test1'},
            content_type='application/json'
        )
        request.user = self.user
        
        response = run_test_api(request, 'invalid_interface')
        self.assertEqual(response.status_code, 404)
    
    def test_run_test_api_missing_test_id(self):
        """Verifica que se maneje correctamente la falta de test_id."""
        url = reverse('core_testing:run_test', args=['mock_interface'])
        request = self.factory.post(
            url,
            data={},
            content_type='application/json'
        )
        request.user = self.user
        
        response = run_test_api(request, 'mock_interface')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertIn('test_id', response_data['error'])


@override_settings(**TEST_SETTINGS)
class TestRunDetailViewTest(TestCase):
    """Pruebas para la vista TestRunDetailView."""
    
    @classmethod
    def setUpTestData(cls):
        # Crear un usuario de prueba
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        
        # Crear un test run de prueba
        cls.test_run = TestRun.objects.create(
            test_id='test1',
            interface_name='mock_interface',
            status='completed',
            result={'success': True, 'message': 'Test passed'},
            created_by=cls.user
        )
    
    def setUp(self):
        self.factory = RequestFactory()
        self.mock_interface = MockTestingInterface()
    
    def test_get_context_data(self):
        """Verifica que el contexto incluya el test run."""
        view = TestRunDetailView()
        view.kwargs = {'pk': self.test_run.pk}
        view.request = self.factory.get('/')
        view.request.user = self.user
        
        context = view.get_context_data()
        
        self.assertIn('test_run', context)
        self.assertEqual(context['test_run'], self.test_run)
        self.assertEqual(context['test_run'].test_id, 'test1')
    
    def test_get_object(self):
        """Verifica que se pueda obtener el objeto TestRun correctamente."""
        view = TestRunDetailView()
        view.kwargs = {'pk': self.test_run.pk}
        
        obj = view.get_object()
        
        self.assertEqual(obj, self.test_run)
        self.assertEqual(obj.test_id, 'test1')
        self.assertEqual(obj.interface_name, 'mock_interface')
    
    def test_get_object_does_not_exist(self):
        """Verifica que se lance una excepción cuando el TestRun no existe."""
        view = TestRunDetailView()
        view.kwargs = {'pk': 9999}  # ID que no existe
        
        with self.assertRaises(Http404):
            view.get_object()
    
    def test_get_queryset(self):
        """Verifica que el queryset devuelva los test runs correctos."""
        # Crear otro test run con un usuario diferente
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            is_staff=True
        )
        other_test_run = TestRun.objects.create(
            test_id='test2',
            interface_name='mock_interface',
            status='completed',
            created_by=other_user
        )
        
        view = TestRunDetailView()
        view.request = self.factory.get('/')
        view.request.user = self.user
        
        # Debería devolver solo los test runs del usuario actual
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().test_id, 'test1')
    
    def test_get_test_run_detail(self):
        """Verifica que se pueda ver el detalle de un test run."""
        url = reverse('core_testing:testrun_detail', args=[self.test_run.id])
        request = self.factory.get(url)
        request.user = self.user
        
        response = TestRunDetailView.as_view()(request, run_id=self.test_run.id)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core_testing/testrun_detail.html')
        self.assertEqual(response.context_data['test_run'], self.test_run)
        
    def test_get_nonexistent_test_run(self):
        """Verifica que se maneje correctamente un test run que no existe."""
        non_existent_id = 9999
        request = self.factory.get('/')
        request.user = self.user
        
        with self.assertRaises(TestRun.DoesNotExist):
            TestRunDetailView.as_view()(request, run_id=non_existent_id)


@override_settings(**TEST_SETTINGS)
class TestCoverageReportViewTest(TestCase):
    """Pruebas para la vista TestCoverageReportView."""
    
    @classmethod
    def setUpTestData(cls):
        # Crear un usuario de prueba
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        
        # Crear datos de cobertura de prueba
        cls.coverage = TestCoverage.objects.create(
            interface_name='mock_interface',
            total_tests=10,
            passed=8,
            failed=1,
            skipped=1,
            coverage_percentage=80.0,
            last_run=timezone.now(),
            created_by=cls.user
        )
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_get_coverage_report(self):
        """Verifica que se pueda ver el informe de cobertura."""
        url = reverse('core_testing:coverage_report')
        self.client.force_login(self.user)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core_testing/coverage_report.html')
        self.assertIn('coverage_data', response.context)
    
    def test_get_coverage_data(self):
        """Verifica que se obtengan correctamente los datos de cobertura."""
        view = TestCoverageReportView()
        view.request = self.factory.get('/')
        view.request.user = self.user
        
        coverage_data = view.get_coverage_data()
        
        self.assertEqual(len(coverage_data), 1)
        self.assertEqual(coverage_data[0]['interface_name'], 'mock_interface')
        self.assertEqual(coverage_data[0]['coverage_percentage'], 80.0)
        self.assertEqual(coverage_data[0]['passed'], 8)
        self.assertEqual(coverage_data[0]['failed'], 1)
        self.assertEqual(coverage_data[0]['skipped'], 1)
    
    def test_get_context_data(self):
        """Verifica que el contexto incluya los datos de cobertura."""
        view = TestCoverageReportView()
        view.request = self.factory.get('/')
        view.request.user = self.user
        
        context = view.get_context_data()
        
        self.assertIn('coverage_data', context)
        self.assertEqual(len(context['coverage_data']), 1)
        self.assertEqual(context['coverage_data'][0]['interface_name'], 'mock_interface')
    
    def test_get_queryset(self):
        """Verifica que el queryset devuelva solo los datos de cobertura del usuario."""
        # Crear otro usuario y datos de cobertura
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123',
            is_staff=True
        )
        TestCoverage.objects.create(
            interface_name='other_interface',
            total_tests=5,
            passed=4,
            failed=1,
            skipped=0,
            coverage_percentage=80.0,
            last_run=timezone.now(),
            created_by=other_user
        )
        
        view = TestCoverageReportView()
        view.request = self.factory.get('/')
        view.request.user = self.user
        
        # Debería devolver solo los datos de cobertura del usuario actual
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().interface_name, 'mock_interface')
