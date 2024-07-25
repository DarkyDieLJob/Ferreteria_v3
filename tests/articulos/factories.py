import factory

from articulos.models import Articulo

class ArticuloFactory(factory.Factory):
    class Meta:
        model = Articulo