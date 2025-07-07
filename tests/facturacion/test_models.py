from django.test import TestCase
from facturacion.models import Cliente, ArticuloVendido, MetodoPago, Transaccion, CierreZ
from django.contrib.auth import get_user_model
from bdd.models import Item, ArticuloSinRegistro, Proveedor, Carrito
from decimal import Decimal

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
        choices = dict(Cliente.RESPONSABILIDAD_IVA_OPCIONES)
        self.assertIn(('I', 'Responsable inscripto'), Cliente.RESPONSABILIDAD_IVA_OPCIONES)
        self.assertIn(('C', 'Consumidor final'), Cliente.RESPONSABILIDAD_IVA_OPCIONES)

    def test_tipo_documento_choices(self):
        """Test de las opciones de tipo de documento"""
        choices = dict(Cliente.TIPO_DOCUMENTO_OPCIONES)
        self.assertIn(('C', 'CUIT'), Cliente.TIPO_DOCUMENTO_OPCIONES)
        self.assertIn(('2', 'Documento Nacional de Identidad'), Cliente.TIPO_DOCUMENTO_OPCIONES)


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


class TransaccionModelTest(TestCase):
    def setUp(self):
        # Crear usuario
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            razon_social='Cliente Test',
            cuit_dni='20345678901',
            responsabilidad_iva='I'
        )
        
        # Crear método de pago
        self.metodo_pago = MetodoPago.objects.create(
            display='Tarjeta',
            ticket=True
        )
        
        # Crear transacción
        self.transaccion = Transaccion.objects.create(
            cliente=self.cliente,
            usuario=self.user,
            metodo_de_pago=self.metodo_pago,
            total=1000.00,
            tipo_cbte='FA',
            numero_cbte=1
        )

    def test_creacion_transaccion(self):
        """Test de creación básica de una transacción"""
        self.assertEqual(Transaccion.objects.count(), 1)
        transaccion = Transaccion.objects.first()
        self.assertEqual(transaccion.cliente, self.cliente)
        self.assertEqual(transaccion.usuario, self.user)
        self.assertEqual(transaccion.metodo_de_pago, self.metodo_pago)
        self.assertEqual(float(transaccion.total), 1000.00)

    def test_get_cliente_id(self):
        """Test del método get_cliente_id"""
        self.assertEqual(self.transaccion.get_cliente_id(), self.cliente.id)

    def test_str_representation(self):
        """Test de la representación en string del modelo"""
        self.assertIn(str(self.transaccion.fecha.year), str(self.transaccion))
        self.assertIn('Tarjeta', str(self.transaccion))
        self.assertIn('1000.0', str(self.transaccion))


class CierreZModelTest(TestCase):
    def setUp(self):
        self.cierre_z = CierreZ.objects.create()

    def test_creacion_cierre_z(self):
        """Test de creación básica de un cierre Z"""
        self.assertEqual(CierreZ.objects.count(), 1)
        
    def test_valores_por_defecto(self):
        """Test de los valores por defecto del cierre Z"""
        self.assertEqual(self.cierre_z.zeta_numero, 1)
        self.assertEqual(self.cierre_z.status_fiscal, "0600")
        self.assertEqual(self.cierre_z.status_impresora, "C080")

    def test_str_representation(self):
        """Test de la representación en string del modelo"""
        self.assertIn('FiscalZ', str(self.cierre_z))
