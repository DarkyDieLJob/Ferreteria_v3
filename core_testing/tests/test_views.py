"""
Pruebas para las vistas del módulo core_testing.
"""
from typing import List, Dict, Any, Optional
from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import Http404, HttpResponse, JsonResponse, HttpRequest
from django.utils import timezone
from unittest.mock import patch, MagicMock, ANY

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

# Importar las vistas desde el módulo correcto
from core_testing.views.views import (
    TestingDashboardView,
    InterfaceTestingView,
    TestRunDetailView,
    CoverageReportView
)

# Importar funciones de utilidad
from core_testing.views.views import (
    run_test_api,
    get_test_form
)

# Importar modelos
from core_testing.models import TestRun, ModuleCoverage
from core_testing.testing_interfaces.base import TestingView, TestingInterface
from core_testing.testing_interfaces.test_interface import TestInterface

# Obtener el modelo de usuario
User = get_user_model()

# Usamos la implementación concreta de TestInterface para las pruebas
# en lugar de crear un mock que herede de la clase abstracta
MockTestingInterface = TestInterface

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


class TestInterfaceView(TestingView):
    """Vista de prueba que implementa TestingView."""
    interface_class = TestInterface


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
            email='test@example.com'
        )
        
        # Crear un test run de prueba
        cls.test_run = TestRun.objects.create(
            name='Test Run 1',
            status='passed',
            started_at=timezone.now(),
            finished_at=timezone.now()
        )
    
    def setUp(self):
        self.client.force_login(self.user)
    
    def test_get_test_run_detail(self):
        """Verifica que se pueda ver el detalle de un test run."""
        url = reverse('core_testing:test_run_detail', args=[self.test_run.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core_testing/test_run_detail.html')
        self.assertEqual(response.context['test_run'], self.test_run)
    
    def test_get_nonexistent_test_run(self):
        """Verifica que se maneje correctamente un test run que no existe."""
        url = reverse('core_testing:test_run_detail', args=[9999])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)
    
    def test_get_context_data(self):
        """Verifica que el contexto incluya el test run."""
        view = TestRunDetailView()
        view.kwargs = {'pk': self.test_run.id}
        view.request = self.client.get('/').wsgi_request
        
        context = view.get_context_data()
        
        self.assertIn('test_run', context)
        self.assertEqual(context['test_run'], self.test_run)
    
    def test_get_object(self):
        """Verifica que se pueda obtener el objeto TestRun correctamente."""
        view = TestRunDetailView()
        view.kwargs = {'pk': self.test_run.id}
        view.request = self.client.get('/').wsgi_request
        
        obj = view.get_object()
        
        self.assertEqual(obj, self.test_run)
    
    def test_get_object_does_not_exist(self):
        """Verifica que se lance una excepción cuando el TestRun no existe."""
        view = TestRunDetailView()
        view.kwargs = {'pk': 9999}
        view.request = self.client.get('/').wsgi_request
        
        with self.assertRaises(Http404):
            view.get_object()
    
    def test_get_queryset(self):
        """Verifica que el queryset devuelva los test runs correctos."""
        view = TestRunDetailView()
        view.request = self.factory.get('/')
        view.request.user = self.user
        
        # Debería devolver todos los test runs
        queryset = view.get_queryset()
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().name, 'Test Run 1')
    
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
class CoverageReportViewTest(TestCase):
    """Pruebas para la vista CoverageReportView."""
    
    @classmethod
    def setUpTestData(cls):
        # Crear un usuario de prueba
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        
        # Crear una ejecución de prueba
        cls.test_run = TestRun.objects.create(
            name='Prueba de cobertura',
            status='passed',
            started_at=timezone.now(),
            finished_at=timezone.now()
        )
        
        # Crear datos de cobertura
        cls.module_coverage = ModuleCoverage.objects.create(
            module_name='core_testing.tests',
            coverage_percent=80.0,
            lines_covered=80,
            lines_missing=20,
            total_lines=100,
            test_run=cls.test_run,
            last_updated=timezone.now()
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
        self.assertGreaterEqual(len(response.context['coverage_data']), 1)
        # Verificar que los datos de cobertura estén en el contexto
        self.assertTrue(any(
            cov.module_name == 'core_testing.tests' 
            for cov in response.context['coverage_data']
        ))
    
    def test_get_coverage_data(self):
        """Verifica que se obtengan correctamente los datos de cobertura."""
        view = CoverageReportView()
        data = view.get_coverage_data()
        
        self.assertIn('total_coverage', data)
        self.assertIn('by_module', data)
        self.assertGreaterEqual(len(data['by_module']), 1)
        
        # Verificar que los datos de cobertura estén en los resultados
        module_data = next(
            (m for m in data['by_module'] if m.module_name == 'core_testing.tests'),
            None
        )
        self.assertIsNotNone(module_data)
        self.assertEqual(module_data.coverage_percent, 80.0)
    
    def test_get_context_data(self):
        """Verifica que el contexto incluya los datos de cobertura."""
        view = CoverageReportView()
        view.request = self.factory.get('/')
        view.request.user = self.user
        
        context = view.get_context_data()
        
        self.assertIn('coverage_data', context)
        self.assertIn('total_coverage', context)
        self.assertGreaterEqual(len(context['coverage_data']), 1)
        
        # Verificar que los datos de cobertura estén en el contexto
        self.assertTrue(any(
            cov.module_name == 'core_testing.tests' 
            for cov in context['coverage_data']
        ))
    def test_get_queryset(self):
        """Verifica que el queryset devuelva los datos de cobertura."""
        # Crear otra ejecución de prueba
        other_test_run = TestRun.objects.create(
            name='Otra prueba',
            status='passed',
            started_at=timezone.now(),
            finished_at=timezone.now()
        )
        
        # Crear datos de cobertura adicionales
        ModuleCoverage.objects.create(
            module_name='other.module',
            coverage_percent=90.0,
            lines_covered=90,
            lines_missing=10,
            total_lines=100,
            test_run=other_test_run,
            last_updated=timezone.now()
        )
        
        view = CoverageReportView()
        view.request = self.factory.get('/')
        view.request.user = self.user
        
        # Obtener el queryset
        qs = view.get_queryset()
        
        # Verificar que se devuelvan todos los datos de cobertura
        self.assertEqual(qs.count(), 2)
        
        # Verificar que los datos de cobertura estén en el queryset
        module_names = [m.module_name for m in qs]
        self.assertIn('core_testing.tests', module_names)
        self.assertIn('other.module', module_names)
