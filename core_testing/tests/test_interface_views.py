"""
Pruebas para las vistas de interfaces de testing.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class InterfaceViewsTestCase(TestCase):
    """Caso de prueba para las vistas de interfaces de testing."""
    
    @classmethod
    def setUpTestData(cls):
        """Configuración inicial para todas las pruebas."""
        # Crear un usuario para pruebas
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
    
    def setUp(self):
        """Configuración antes de cada prueba."""
        self.client = Client()
        # Autenticar al usuario
        self.client.login(username='testuser', password='testpass123')
    
    def test_example_interface_view_status_code(self):
        """Verifica que la vista de ejemplo devuelva un código 200."""
        # Usar la URL directa en lugar de reverse para evitar problemas de configuración
        response = self.client.get('/testing/interface/example/')
        self.assertEqual(response.status_code, 200)
    
    def test_example_advanced_interface_view_status_code(self):
        """Verifica que la vista de ejemplo avanzada devuelva un código 200."""
        # Usar la URL directa en lugar de reverse para evitar problemas de configuración
        response = self.client.get('/testing/interface/example_interface/')
        self.assertEqual(response.status_code, 200)
