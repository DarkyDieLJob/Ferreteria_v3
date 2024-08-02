import pytest

from x_cartel.models import Cartelitos, Carteles, CartelesCajon



@pytest.mark.django_db
def test_cartelitos_creation(x_cartel):
    assert isinstance(x_cartel.cartelitos, Cartelitos)

@pytest.mark.django_db
def test_carteles_creation(x_cartel):
    assert isinstance(x_cartel.carteles, Carteles)

@pytest.mark.django_db
def test_carteñes_cajon_creation(x_cartel):
    assert isinstance(x_cartel.carteñes_cajon, CartelesCajon)