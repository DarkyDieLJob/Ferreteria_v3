from django.test import TestCase
from django.contrib.auth import get_user_model
from facturacion.models import ArticuloVendido
from bdd.models import Item, ArticuloSinRegistro, Carrito, Proveedor
from decimal import Decimal

class ArticuloVendidoModelTest(TestCase):
    def setUp(self):
        # Crear un usuario para el carrito
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear un carrito para el usuario
        self.carrito = Carrito.objects.create(usuario=self.user)
        
        # Crear un proveedor para el ítem
        self.proveedor = Proveedor.objects.create(
            cuit='30714065042',
            direccion='Calle Falsa 123',
            text_display='Proveedor de Prueba'
        )
        
        # Crear un ítem registrado con los campos correctos
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
        
        # Crear un artículo sin registrar asociado al carrito
        self.articulo_sin_registrar = ArticuloSinRegistro.objects.create(
            descripcion='Artículo sin registro',
            precio=Decimal('50.25'),
            cantidad=1.0,
            carrito=self.carrito
        )
        
        # Crear artículos vendidos
        self.articulo_vendido_con_item = ArticuloVendido.objects.create(
            item=self.item,
            cantidad=2
        )
        
        self.articulo_vendido_sin_registrar = ArticuloVendido.objects.create(
            sin_registrar=self.articulo_sin_registrar,
            cantidad=1
        )
    
    def test_creacion_articulo_vendido_con_item(self):
        """Test de creación de un artículo vendido con ítem registrado"""
        self.assertEqual(ArticuloVendido.objects.count(), 2)
        articulo = self.articulo_vendido_con_item
        self.assertEqual(articulo.item, self.item)
        self.assertIsNone(articulo.sin_registrar)
        self.assertEqual(articulo.cantidad, 2)
    
    def test_creacion_articulo_vendido_sin_registrar(self):
        """Test de creación de un artículo vendido sin registro"""
        articulo = self.articulo_vendido_sin_registrar
        self.assertIsNone(articulo.item)
        self.assertEqual(articulo.sin_registrar, self.articulo_sin_registrar)
        self.assertEqual(articulo.cantidad, 1)
    
    def test_str_representation_con_item(self):
        """Test de la representación en string con ítem registrado"""
        self.assertEqual(
            str(self.articulo_vendido_con_item), 
            str(self.item)
        )
    
    def test_str_representation_sin_registrar(self):
        """Test de la representación en string con artículo sin registrar"""
        self.assertEqual(
            str(self.articulo_vendido_sin_registrar), 
            str(self.articulo_sin_registrar)
        )
        
    def test_str_representation_sin_item_ni_sin_registrar(self):
        """Test de la representación en string cuando no hay ítem ni artículo sin registrar"""
        articulo = ArticuloVendido.objects.create(cantidad=1)
        self.assertEqual(str(articulo), 'None')
    
    def test_get_item_con_item_registrado(self):
        """Test del método get_item con ítem registrado"""
        resultado = self.articulo_vendido_con_item.get_item()
        self.assertEqual(resultado['ds'], self.item.descripcion)
        self.assertEqual(resultado['importe'], float(round(Decimal('100.50'), 2)))
        self.assertEqual(resultado['importe_efectivo'], float(round(Decimal('95.50'), 2)))
        self.assertEqual(resultado['qty'], 2.0)
    
    def test_get_item_con_articulo_sin_registrar(self):
        """Test del método get_item con artículo sin registrar"""
        resultado = self.articulo_vendido_sin_registrar.get_item()
        self.assertEqual(resultado['ds'], self.articulo_sin_registrar.descripcion)
        self.assertEqual(resultado['importe'], float(round(Decimal('50.25'), 2)))
        self.assertEqual(resultado['importe_efectivo'], float(round(Decimal('50.25'), 2)))
        self.assertEqual(resultado['qty'], 1.0)
        
    def test_get_item_con_item_none(self):
        """Test del método get_item cuando item es None"""
        # Crear un artículo vendido sin item ni sin_registrar
        articulo = ArticuloVendido.objects.create(cantidad=1)
        
        # Verificar que se lance AttributeError al intentar acceder a atributos de None
        with self.assertRaises(AttributeError):
            articulo.get_item()
