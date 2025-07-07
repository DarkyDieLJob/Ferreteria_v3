"""
Configuración de pytest para el módulo core_testing.

Este archivo contiene configuraciones y fixtures específicas para las pruebas
unitarias del módulo core_testing.
"""
import os
import sys
import pytest
from django.conf import settings

# Asegurarse de que el directorio raíz esté en el path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar fixtures
from core_testing.fixtures import *

# Configuración específica para las pruebas de core_testing
def pytest_configure():
    """Configuración específica para las pruebas."""
    # Configuración adicional si es necesaria
    pass
