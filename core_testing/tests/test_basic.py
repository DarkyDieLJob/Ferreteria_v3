from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class BasicTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Crear un superusuario para asegurar todos los permisos
        self.username = 'testadmin'
        self.password = 'adminpass123'
        self.user = User.objects.create_superuser(
            username=self.username,
            password=self.password,
            email='admin@example.com'
        )
        # Autenticar al usuario
        self.client.login(username=self.username, password=self.password)

    def test_dashboard_view(self):
        """Verifica que el dashboard sea accesible y muestre el título."""
        response = self.client.get(reverse('core_testing:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        
    # Nota: Se eliminó test_discover_interfaces ya que la funcionalidad ya no existe
