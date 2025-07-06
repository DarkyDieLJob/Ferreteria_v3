"""
Pruebas para la clase base de interfaces de prueba.
"""
import pytest
from django.test import TestCase, RequestFactory
from django.http import HttpRequest
from unittest.mock import patch, MagicMock

from core_testing.testing_interfaces.base import TestingInterface, TestingView

# Evitar que pytest intente recolectar pruebas de la clase base
TestingInterface.__test__ = False


class TestingInterfaceTest(TestCase):
    """Pruebas para la clase base TestingInterface."""
    
    def test_abstract_methods(self):
        """Verifica que los métodos abstractos estén definidos."""
        # Crear una implementación concreta para probar
        class ConcreteTestingInterface(TestingInterface):
                name = "Concrete Interface"
                description = "Implementación concreta para pruebas"
                version = "1.0.0"
                
                def get_available_tests(self) -> list[dict[str, any]]:
                    return []
                    
                def run_test(self, test_id: str, **kwargs) -> dict[str, any]:
                    return {
                        'success': True,
                        'test_id': test_id,
                        'message': 'Test ejecutado correctamente',
                        'details': {}
                    }
                    
                def get_test_form(self, test_id: str, request: HttpRequest | None = None) -> str:
                    return "<form>Test Form</form>"
        
        # Verificar que se puede instanciar sin errores
        interface = ConcreteTestingInterface()
        self.assertIsInstance(interface, TestingInterface)
        
    def test_abstract_methods_not_implemented(self):
        """Verifica que no se pueda instanciar sin implementar métodos abstractos."""
        class IncompleteTestingInterface(TestingInterface):
            pass
            
        with self.assertRaises(TypeError):
            IncompleteTestingInterface()


class TestingViewTest(TestCase):
    """Pruebas para la clase base TestingView."""
    
    def setUp(self):
        self.factory = RequestFactory()
        
    def test_get_interface_not_implemented(self):
        """Verifica que get_interface() lance NotImplementedError si no está implementado."""
        class TestView(TestingView):
            pass
            
        view = TestView()
        with self.assertRaises(NotImplementedError):
            view.get_interface()
            
    def test_get_interface_implemented(self):
        """Verifica que get_interface() devuelva la interfaz correcta."""
        class MockInterface(TestingInterface):
            name = "Mock Interface"
            description = "Interfaz simulada para pruebas"
            version = "1.0.0"
            
            def get_available_tests(self) -> list[dict[str, any]]:
                return []
                
            def run_test(self, test_id: str, **kwargs) -> dict[str, any]:
                return {
                    'success': True,
                    'test_id': test_id,
                    'message': 'Test simulado ejecutado',
                    'details': {}
                }
                
            def get_test_form(self, test_id: str, request: HttpRequest | None = None) -> str:
                return "<form>Test Form</form>"
                
        class TestView(TestingView):
            def get_interface(self):
                return MockInterface()
                
        view = TestView()
        interface = view.get_interface()
        self.assertIsInstance(interface, MockInterface)
        
    def test_get_context_data(self):
        """Verifica que get_context_data() incluya la interfaz en el contexto."""
        class MockInterface(TestingInterface):
            name = "Mock Interface"
            description = "Interfaz simulada para pruebas"
            version = "1.0.0"
            
            def get_available_tests(self) -> list[dict[str, any]]:
                return [{
                    'id': 'test1', 
                    'name': 'Test 1',
                    'description': 'Test de ejemplo',
                    'form_required': False
                }]
                
            def run_test(self, test_id: str, **kwargs) -> dict[str, any]:
                return {
                    'success': True,
                    'test_id': test_id,
                    'message': 'Test simulado ejecutado',
                    'details': {}
                }
                
            def get_test_form(self, test_id: str, request: HttpRequest | None = None) -> str:
                return "<form>Test Form</form>"
                
        class TestView(TestingView):
            template_name = 'core_testing/base_testing.html'
            
            def get_interface(self):
                return MockInterface()
                
        request = self.factory.get('/')
        view = TestView()
        view.request = request
        
        context = view.get_context_data()
        self.assertIn('interface', context)
        self.assertEqual(context['interface'].name, "Mock Interface")
        self.assertIn('tests', context)
        self.assertEqual(len(context['tests']), 1)
        self.assertEqual(context['tests'][0]['name'], 'Test 1')
