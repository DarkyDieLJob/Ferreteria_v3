import pytest

from facturacion.models import Cliente

@pytest.mark.django_db
def test_marca_creation(facturacion):
    assert isinstance(facturacion.cliente, Cliente)