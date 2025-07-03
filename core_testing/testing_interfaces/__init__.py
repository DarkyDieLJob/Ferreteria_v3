"""
Paquete que contiene las interfaces de testing.

Cada módulo en este paqueto debe definir una clase que herede de TestingInterface.
"""

# Importar las interfaces disponibles para facilitar el acceso
from .example import ExampleTestingInterface  # noqa

__all__ = ['ExampleTestingInterface']
