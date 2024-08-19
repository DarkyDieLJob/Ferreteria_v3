# No son Factories. Sino armadores de Fixtures de pytest
import pytest
from ddf import G
from bdd.models import Item

class ItemFixture:
    def __init__(self):
        self.item = G(Item)

    def get_items(self):
        return [
            self.item,
        ]