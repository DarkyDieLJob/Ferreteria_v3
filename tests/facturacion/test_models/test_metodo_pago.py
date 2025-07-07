from django.test import TestCase
from facturacion.models import MetodoPago

class MetodoPagoModelTest(TestCase):
    def setUp(self):
        self.metodo_data = {
            'display': 'Efectivo',
            'ticket': True
        }
        self.metodo = MetodoPago.objects.create(**self.metodo_data)

    def test_creacion_metodo_pago(self):
        """Test de creación básica de un método de pago"""
        self.assertEqual(MetodoPago.objects.count(), 1)
        metodo = MetodoPago.objects.first()
        self.assertEqual(metodo.display, self.metodo_data['display'])
        self.assertEqual(metodo.ticket, self.metodo_data['ticket'])

    def test_str_representation(self):
        """Test de la representación en string del modelo"""
        self.assertEqual(str(self.metodo), self.metodo_data['display'])
        
    def test_str_representation_display_vacio(self):
        """Test de la representación en string cuando display está vacío"""
        metodo = MetodoPago.objects.create(display='', ticket=False)
        self.assertEqual(str(metodo), '')
        
    def test_valores_por_defecto(self):
        """Test de los valores por defecto del modelo"""
        metodo = MetodoPago.objects.create(display='Tarjeta')
        self.assertEqual(metodo.ticket, False)  # Valor por defecto de ticket es False
