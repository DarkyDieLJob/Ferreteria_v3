"""
Pruebas para la interfaz de ejemplo.
"""
from django.test import TestCase, RequestFactory
from django.http import HttpRequest

# Importar la interfaz de ejemplo
from core_testing.testing_interfaces.example_interface import ExampleTestingInterface


class ExampleTestingInterfaceTest(TestCase):
    """Pruebas para la interfaz de ejemplo."""
    
    def setUp(self):
        self.interface = ExampleTestingInterface()
        self.factory = RequestFactory()
        
    def test_interface_attributes(self):
        """Verifica los atributos de la interfaz."""
        self.assertEqual(self.interface.name, "Ejemplo de Interfaz")
        self.assertEqual(self.interface.description, "Interfaz de ejemplo para testing")
        self.assertEqual(self.interface.version, "1.0.0")
        
    def test_get_tests(self):
        """Verifica que get_tests() devuelva la lista de pruebas."""
        tests = self.interface.get_tests()
        self.assertIsInstance(tests, list)
        self.assertGreater(len(tests), 0)
        
        # Verificar la estructura de cada prueba
        for test in tests:
            self.assertIn('id', test)
            self.assertIn('name', test)
            self.assertIn('description', test)
            
    def test_run_test_success(self):
        """Verifica que run_test() ejecute una prueba correctamente."""
        # Obtener el ID de la primera prueba
        test_id = self.interface.get_tests()[0]['id']
        
        # Ejecutar la prueba
        result = self.interface.run_test(test_id, param1='value1')
        
        # Verificar el resultado
        self.assertIn('success', result)
        self.assertIn('message', result)
        self.assertIn('details', result)
        self.assertEqual(result['details']['test_id'], test_id)
        self.assertEqual(result['details']['param1'], 'value1')
        
    def test_run_test_invalid_id(self):
        """Verifica que run_test() maneje correctamente un ID de prueba inválido."""
        with self.assertRaises(ValueError) as context:
            self.interface.run_test('invalid_test_id')
            
        self.assertIn('Prueba no encontrada', str(context.exception))
        
    def test_get_test_form(self):
        """Verifica que get_test_form() devuelva el formulario HTML esperado."""
        # Obtener el ID de la primera prueba
        test_id = self.interface.get_tests()[0]['id']
        
        # Obtener el formulario sin request
        form_html = self.interface.get_test_form(test_id)
        self.assertIsInstance(form_html, str)
        self.assertIn('<form', form_html)
        
        # Obtener el formulario con request
        request = self.factory.get('/')
        form_html_with_request = self.interface.get_test_form(test_id, request)
        self.assertIsInstance(form_html_with_request, str)
        self.assertIn('<form', form_html_with_request)
