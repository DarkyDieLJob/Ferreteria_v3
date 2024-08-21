# No son Factories. Sino armadores de Fixtures de pytest
import pytest
from ddf import G
from bdd.models import Item, Carrito, Articulo, ArticuloSinRegistro
from faker import Faker
from tests.factories import UserFixture

fake = Faker()

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

class CarritoFixture:
    def __init__(self):
        self.carrito_admin = G(
            Carrito,
            usuario=UserFixture().admin,
        )

    def get_usuario(self):
        return [
            self.carrito_admin,
        ]

class ArticuloFixture:
    def __init__(self):
        carrito_admin = CarritoFixture().carrito_admin
        self.articulo_asci_carrito_admin = G(
            Articulo,
            item=ItemFixture().item,
            carrito = carrito_admin,
            precio = 100.0,
            precio_efectivo = 90.0,
            )

        self.articulo_no_asci_carrito_admin = G(
            Articulo,
            item=ItemFixture().item_descripcion_no_asci,
            carrito = carrito_admin,
            precio = 100.0,
            precio_efectivo = 90.0,
        )
    
    def get_articulos_carrito_admin(self):
        return [
            self.articulo_asci_carrito_admin,
            self.articulo_no_asci_carrito_admin,
        ]
    
class ArticuloSinRegistroFixture:
    def __init__(self):
        carrito_admin = CarritoFixture().carrito_admin
        self.articulo_sr_asci_carrito_admin = G(
            ArticuloSinRegistro,
            descripcion=ItemFixture().item.descripcion,
            carrito = carrito_admin,
            precio = 100.0,    
        )

        self.articulo_sr_no_asci_carrito_admin = G(
            ArticuloSinRegistro,
            descripcion=ItemFixture().item_descripcion_no_asci.descripcion,
            carrito = carrito_admin,
            precio = 100.0,           
        )

    def get_articulos_sr_carrito_admin(self):
        return [
            self.articulo_sr_asci_carrito_admin,
            self.articulo_sr_no_asci_carrito_admin,
        ]


