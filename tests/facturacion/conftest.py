import os
import sys
import pytest
from ddf import G

# Añadir el directorio raíz al path de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Ahora podemos importar los modelos de facturación
from facturacion import models

# Clase de ayuda para agrupar instancias relacionadas
class FacturacionTestData:
    """Clase para agrupar instancias de prueba relacionadas con facturación"""
    def __init__(self):
        # Modelos básicos
        self.cliente = G(models.Cliente)
        
        # Agregar aquí más instancias de modelos según sea necesario

# Fixture principal que proporciona acceso a todos los datos de prueba
@pytest.fixture
def facturacion():
    """Fixture que proporciona acceso a instancias de prueba de facturación"""
    return FacturacionTestData()

# Fixtures individuales para cada modelo
@pytest.fixture
def cliente():
    """Fixture que devuelve una instancia de Cliente"""
    return G(models.Cliente)

# Puedes agregar más fixtures específicas según sea necesario
# Ejemplo:
# @pytest.fixture
# def otro_modelo():
#     return G(models.OtroModelo)
