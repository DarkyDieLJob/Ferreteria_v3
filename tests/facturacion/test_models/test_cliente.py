from django.test import TestCase
from facturacion.models import Cliente

class ClienteModelTest(TestCase):
    def setUp(self):
        self.cliente_data = {
            'razon_social': 'Cliente de Prueba S.A.',
            'cuit_dni': '20345678901',
            'responsabilidad_iva': 'I',  # Responsable Inscripto
            'tipo_documento': 'C',  # CUIT
            'domicilio': 'Calle Falsa 123',
            'telefono': '12345678'
        }
        self.cliente = Cliente.objects.create(**self.cliente_data)

    def test_creacion_cliente(self):
        """Test de creación básica de un cliente"""
        self.assertEqual(Cliente.objects.count(), 1)
        cliente = Cliente.objects.first()
        self.assertEqual(cliente.razon_social, self.cliente_data['razon_social'])
        self.assertEqual(cliente.cuit_dni, self.cliente_data['cuit_dni'])

    def test_str_representation(self):
        """Test de la representación en string del modelo"""
        self.assertEqual(str(self.cliente), self.cliente_data['razon_social'])

    def test_get_responsabilidad(self):
        """Test del método get_responsabilidad"""
        self.assertEqual(self.cliente.get_responsabilidad(), 'RESPONSABLE_INSCRIPTO')
        
        # Probamos con otro tipo de responsabilidad
        self.cliente.responsabilidad_iva = 'E'  # Exento
        self.assertEqual(self.cliente.get_responsabilidad(), 'EXENTO')

    def test_get_tipo_documento(self):
        """Test del método get_tipo_documento"""
        self.assertEqual(self.cliente.get_tipo_documento(), 'CUIT')
        
        # Probamos con otro tipo de documento
        self.cliente.tipo_documento = '2'  # DNI
        self.assertEqual(self.cliente.get_tipo_documento(), 'Documento Nacional de Identidad')

    def test_responsabilidad_choices(self):
        """Test de las opciones de responsabilidad"""
        self.assertIn(('I', 'Responsable inscripto'), Cliente.RESPONSABILIDAD_IVA_OPCIONES)
        self.assertIn(('C', 'Consumidor final'), Cliente.RESPONSABILIDAD_IVA_OPCIONES)

    def test_tipo_documento_choices(self):
        """Test de las opciones de tipo de documento"""
        self.assertIn(('C', 'CUIT'), Cliente.TIPO_DOCUMENTO_OPCIONES)
        self.assertIn(('2', 'Documento Nacional de Identidad'), Cliente.TIPO_DOCUMENTO_OPCIONES)
