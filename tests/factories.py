# No son Factories. Sino armadores de Fixtures de pytest
from django.contrib.auth.models import User
from ddf import G
import factory
from faker import Faker

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    first_name = fake.name()
    last_name = fake.last_name()
    username = fake.user_name()
    password = fake.phone_number()
    email = f"{first_name}.{last_name}@info.com"
    is_staff = True
    is_superuser = True
    is_active = True

class UserFixture:
    def __init__(self):
        self.admin = G(
            User, 
            username = fake.user_name(),
            email = f"{fake.name()}.{fake.last_name()}@info.com",
        )

