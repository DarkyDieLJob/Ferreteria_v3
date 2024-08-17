import pytest
from ddf import G
from .factories import ClienteFixture, ArticuloVendidoFixture, MetodoPagoFixture, Transaccion, CierreZ, TransaccionFixture


class AppFacturacion:
    def __init__(self):
        self.cliente = ClienteFixture()
        self.articulo_vendido = ArticuloVendidoFixture()
        self.metodo_pago = MetodoPagoFixture()
        self.transaccion = TransaccionFixture()
        self.cierre_z = G(CierreZ)

@pytest.fixture
def facturacion():
    return AppFacturacion()


