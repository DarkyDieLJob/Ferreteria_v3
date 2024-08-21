import pytest
from .factories import UserFixture
from ddf import G

class DefaultModels:
    def __init__(self):
        self.user = UserFixture()

@pytest.fixture
def default_models():
    return DefaultModels()