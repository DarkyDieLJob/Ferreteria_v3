import pytest
from ddf import G
from facturacion.models import Cliente, ArticuloVendido , MetodoPago, Transaccion, CierreZ
class AppFacturacion:
    def __init__(self):
        self.cliente = G(Cliente)
        self.articulo_vendido = G(ArticuloVendido)
        self.metodo_pago = G(MetodoPago)
        self.transaccion = G(Transaccion)
        self.cierre_z = G(CierreZ)

@pytest.fixture
def facturacion():
    return AppFacturacion()
