import pytest

from boletas.models import Comando, Boleta, OrdenComando


@pytest.mark.django_db
def test_comando_creation(boletas):
    assert isinstance(boletas.comando, Comando)

@pytest.mark.django_db
def test_boleta_creation(boletas):
    assert isinstance(boletas.boleta, Boleta)

@pytest.mark.django_db
def test_orden_comando_creation(boletas):
    assert isinstance(boletas.orden_comando, OrdenComando)