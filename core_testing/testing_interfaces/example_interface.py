"""
Ejemplo de implementación de una interfaz de testing.
Muestra cómo crear una interfaz personalizada para un módulo específico.
"""
import random
from typing import Dict, List, Any, Optional
from django.http import HttpRequest
from django import forms

from .base import TestingInterface


class ExampleTestForm(forms.Form):
    """Formulario de ejemplo para el test."""
    param1 = forms.CharField(label="Parámetro 1", required=True)
    param2 = forms.IntegerField(label="Parámetro 2", required=False, initial=42)


class ExampleTestingInterface(TestingInterface):
    """
    Ejemplo de implementación de TestingInterface.
    Esta clase muestra cómo implementar una interfaz de testing personalizada.
    """
    
    name = "Ejemplo de Interfaz"
    description = "Interfaz de ejemplo para demostración"
    version = "1.0.0"
    
    def get_available_tests(self) -> List[Dict[str, Any]]:
        """Retorna la lista de tests disponibles."""
        return [
            {
                'id': 'test_basico',
                'name': 'Test Básico',
                'description': 'Un test básico de ejemplo',
                'form_required': True
            },
            {
                'id': 'test_avanzado',
                'name': 'Test Avanzado',
                'description': 'Un test más avanzado con más opciones',
                'form_required': True
            },
            {
                'id': 'test_rapido',
                'name': 'Test Rápido',
                'description': 'Un test rápido sin configuración',
                'form_required': False
            }
        ]
    
    def run_test(self, test_id: str, **kwargs) -> Dict[str, Any]:
        """Ejecuta el test especificado."""
        request = kwargs.get('request')
        
        if test_id == 'test_basico':
            form = ExampleTestForm(request.POST if request else None)
            if form.is_valid():
                # Lógica del test básico
                return {
                    'success': True,
                    'message': 'Test básico completado con éxito',
                    'data': {
                        'param1': form.cleaned_data['param1'],
                        'param2': form.cleaned_data['param2']
                    }
                }
            else:
                return {
                    'success': False,
                    'message': 'Error en el formulario',
                    'errors': form.errors
                }
                
        elif test_id == 'test_avanzado':
            # Lógica del test avanzado
            return {
                'success': True,
                'message': 'Test avanzado completado',
                'data': {
                    'resultado': random.randint(1, 100)
                }
            }
            
        elif test_id == 'test_rapido':
            # Lógica del test rápido
            return {
                'success': True,
                'message': 'Test rápido completado',
                'data': {
                    'tiempo_ejecucion': f"{random.uniform(0.1, 2.0):.2f} segundos"
                }
            }
            
        return {
            'success': False,
            'message': f'Test con ID {test_id} no encontrado'
        }
    
    def get_test_form(self, test_id: str, request: Optional[HttpRequest] = None) -> str:
        """Retorna el formulario HTML para el test especificado."""
        if test_id in ['test_basico', 'test_avanzado']:
            form = ExampleTestForm()
            return f"""
            <form id="testForm" method="post" action="">
                {form.as_p()}
                <input type="hidden" name="test_id" value="{test_id}">
                <button type="submit" class="btn btn-primary">Ejecutar Test</button>
            </form>
            """
        return ""


# Importar TestingView desde el módulo base
from django.views.generic import TemplateView
from .base import TestingView, TestingInterface

# Vista específica para esta interfaz
class ExampleTestingView(TestingView):
    """Vista para la interfaz de ejemplo."""
    interface_class = ExampleTestingInterface
    template_name = "core_testing/example_interface.html"
    
    def get_context_data(self, **kwargs):
        """Añade el contexto necesario para la plantilla."""
        context = super().get_context_data(**kwargs)
        context['interface'] = self.get_interface()
        return context
