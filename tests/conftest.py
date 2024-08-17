import pytest
from .factories import UserFixture
from bdd.models import Carrito
from ddf import G

class DefaultModels:
    def __init__(self):
        self.user = UserFixture()
        self.carrito = G(Carrito)

@pytest.fixture
def default_models():
    return DefaultModels()