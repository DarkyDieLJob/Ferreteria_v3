import pytest

from facturacion.models import Cliente, ArticuloVendido , MetodoPago, Transaccion, CierreZ


@pytest.mark.django_db
def test_cliente_creation(facturacion):
    assert isinstance(facturacion.cliente, Cliente)

@pytest.mark.django_db
def test_articulo_vendido_creation(facturacion):
    assert isinstance(facturacion.articulo_vendido, ArticuloVendido)

@pytest.mark.django_db
def test_metodo_pago_creation(facturacion):
    assert isinstance(facturacion.metodo_pago, MetodoPago)

@pytest.mark.django_db
def test_transaccion_creation(facturacion):
    assert isinstance(facturacion.transaccion, Transaccion)

@pytest.mark.django_db
def test_cierre_z_creation(facturacion):
    assert isinstance(facturacion.cierre_z, CierreZ)