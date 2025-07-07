"""
Configuración global de pytest para el proyecto Ferreteria_v3.

Este archivo se ejecuta antes de cualquier prueba y configura el entorno de pruebas.
"""
import os
import sys

# Asegurarse de que el directorio raíz esté en el path de Python
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configuración de Django para pruebas
import django
from django.conf import settings

# Configurar Django para pruebas
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')
django.setup()

# Configuración de cobertura
import pytest

# Deshabilitar plugins que pueden interferir con las pruebas
pytest_plugins = [
    'core_testing.fixtures',
]

# Configuración específica para las pruebas
def pytest_configure():
    """Configuración de pytest."""
    # Asegurarse de que las aplicaciones de prueba estén en INSTALLED_APPS
    if hasattr(settings, 'INSTALLED_APPS') and 'core_testing' not in settings.INSTALLED_APPS:
        settings.INSTALLED_APPS += ('core_testing',)
