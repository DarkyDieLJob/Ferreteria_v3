import pytest
from ddf import G
from articulos.models import Articulo, ArticuloProveedor, Cartel, Categoria, CodigoBarras, Marca, Proveedor


class AppArticulos:
    def __init__(self):
        self.marca = G(Marca)
        self.categoria = G(Categoria)
        self.cartel = G(Cartel)
        self.proveedor = G(Proveedor)
        self.articulo = G(
            Articulo, 
            marca=self.marca, 
            categoria=self.categoria
            )
        self.codigo_barras = G(
            CodigoBarras, 
            articulo=self.articulo
            )
        self.articulo_proveedor = G(
            ArticuloProveedor, 
            articulo=self.articulo, 
            proveedor=self.proveedor, 
            cartel=self.cartel
            )

@pytest.fixture
def articulos():
    return AppArticulos()
