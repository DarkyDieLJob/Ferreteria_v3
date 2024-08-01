import pytest
from ddf import G
from pedido.models import Pedido, Vendido

class AppPedidos:
    def __init__(self):
        self.vendido = G(Vendido)
        self.pedido = G(Pedido)

@pytest.fixture
def pedido():
    return AppPedidos()
