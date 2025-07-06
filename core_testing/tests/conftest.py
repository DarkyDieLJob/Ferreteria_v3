"""
Configuración de pytest para las pruebas de Django.
"""
import os
import sys
import pytest
import inspect
from abc import ABC, abstractmethod
from django.conf import settings

# Asegurar que estamos usando la configuración del proyecto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_config.settings')

def pytest_configure(config):
    """Configura el entorno de pruebas de Django."""
    # Usamos la configuración del proyecto en lugar de crear una nueva
    if not settings.configured:
        import django
        django.setup()
    
    # Configurar para ignorar advertencias específicas
    import warnings
    warnings.filterwarnings(
        'ignore',
        message=r".*cannot collect test class '.*' because it has a __init__ constructor.*",
        category=pytest.PytestCollectionWarning
    )

def pytest_collection_modifyitems(config, items):
    """Modifica la colección de pruebas para excluir clases abstractas."""
    remaining = []
    for item in items:
        # Saltar cualquier prueba en test_interfaces_base.py
        if 'test_interfaces_base.py' in str(item.fspath):
            continue
            
        # Verificar si es una clase de prueba
        if hasattr(item, 'cls') and item.cls is not None:
            # Verificar si la clase o alguna de sus bases es abstracta
            is_abstract = False
            for base in item.cls.__mro__:
                if hasattr(base, '__abstractmethods__') and base.__abstractmethods__:
                    is_abstract = True
                    break
            
            # Si no es abstracta, la mantenemos
            if not is_abstract:
                remaining.append(item)
        else:
            # Si no es una clase de prueba, la mantenemos
            remaining.append(item)
    
    # Reemplazar la lista de ítems
    items[:] = remaining

# Fixture para el cliente de prueba
@pytest.fixture
def client():
    from django.test import Client
    return Client()
