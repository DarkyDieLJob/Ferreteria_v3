import pytest
from ddf import G
from facturacion.models import Cliente, ArticuloVendido , MetodoPago, Transaccion, CierreZ

class ClienteFixture:
    def __init__(self):
        self.exento = G(Cliente, responsabilidad_iva='E')
        self.responsable_inscripto = G(Cliente, responsabilidad_iva='I')
        self.consumidor_final = G(Cliente, responsabilidad_iva='C')

class MetodoPagoFixture:
    def __init__(self):
        self.efectivo_sin_ticket = G(MetodoPago, display='Efectivo S/Ticket')
        self.efectivo_con_ticket = G(MetodoPago, display='Efectivo con Ticket')
        self.credito = G(MetodoPago, display='Crédito')
        self.debito = G(MetodoPago, display='Débito')
        self.mercado_pago = G(MetodoPago, display='Mercado Pago')
        self.cuenta_dni = G(MetodoPago, display='Cuenta DNI')
        self.maestro = G(MetodoPago, display='Maestro')

class ArticuloVendidoFixture:
    def __init__(self):
        self.vendido_sin_registro = G(ArticuloVendido)
        self.vendido_con_registro = G(ArticuloVendido)
        self.vendido_con_sin_registro = G(ArticuloVendido)

class AppFacturacion:
    def __init__(self, cliente, metodo_pago, articulo_vendido):
        self.cliente = cliente
        self.articulo_vendido = articulo_vendido
        self.metodo_pago = metodo_pago
        self.transaccion = G(Transaccion)
        self.cierre_z = G(CierreZ)

@pytest.fixture
def facturacion():
    return AppFacturacion(
        ClienteFixture(),
        ArticuloVendidoFixture(),
        MetodoPagoFixture()
        )
