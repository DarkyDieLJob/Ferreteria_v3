"""
Paquete que contiene las interfaces de testing.

Cada módulo en este paquete debe definir una clase que herede de TestingInterface.
"""

# Importar las interfaces disponibles para facilitar el acceso
from .example_interface import ExampleTestingInterface  # noqa
from .test_interface import TestInterface  # noqa

__all__ = [
    'ExampleTestingInterface',
    'TestInterface',
]
