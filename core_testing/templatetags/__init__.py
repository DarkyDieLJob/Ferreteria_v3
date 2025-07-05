"""
Paquete de filtros personalizados para plantillas.

Este paquete contiene filtros personalizados para ser utilizados en las plantillas de Django.
"""

# Importar los filtros para que estén disponibles al cargar el paquete
from .testing_filters import *  # noqa

# Asegurarse de que los filtros estén registrados
try:
    from django.template import Library
    register = Library()
    
    # Registrar manualmente el filtro coverage_color si no está registrado
    if 'coverage_color' not in register.filters:
        from .testing_filters import coverage_color
        register.filter('coverage_color', coverage_color)
        
except ImportError:
    pass
