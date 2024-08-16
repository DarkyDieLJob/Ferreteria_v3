import factory
from django.contrib.auth.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = "darkydiel"
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')  
