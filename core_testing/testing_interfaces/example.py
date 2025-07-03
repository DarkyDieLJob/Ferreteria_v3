"""
Ejemplo de interfaz de testing.
Implementa una interfaz de prueba simple para demostrar el funcionamiento.
"""
from typing import List, Dict, Any
from django.http import HttpRequest

from .base import TestingInterface


class ExampleTestingInterface(TestingInterface):
    """Interfaz de ejemplo para testing."""
    
    name = "Ejemplo de Testing"
    description = "Interfaz de ejemplo para demostrar el sistema de testing"
    version = "1.0.0"
    
    def get_available_tests(self) -> List[Dict[str, Any]]:
        """Retorna la lista de tests disponibles."""
        return [
            {
                'id': 'test_1',
                'name': 'Test de Ejemplo 1',
                'description': 'Un test de ejemplo simple',
                'parameters': [
                    {
                        'name': 'param1',
                        'type': 'string',
                        'required': True,
                        'default': 'valor predeterminado',
                        'help_text': 'Parámetro de ejemplo 1'
                    }
                ]
            },
            {
                'id': 'test_2',
                'name': 'Test de Ejemplo 2',
                'description': 'Otro test de ejemplo',
                'parameters': [
                    {
                        'name': 'param2',
                        'type': 'number',
                        'required': True,
                        'default': 42,
                        'help_text': 'Parámetro numérico de ejemplo'
                    }
                ]
            }
        ]
    
    def run_test(self, test_id: str, **kwargs) -> Dict[str, Any]:
        """Ejecuta un test específico."""
        if test_id == 'test_1':
            return {
                'success': True,
                'message': 'Test de ejemplo 1 ejecutado correctamente',
                'data': {
                    'param1': kwargs.get('param1', 'No proporcionado'),
                    'timestamp': '2023-01-01T12:00:00Z'
                }
            }
        elif test_id == 'test_2':
            return {
                'success': True,
                'message': 'Test de ejemplo 2 ejecutado correctamente',
                'data': {
                    'param2': kwargs.get('param2', 0),
                    'timestamp': '2023-01-01T12:00:01Z'
                }
            }
        else:
            return {
                'success': False,
                'message': f'Test con ID {test_id} no encontrado',
                'data': {}
            }
    
    def get_test_form(self, test_id: str, request: Optional[HttpRequest] = None) -> str:
        """Genera el formulario HTML para un test específico."""
        tests = self.get_available_tests()
        test = next((t for t in tests if t['id'] == test_id), None)
        
        if not test:
            return f'<div class="alert alert-danger">Test no encontrado: {test_id}</div>'
        
        # En una implementación real, aquí se generaría el formulario HTML
        # basado en los parámetros definidos en el test
        form_html = f'''
        <div class="card">
            <div class="card-header">
                <h5 class="mb-0">{test['name']}</h5>
            </div>
            <div class="card-body">
                <p class="card-text">{test['description']}</p>
                <div class="form-group">
                    <label for="test-params">Parámetros del test:</label>
                    <pre id="test-params">{test['parameters']}</pre>
                </div>
            </div>
        </div>
        '''
        
        return form_html
