from faker import Faker
from faker.providers import BaseProvider

fake = Faker()

class CuitProvider(BaseProvider):
    def cuit(self):
        init_number = fake.random_number(digits=2, fix_len=True)
        medium_number = fake.random_number(digits=8, fix_len=True)
        end_number = fake.random_number(digits=1, fix_len=True)
        return f"{init_number}-{medium_number}-{end_number}"