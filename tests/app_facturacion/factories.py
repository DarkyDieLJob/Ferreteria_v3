import factory
from django.contrib.auth.models import User
from facturacion.models import Cliente, ArticuloVendido , MetodoPago, Transaccion, CierreZ


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = "darkydiel"
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')  

class ClienteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cliente

    # Define los diferentes tipos de clientes
    exento = factory.SubFactory('facturacion.factories.ClienteFactory', responsabilidad_iva='E')
    responsable_inscripto = factory.SubFactory('facturacion.factories.ClienteFactory', responsabilidad_iva='I')
    consumidor_final = factory.SubFactory('facturacion.factories.ClienteFactory', responsabilidad_iva='C')

class FacturacionFactory(factory.django.DjangoModelFactory):
    @classmethod
    def get_usuario():
        return UserFactory()
