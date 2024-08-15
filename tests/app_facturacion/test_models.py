import pytest

from facturacion.models import Cliente, ArticuloVendido , MetodoPago, Transaccion, CierreZ


@pytest.mark.django_db
def test_cliente_creation(facturacion):
    assert isinstance(facturacion.cliente.exento, Cliente)
    assert isinstance(facturacion.cliente.responsable_inscripto, Cliente)
    assert isinstance(facturacion.cliente.consumidor_final, Cliente)

@pytest.mark.django_db
def test_articulo_vendido_creation(facturacion):
    assert isinstance(facturacion.articulo_vendido.vendido_sin_registro, ArticuloVendido)
    assert isinstance(facturacion.articulo_vendido.vendido_con_registro, ArticuloVendido)
    assert isinstance(facturacion.articulo_vendido.vendido_con_sin_registro, ArticuloVendido)

@pytest.mark.django_db
def test_metodo_pago_creation(facturacion):
    assert isinstance(facturacion.metodo_pago.efectivo_sin_ticket, MetodoPago)
    assert isinstance(facturacion.metodo_pago.efectivo_con_ticket, MetodoPago)
    assert isinstance(facturacion.metodo_pago.credito, MetodoPago)
    assert isinstance(facturacion.metodo_pago.debito, MetodoPago)
    assert isinstance(facturacion.metodo_pago.mercado_pago, MetodoPago)
    assert isinstance(facturacion.metodo_pago.cuenta_dni, MetodoPago)
    assert isinstance(facturacion.metodo_pago.maestro, MetodoPago)

@pytest.mark.django_db
def test_transaccion_creation(facturacion):
    assert isinstance(facturacion.transaccion, Transaccion)

@pytest.mark.django_db
def test_cierre_z_creation(facturacion):
    assert isinstance(facturacion.cierre_z, CierreZ)