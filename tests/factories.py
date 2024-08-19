# No son Factories. Sino armadores de Fixtures de pytest
from django.contrib.auth.models import User
from ddf import G
import factory
from faker import Faker

fake = Faker()

class UserFixture:
    def __init__(self):
        self.admin = G(
            User, 
            username = fake.user_name(),
            email = f"{fake.name()}.{fake.last_name()}@info.com",
        )

