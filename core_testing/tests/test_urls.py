"""
Pruebas para las URLs del módulo core_testing.
"""
import os
import django
from django.test import TestCase, override_settings
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.utils import timezone

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
django.setup()

# Importar las vistas
from core_testing.views.views import (
    TestingDashboardView,
    TestRunDetailView,
    CoverageReportView,
    TestRunListView
)
from core_testing.models import TestRun, ModuleCoverage

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

@override_settings(**TEST_SETTINGS)
class CoreTestingURLTests(TestCase):
    """Pruebas para las URLs del módulo core_testing."""
    
    @classmethod
    def setUpTestData(cls):
        # Crear un usuario de prueba
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        
        # Crear datos de prueba
        cls.test_run = TestRun.objects.create(
            name='Test Run 1',
            started_at='2023-01-01T00:00:00Z',
            status='passed',
            total_tests=10,
            tests_passed=10,
            tests_failed=0,
            tests_error=0,
            tests_skipped=0,
            coverage_percent=85.5
        )
        
        cls.module_coverage = ModuleCoverage.objects.create(
            module_name='test_module',
            coverage_percent=85.5,
            lines_covered=100,
            lines_missing=20,
            total_lines=120
        )
    
    def setUp(self):
        # Autenticar al usuario para las pruebas
        self.client.force_login(self.user)
    
    def test_dashboard_url_resolves(self):
        """Verifica que la URL del dashboard se resuelve correctamente."""
        url = reverse('core_testing:dashboard')
        self.assertEqual(url, '/testing/')
        
        # Verificar que la vista asociada sea la correcta
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, TestingDashboardView.as_view().__name__)
    
    def test_dashboard_url_accessible(self):
        """Verifica que la URL del dashboard sea accesible."""
        url = reverse('core_testing:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_run_detail_url_resolves(self):
        """Verifica que la URL de detalle de ejecución se resuelve correctamente."""
        url = reverse('core_testing:test_run_detail', kwargs={'pk': self.test_run.id})
        self.assertEqual(url, f'/testing/test-run/{self.test_run.id}/')
        
        # Verificar que la vista asociada sea la correcta
        resolver = resolve(f'/testing/test-run/{self.test_run.id}/')
        self.assertEqual(resolver.func.view_class, TestRunDetailView)
    
    def test_run_detail_url_accessible(self):
        """Verifica que la URL de detalle de ejecución sea accesible."""
        url = reverse('core_testing:test_run_detail', kwargs={'pk': self.test_run.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_coverage_report_url_resolves(self):
        """Verifica que la URL del reporte de cobertura se resuelve correctamente."""
        url = reverse('core_testing:coverage_report')
        self.assertEqual(url, '/testing/coverage/')
        
        # Verificar que la vista asociada sea la correcta
        resolver = resolve('/testing/coverage/')
        self.assertEqual(resolver.func.__name__, CoverageReportView.as_view().__name__)
    
    def test_coverage_report_url_accessible(self):
        """Verifica que la URL del reporte de cobertura sea accesible."""
        url = reverse('core_testing:coverage_report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    
    def test_nonexistent_run_detail_returns_404(self):
        """Verifica que se devuelva 404 para un ID de ejecución inexistente."""
        non_existent_id = 9999
        url = reverse('core_testing:test_run_detail', kwargs={'pk': non_existent_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_testrun_list_url(self):
        """Verifica que la URL de lista de ejecuciones funcione correctamente."""
        url = reverse('core_testing:testrun_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(resolve(url).func.view_class, TestRunListView)
    
    def test_urls_require_authentication(self):
        """Verifica que las URLs requieran autenticación."""
        self.client.logout()
        
        # Probar el dashboard
        url = reverse('core_testing:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirección a login
        
        # Probar el detalle de ejecución
        url = reverse('core_testing:test_run_detail', kwargs={'pk': self.test_run.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirección a login
        
        # Probar el reporte de cobertura
        url = reverse('core_testing:coverage_report')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirección a login
