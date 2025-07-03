"""
Módulo base para las interfaces de testing.
Define la interfaz común que deben implementar todos los módulos de testing.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class TestingInterface(ABC):
    """
    Interfaz base para todos los módulos de testing.
    Define los métodos que deben implementar las interfaces de testing específicas.
    """
    
    # Metadatos de la interfaz
    name: str = "Interfaz Base"
    description: str = "Descripción de la interfaz de testing"
    version: str = "1.0.0"
    
    @abstractmethod
    def get_available_tests(self) -> List[Dict[str, Any]]:
        """
        Retorna una lista de tests disponibles en esta interfaz.
        
        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con información de los tests
        """
        pass
    
    @abstractmethod
    def run_test(self, test_id: str, **kwargs) -> Dict[str, Any]:
        """
        Ejecuta un test específico.
        
        Args:
            test_id: Identificador único del test a ejecutar
            **kwargs: Argumentos adicionales para el test
            
        Returns:
            Dict[str, Any]: Resultados del test
        """
        pass
    
    @abstractmethod
    def get_test_form(self, test_id: str, request: Optional[HttpRequest] = None) -> str:
        """
        Retorna el formulario HTML para configurar un test específico.
        
        Args:
            test_id: Identificador único del test
            request: Objeto HttpRequest opcional
            
        Returns:
            str: HTML del formulario
        """
        pass


class TestingView(LoginRequiredMixin, TemplateView):
    """
    Vista base para las interfaces de testing.
    Proporciona funcionalidad común para todas las vistas de testing.
    """
    template_name = "core_testing/testing_interface.html"
    interface_class = None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        interface = self.get_interface()
        
        context.update({
            'interface': interface,
            'tests': interface.get_available_tests(),
            'interface_name': interface.name,
            'interface_description': interface.description,
            'interface_version': interface.version,
        })
        
        return context
    
    def get_interface(self) -> TestingInterface:
        """
        Retorna una instancia de la interfaz de testing.
        
        Returns:
            TestingInterface: Instancia de la interfaz
        """
        if not self.interface_class:
            raise NotImplementedError("Debes definir interface_class en la vista")
        return self.interface_class()
    
    def post(self, request, *args, **kwargs):
        """Maneja las peticiones POST para ejecutar tests."""
        test_id = request.POST.get('test_id')
        if not test_id:
            return HttpResponse("ID de test no especificado", status=400)
        
        interface = self.get_interface()
        result = interface.run_test(test_id, request=request)
        
        return HttpResponse(
            render_to_string(
                'core_testing/test_result.html',
                {'result': result, 'test_id': test_id}
            )
        )
