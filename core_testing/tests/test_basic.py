from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class BasicTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear un usuario de prueba
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password,
            is_staff=True  # Asegurarse de que el usuario tenga permisos de administrador
        )
        # Autenticar al usuario
        self.client.login(username=self.username, password=self.password)

    def test_dashboard_view(self):
        """Test that the dashboard view returns a 200 status code."""
        response = self.client.get(reverse('core_testing:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard de Testing')

    def test_discover_interfaces(self):
        """Test that the test_interfaces view returns a 200 status code."""
        response = self.client.get(reverse('core_testing:test_interfaces'))
        self.assertEqual(response.status_code, 200)
