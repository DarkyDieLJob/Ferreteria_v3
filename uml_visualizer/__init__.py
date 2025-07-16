"""
Módulo para la visualización de diagramas UML de las aplicaciones del proyecto.

Este módulo proporciona una interfaz web para generar y visualizar diagramas UML
de los modelos de las aplicaciones de Django utilizando django-extensions y graphviz.
"""

# Exportar las vistas principales
from .views import (
    uml_dashboard,
    app_diagram,
    download_diagram,
    generate_app_diagram
)

__all__ = [
    'uml_dashboard',
    'app_diagram',
    'download_diagram',
    'generate_app_diagram'
]
