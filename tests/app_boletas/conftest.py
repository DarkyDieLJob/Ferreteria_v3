import pytest
from ddf import G
from boletas.models import Comando, Boleta, OrdenComando

class AppBoletas:
    def __init__(self):
        self.comando = G(Comando)
        self.boleta = G(Boleta)
        self.orden_comando = G(OrdenComando)

@pytest.fixture
def boletas():
    return AppBoletas()
