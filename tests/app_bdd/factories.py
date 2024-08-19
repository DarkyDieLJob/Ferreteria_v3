# No son Factories. Sino armadores de Fixtures de pytest
import pytest
from ddf import G
from bdd.models import Item, Carrito
from django.contrib.auth.models import User

class CarritoFixture:
    def __init__(self):
        self.carrito = G(
            Carrito,
            usuario=G(User),
        )

    def get_usuario(self):
        return [
            self.carrito,
        ]


class ItemFixture:
    def __init__(self):
        self.item = G(
            Item,
            codigo="1234/as",
            descripcion="Descripcon de articulo",
        )
        self.item_descripcion_no_asci = G(
            Item,
            codigo="5678/df",
            descripcion="CAðO ALUMINIO CORRUGADO no asci ",
        )

    def get_items(self):
        return [
            self.item,
            self.item_descripcion_no_asci,
        ]