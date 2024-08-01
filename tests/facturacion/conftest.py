import pytest
from ddf import G
from facturacion.models import Cliente

class AppFacturacion:
    def __init__(self):
        self.cliente = G(Cliente)

@pytest.fixture
def facturacion():
    return AppFacturacion()
