import pytest
from ddf import G
from x_cartel.models import Cartelitos, Carteles, CartelesCajon
from bdd.models import Item, Proveedor

class AppXcartel:
    def __init__(self):
        self.cartelitos = G(
            Cartelitos,
            item = G(Item),
            proveedor = G(Proveedor)
            )
        self.carteles = G(
            Carteles,
            item = G(Item),
            proveedor = G(Proveedor)
            )
        self.carteñes_cajon = G(
            CartelesCajon,
            item = G(Item),
            proveedor = G(Proveedor)
            )

@pytest.fixture
def x_cartel():
    return AppXcartel()
