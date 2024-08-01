import pytest

from pedido.models import Pedido, Vendido


@pytest.mark.django_db
def test_vendido_creation(pedido):
    assert isinstance(pedido.vendido, Vendido)

@pytest.mark.django_db
def test_pedido_creation(pedido):
    assert isinstance(pedido.pedido, Pedido)