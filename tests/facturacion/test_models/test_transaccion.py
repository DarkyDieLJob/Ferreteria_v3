from django.test import TestCase
from django.contrib.auth import get_user_model
from facturacion.models import Transaccion, Cliente, MetodoPago, ArticuloVendido
from bdd.models import Item, Proveedor
from datetime import datetime, timedelta

class TransaccionModelTest(TestCase):
    def setUp(self):
        # Crear usuario
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            razon_social='Cliente de Prueba',
            cuit_dni='20345678901',
            responsabilidad_iva='C',  # Consumidor Final
            tipo_documento='C',  # CUIT
            domicilio='Calle Falsa 123',
            telefono='12345678'
        )
        
        # Crear método de pago
        self.metodo_pago = MetodoPago.objects.create(
            display='Efectivo',
            ticket=True
        )
        
        # Crear artículos vendidos
        self.proveedor = Proveedor.objects.create(
            cuit='30714065042',
            direccion='Calle Falsa 123',
            text_display='Proveedor de Prueba'
        )
        
        self.item = Item.objects.create(
            codigo='ART001',
            descripcion='Artículo de prueba',
            final=100.50,
            final_efectivo=95.50,
            stock=10,
            proveedor=self.proveedor,
            precio_base=80.00,
            porcentaje=1.25,
            porcentaje_efectivo=1.20
        )
        
        self.articulo_vendido = ArticuloVendido.objects.create(
            item=self.item,
            cantidad=2
        )
        
        # Crear transacción
        self.transaccion = Transaccion.objects.create(
            cliente=self.cliente,
            usuario=self.user,
            metodo_de_pago=self.metodo_pago,
            total=201.00,
            tipo_cbte='TB',
            numero_cbte=1
        )
        self.transaccion.articulos_vendidos.add(self.articulo_vendido)
    
    def test_creacion_transaccion(self):
        """Test de creación básica de una transacción"""
        self.assertEqual(Transaccion.objects.count(), 1)
        transaccion = Transaccion.objects.first()
        self.assertEqual(transaccion.cliente, self.cliente)
        self.assertEqual(transaccion.usuario, self.user)
        self.assertEqual(transaccion.metodo_de_pago, self.metodo_pago)
        self.assertEqual(transaccion.total, 201.00)
        self.assertEqual(transaccion.tipo_cbte, 'TB')
        self.assertEqual(transaccion.numero_cbte, 1)
        self.assertIsNotNone(transaccion.fecha)
        
        # Verificar que la relación many-to-many se haya creado correctamente
        self.assertEqual(transaccion.articulos_vendidos.count(), 1)
        self.assertEqual(transaccion.articulos_vendidos.first(), self.articulo_vendido)
    
    def test_str_representation(self):
        """Test de la representación en string del modelo"""
        expected_str = f"{self.transaccion.fecha}-{self.metodo_pago}-201.0"
        self.assertEqual(str(self.transaccion), expected_str)
    
    def test_get_cliente_id(self):
        """Test del método get_cliente_id"""
        self.assertEqual(self.transaccion.get_cliente_id(), self.cliente.id)
    
    def test_valores_por_defecto(self):
        """Test de los valores por defecto del modelo"""
        transaccion = Transaccion.objects.create(
            cliente=self.cliente,
            usuario=self.user,
            metodo_de_pago=self.metodo_pago
        )
        self.assertEqual(transaccion.total, 0.0)
        self.assertEqual(transaccion.tipo_cbte, '')
        self.assertEqual(transaccion.numero_cbte, 0)
    
    def test_fecha_auto_ahora(self):
        """Test de que la fecha se establece automáticamente al crear"""
        ahora = datetime.now()
        transaccion = Transaccion.objects.create(
            cliente=self.cliente,
            usuario=self.user,
            metodo_de_pago=self.metodo_pago
        )
        # Verificar que la fecha esté dentro de los últimos 10 segundos
        self.assertLessEqual((ahora - transaccion.fecha.replace(tzinfo=None)).total_seconds(), 10)
