import pytest
from ddf import G
from .factories import ClienteFixture, ArticuloVendidoFixture, MetodoPagoFixture, Transaccion, CierreZ, TransaccionFixture


class AppFacturacion:
    def __init__(self, usuario=None, carrito=None):
        self.cliente = ClienteFixture()
        self.articulo_vendido = ArticuloVendidoFixture(carrito)
        self.metodo_pago = MetodoPagoFixture()
        self.transaccion = TransaccionFixture(usuario, carrito)
        self.cierre_z = G(CierreZ)

@pytest.fixture
def facturacion():
    return AppFacturacion()


