# No son Factories. Sino armadores de Fixtures de pytest
import pytest
from ddf import G
from facturacion.models import Cliente, ArticuloVendido , MetodoPago, Transaccion, CierreZ, Transaccion
from tests.conftest import DefaultModels
from tests.app_bdd.factories import ItemFixture
from bdd.models import Item


class ClienteFixture:
    def __init__(self):
        self.exento = G(Cliente, responsabilidad_iva='E')
        self.responsable_inscripto = G(Cliente, responsabilidad_iva='I')
        self.consumidor_final = G(Cliente, responsabilidad_iva='C')

    def get_clientes(self):
        return [
            self.exento,
            self.responsable_inscripto,
            self.consumidor_final
        ]
class MetodoPagoFixture:
    def __init__(self):
        self.efectivo_sin_ticket = G(MetodoPago, display='Efectivo S/Ticket')
        self.efectivo_con_ticket = G(MetodoPago, display='Efectivo con Ticket')
        self.credito = G(MetodoPago, display='Crédito')
        self.debito = G(MetodoPago, display='Débito')
        self.mercado_pago = G(MetodoPago, display='Mercado Pago')
        self.cuenta_dni = G(MetodoPago, display='Cuenta DNI')
        self.maestro = G(MetodoPago, display='Maestro')

    def get_metodos_de_pago(self):
        return [
            self.efectivo_sin_ticket,
            self.efectivo_con_ticket,
            self.credito,
            self.debito,
            self.mercado_pago,
            self.cuenta_dni,
            self.maestro,
        ]

class ArticuloVendidoFixture:
    def __init__(self):
        self.vendido_con_registro = G(
            ArticuloVendido,
            item=ItemFixture().item,
            )
        self.vendido_con_registro_no_asci = G(
            ArticuloVendido,
            item=ItemFixture().item_descripcion_no_asci,
        )

    def get_articulos_vendidos(self):
        return [
            self.vendido_con_registro,
            self.vendido_con_registro_no_asci,
        ]

class TransaccionFixture:
    '''
    cliente
    usuario
    articulos_vendidos
    metodo_de_pago
    fecha
    total
    '''
    def __init__(self):
        metodo_pago_fixture = MetodoPagoFixture()
        self.efectivo_con_ticket_consumidor_final = G(
            Transaccion,
            cliente=ClienteFixture().consumidor_final,
            usuario=DefaultModels().user.admin,
            articulos_vendidos=ArticuloVendidoFixture().get_articulos_vendidos(),
            metodo_de_pago=metodo_pago_fixture.efectivo_con_ticket,
            )

        self.efectivo_con_ticket_cliente_responsable_inscripto = G(
            Transaccion,
            cliente=ClienteFixture().responsable_inscripto,
            usuario=DefaultModels().user.admin,
            articulos_vendidos=ArticuloVendidoFixture().get_articulos_vendidos(),
            metodo_de_pago=metodo_pago_fixture.efectivo_con_ticket,
            )

        self.efectivo_con_ticket_cliente_exento = G(
            Transaccion,
            cliente=ClienteFixture().exento,
            usuario=DefaultModels().user.admin,
            articulos_vendidos=ArticuloVendidoFixture().get_articulos_vendidos(),
            metodo_de_pago=metodo_pago_fixture.efectivo_con_ticket,
            )

    def get_transacciones(self):
        return [
            self.efectivo_con_ticket_consumidor_final,
            self.efectivo_con_ticket_cliente_responsable_inscripto,
            self.efectivo_con_ticket_cliente_exento,
        ]
