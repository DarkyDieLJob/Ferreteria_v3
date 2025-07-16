from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from facturacion.models import Cliente, MetodoPago, Transaccion, ArticuloVendido
from bdd.models import Item, ArticuloSinRegistro
from facturacion.classes import TicketCabecera, FormasPago, TicketItem, TicketFactura
from decimal import Decimal

class TicketCabeceraTest(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            razon_social='Cliente de Prueba S.A.',
            cuit_dni='20345678901',
            responsabilidad_iva='I',  # Responsable Inscripto
            tipo_documento='C',  # CUIT
            domicilio='Calle Falsa 123'
        )

    def test_creacion_con_cliente_valido(self):
        """Test de creación con un ID de cliente válido"""
        cabecera = TicketCabecera(cliente_id=self.cliente.id)
        self.assertEqual(cabecera.nombre_cliente, self.cliente.razon_social)
        self.assertEqual(cabecera.tipo_cbte, "FA")  # Factura A para Responsable Inscripto
        self.assertEqual(cabecera.tipo_doc, 'CUIT')
        self.assertEqual(cabecera.nro_doc, '20345678901')
        self.assertEqual(cabecera.domicilio_cliente, 'Calle Falsa 123')
        self.assertEqual(cabecera.tipo_responsable, 'RESPONSABLE_INSCRIPTO')

    def test_creacion_sin_cliente(self):
        """Test de creación sin ID de cliente (debe usar consumidor final)"""
        cabecera = TicketCabecera()
        self.assertEqual(cabecera.nombre_cliente, 'Consumidor Final')
        self.assertEqual(cabecera.tipo_cbte, "FB")  # Factura B por defecto
        self.assertEqual(cabecera.tipo_doc, 'DNI')
        self.assertEqual(cabecera.nro_doc, '0')
        self.assertEqual(cabecera.tipo_responsable, 'CONSUMIDOR_FINAL')

    def test_creacion_con_cliente_inexistente(self):
        """Test de creación con un ID de cliente que no existe"""
        cabecera = TicketCabecera(cliente_id=9999)
        self.assertEqual(cabecera.nombre_cliente, 'Consumidor Final')
        self.assertEqual(cabecera.tipo_cbte, "FB")

    def test_creacion_con_cliente_consumidor_final(self):
        """Test de creación con un cliente que es consumidor final"""
        # Este test ya está cubierto por test_creacion_sin_cliente y test_creacion_con_cliente_inexistente
        pass
        
    def test_creacion_con_cliente_exento(self):
        """Test de creación con un cliente exento de IVA"""
        cliente_exento = Cliente.objects.create(
            razon_social='Cliente Exento S.A.',
            cuit_dni='20345678902',
            responsabilidad_iva='E',  # Exento
            tipo_documento='C',  # CUIT
            domicilio='Calle Falsa 456'
        )
        cabecera = TicketCabecera(cliente_id=cliente_exento.id)
        self.assertEqual(cabecera.tipo_cbte, "FB")  # Factura B para exentos
        self.assertEqual(cabecera.tipo_responsable, 'EXENTO')
        
    def test_creacion_con_id_cliente_invalido(self):
        """Test de creación con un ID de cliente inválido (no numérico)"""
        with self.assertLogs(level='WARNING'):
            cabecera = TicketCabecera(cliente_id='no_es_un_numero')
            self.assertEqual(cabecera.nombre_cliente, 'Consumidor Final')
            self.assertEqual(cabecera.tipo_cbte, "FB")
            
    def test_set_consumidor_final_defaults(self):
        """Test del método _set_consumidor_final_defaults"""
        cabecera = TicketCabecera()
        cabecera._set_consumidor_final_defaults()
        self.assertEqual(cabecera.nombre_cliente, 'Consumidor Final')
        self.assertEqual(cabecera.tipo_cbte, "FB")
        self.assertEqual(cabecera.tipo_doc, 'DNI')
        self.assertEqual(cabecera.nro_doc, '0')
        self.assertEqual(cabecera.domicilio_cliente, ' ')
        self.assertEqual(cabecera.tipo_responsable, 'CONSUMIDOR_FINAL')
        
    def test_get_boleta_a(self):
        """Test del método get_boleta_a"""
        # Caso Factura A
        cabecera = TicketCabecera()
        cabecera.tipo_cbte = "FA"
        self.assertTrue(cabecera.get_boleta_a())
        
        # Caso Factura B
        cabecera.tipo_cbte = "FB"
        self.assertFalse(cabecera.get_boleta_a())
        
        # Caso vacío
        cabecera.tipo_cbte = ""
        self.assertFalse(cabecera.get_boleta_a())
        
    def test_get_cabezera_json(self):
        """Test del método get_cabezera_json"""
        cabecera = TicketCabecera(cliente_id=self.cliente.id)
        json_data = cabecera.get_cabezera_json()
        self.assertIn('cabecera', json_data)
        self.assertEqual(json_data['cabecera']['tipo_cbte'], 'FA')
        self.assertEqual(json_data['cabecera']['nro_doc'], '20345678901')
        self.assertEqual(json_data['cabecera']['nombre_cliente'], 'Cliente de Prueba S.A.')
        self.assertEqual(json_data['cabecera']['tipo_doc'], 'CUIT')
        self.assertEqual(json_data['cabecera']['tipo_responsable'], 'RESPONSABLE_INSCRIPTO')
        
        # Probar con consumidor final
        cabecera_cf = TicketCabecera()  # Sin cliente, debería usar consumidor final
        json_data_cf = cabecera_cf.get_cabezera_json()
        self.assertEqual(json_data_cf['cabecera']['tipo_cbte'], 'FB')
        self.assertEqual(json_data_cf['cabecera']['nombre_cliente'], 'Consumidor Final')
        self.assertEqual(json_data_cf['cabecera']['tipo_responsable'], 'CONSUMIDOR_FINAL')


class FormasPagoTest(TestCase):
    def setUp(self):
        self.metodo_pago = MetodoPago.objects.create(
            display='Efectivo',
            ticket=True
        )
        self.transaccion = Transaccion.objects.create(
            cliente=Cliente.objects.create(
                razon_social='Cliente Test',
                cuit_dni='20345678901'
            ),
            usuario=get_user_model().objects.create_user(
                username='testuser',
                password='testpass123'
            ),
            metodo_de_pago=self.metodo_pago,
            total=1500.50
        )

    def test_creacion_formas_pago(self):
        """Test de creación de FormasPago con transacción válida"""
        formas_pago = FormasPago(self.transaccion)
        self.assertEqual(formas_pago.ds, 'Efectivo')
        self.assertEqual(float(formas_pago.importe), 1500.50)
        
    def test_creacion_con_transaccion_nula(self):
        """Test de creación con transacción nula"""
        with self.assertLogs(level='ERROR') as log:
            formas_pago = FormasPago(None)
            self.assertEqual(formas_pago.ds, 'Error')
            self.assertEqual(formas_pago.importe, 0.0)
            self.assertIn('Error al inicializar FormasPago', log.output[0])
    
    def test_creacion_con_transaccion_invalida(self):
        """Test de creación con transacción que no tiene los atributos esperados"""
        class TransaccionFalsa:
            pass
            
        transaccion_falsa = TransaccionFalsa()
        with self.assertLogs(level='ERROR') as log:
            formas_pago = FormasPago(transaccion_falsa)
            self.assertEqual(formas_pago.ds, 'Error')
            self.assertEqual(formas_pago.importe, 0.0)
            self.assertIn('Error al inicializar FormasPago', log.output[0])

    def test_get_importe(self):
        """Test del método get_importe"""
        # Caso estándar con float
        formas_pago = FormasPago(self.transaccion)
        self.assertEqual(formas_pago.get_importe(), 1500.5)
        
        # Caso con importe como string
        self.transaccion.total = '1234.56'
        formas_pago = FormasPago(self.transaccion)
        self.assertEqual(formas_pago.get_importe(), 1234.56)
        
        # Caso con importe como entero
        self.transaccion.total = 2000
        formas_pago = FormasPago(self.transaccion)
        self.assertEqual(formas_pago.get_importe(), 2000.0)
        
        # Caso con importe como Decimal
        from decimal import Decimal
        self.transaccion.total = Decimal('3000.75')
        formas_pago = FormasPago(self.transaccion)
        self.assertEqual(formas_pago.get_importe(), 3000.75)
        
        # Caso con importe inválido (string no numérico)
        self.transaccion.total = 'no_es_un_numero'
        with self.assertLogs(level='WARNING'):
            formas_pago = FormasPago(self.transaccion)
            self.assertEqual(formas_pago.get_importe(), 0.0)
            
        # Caso con importe None
        self.transaccion.total = None
        with self.assertLogs(level='WARNING'):
            formas_pago = FormasPago(self.transaccion)
            self.assertEqual(formas_pago.get_importe(), 0.0)
            
        # Caso con importe 0
        self.transaccion.total = 0
        formas_pago = FormasPago(self.transaccion)
        self.assertEqual(formas_pago.get_importe(), 0.0)
        
        # Caso con importe negativo
        self.transaccion.total = -100.50
        formas_pago = FormasPago(self.transaccion)
        self.assertEqual(formas_pago.get_importe(), -100.5)

    def test_get_formas_pago_json(self):
        """Test del método get_formas_pago_json"""
        # Caso estándar
        formas_pago = FormasPago(self.transaccion)
        json_data = formas_pago.get_formas_pago_json()
        self.assertEqual(json_data['formasPago'][0]['ds'], 'Efectivo')
        self.assertEqual(json_data['formasPago'][0]['importe'], 1500.5)
        
        # Verificar estructura completa del JSON
        self.assertIn('formasPago', json_data)
        self.assertIsInstance(json_data['formasPago'], list)
        self.assertEqual(len(json_data['formasPago']), 1)
        self.assertIn('ds', json_data['formasPago'][0])
        self.assertIn('importe', json_data['formasPago'][0])
        
        # Caso con división de importe en 2 partes
        json_data = formas_pago.get_formas_pago_json(cant=2)
        self.assertEqual(json_data['formasPago'][0]['importe'], 750.25)
        self.assertEqual(len(json_data['formasPago']), 2)
        self.assertEqual(json_data['formasPago'][1]['importe'], 750.25)
        self.assertEqual(json_data['formasPago'][0]['ds'], 'Efectivo (1/2)')
        self.assertEqual(json_data['formasPago'][1]['ds'], 'Efectivo (2/2)')
        
        # Caso con división en 3 partes (para probar redondeo)
        json_data = formas_pago.get_formas_pago_json(cant=3)
        importe_esperado = round(1500.5 / 3, 2)
        self.assertEqual(json_data['formasPago'][0]['importe'], importe_esperado)
        self.assertEqual(len(json_data['formasPago']), 3)
        
        # Caso con cantidad inválida (debe usar 1 por defecto)
        with self.assertLogs('facturacion.classes', level='WARNING') as cm:
            json_data = formas_pago.get_formas_pago_json(cant=0)
            self.assertEqual(json_data['formasPago'][0]['importe'], 1500.5)
            self.assertEqual(len(json_data['formasPago']), 1)
            self.assertIn('Cantidad inválida (0)', cm.output[0])
            
        # Caso con cantidad negativa (debe usar 1 por defecto)
        with self.assertLogs('facturacion.classes', level='WARNING') as cm:
            json_data = formas_pago.get_formas_pago_json(cant=-1)
            self.assertEqual(json_data['formasPago'][0]['importe'], 1500.5)
            self.assertEqual(len(json_data['formasPago']), 1)
            self.assertIn('Cantidad inválida (-1)', cm.output[0])
            
        # Caso con cantidad como string (debe manejarse correctamente)
        json_data = formas_pago.get_formas_pago_json(cant='2')
        self.assertEqual(len(json_data['formasPago']), 2)
        self.assertEqual(json_data['formasPago'][0]['importe'], 750.25)
        self.assertEqual(json_data['formasPago'][1]['importe'], 750.25)
            
        # Caso con cantidad como string no numérico (debe usar 1 por defecto)
        with self.assertLogs('facturacion.classes', level='WARNING') as cm:
            json_data = formas_pago.get_formas_pago_json(cant='no_es_numero')
            self.assertEqual(len(json_data['formasPago']), 1)
            self.assertEqual(json_data['formasPago'][0]['importe'], 1500.5)
            self.assertIn('Cantidad inválida (no_es_numero)', cm.output[0])

    def test_get_efectivo(self):
        """Test del método get_efectivo"""
        # Caso con método de pago en efectivo (mayúsculas/minúsculas)
        for display in ['efectivo con ticket', 'EFECTIVO CON TICKET', 'Efectivo Con Ticket',
                       'efectivo s/ticket', 'EFECTIVO S/TICKET', 'Efectivo S/Ticket',
                       'Efectivo', 'EFECTIVO', 'efectivo']:
            with self.subTest(display=display):
                metodo_pago = MetodoPago.objects.create(display=display, ticket=True)
                transaccion = Transaccion.objects.create(
                    cliente=self.transaccion.cliente,
                    usuario=self.transaccion.usuario,
                    metodo_de_pago=metodo_pago,
                    total=100.0
                )
                formas_pago = FormasPago(transaccion)
                self.assertTrue(formas_pago.get_efectivo(), f"Debería ser efectivo para: {display}")
        
        # Caso con método de pago que no es efectivo
        for display in ['Tarjeta', 'Transferencia', 'MercadoPago', 'Cheque', 'Deposito', 'Cuenta Corriente']:
            with self.subTest(display=display):
                metodo_pago = MetodoPago.objects.create(display=display, ticket=True)
                transaccion = Transaccion.objects.create(
                    cliente=self.transaccion.cliente,
                    usuario=self.transaccion.usuario,
                    metodo_de_pago=metodo_pago,
                    total=100.0
                )
                formas_pago = FormasPago(transaccion)
                self.assertFalse(formas_pago.get_efectivo(), f"No debería ser efectivo para: {display}")
            
        # Caso con display vacío (cadena vacía)
        with self.subTest(display='empty_string'):
            metodo_pago = MetodoPago.objects.create(display='', ticket=True)
            transaccion = Transaccion.objects.create(
                cliente=self.transaccion.cliente,
                usuario=self.transaccion.usuario,
                metodo_de_pago=metodo_pago,
                total=100.0
            )
            formas_pago = FormasPago(transaccion)
            self.assertFalse(formas_pago.get_efectivo())
        
        # Caso con display que contiene 'efectivo' como parte de otra palabra
        for display in ['NoEfectivo', 'PagoNoEfectivo', 'EfectivoNo']:
            with self.subTest(display=display):
                metodo_pago = MetodoPago.objects.create(display=display, ticket=True)
                transaccion = Transaccion.objects.create(
                    cliente=self.transaccion.cliente,
                    usuario=self.transaccion.usuario,
                    metodo_de_pago=metodo_pago,
                    total=100.0
                )
                formas_pago = FormasPago(transaccion)
                self.assertFalse(formas_pago.get_efectivo(), 
                               f"No debería ser efectivo para: {display} (contiene 'efectivo' como parte de otra palabra)")
        
        # Caso con transacción nula (debería manejarse correctamente)
        with self.subTest(case='transaccion_nula'):
            formas_pago = FormasPago(None)
            self.assertFalse(formas_pago.get_efectivo())
        
        # Caso con método de pago que es efectivo pero con ticket=False
        with self.subTest(case='efectivo_sin_ticket'):
            metodo_efectivo_sin_ticket = MetodoPago.objects.create(
                display='efectivo con ticket',
                ticket=False
            )
            transaccion_efectivo_sin_ticket = Transaccion.objects.create(
                cliente=self.transaccion.cliente,
                usuario=self.transaccion.usuario,
                metodo_de_pago=metodo_efectivo_sin_ticket,
                total=100.0
            )
            formas_pago = FormasPago(transaccion_efectivo_sin_ticket)
            self.assertFalse(formas_pago.get_efectivo(),
                           "No debería ser efectivo si ticket=False aunque el display lo indique")


class TicketItemTest(TestCase):
    def test_creacion_con_datos_minimos(self):
        """Test de creación con datos mínimos"""
        item_data = {
            'ds': 'Producto de prueba',
            'importe': '100.50',
            'qty': 2
        }
        ticket_item = TicketItem(item_data)
        self.assertEqual(ticket_item.ds, 'Producto de prueba')
        self.assertEqual(float(ticket_item.importe), 100.50)
        self.assertEqual(ticket_item.qty, 2)
        self.assertEqual(ticket_item.alic_iva, 21.0)  # Valor por defecto

    def test_creacion_con_todos_los_datos(self):
        """Test de creación con todos los datos posibles"""
        item_data = {
            'ds': 'Producto completo',
            'importe': '200.75',
            'importe_efectivo': '180.50',
            'qty': 3,
            'alic_iva': '10.5',
            'tasaAjusteInternos': '5.0'
        }
        ticket_item = TicketItem(item_data)
        self.assertEqual(ticket_item.ds, 'Producto completo')
        self.assertEqual(float(ticket_item.importe), 200.75)
        self.assertEqual(float(ticket_item.importe_efectivo), 180.50)
        self.assertEqual(ticket_item.qty, 3)
        self.assertEqual(ticket_item.alic_iva, 10.5)
        self.assertEqual(ticket_item.tasaAjusteInternos, 5.0)

    def test_set_div_cant(self):
        """Test del método set_div_cant"""
        item_data = {'ds': 'Test', 'importe': '100', 'qty': 4}
        ticket_item = TicketItem(item_data)
        ticket_item.set_div_cant(2)
        self.assertEqual(ticket_item.qty, 2)

    def test_get_item_json(self):
        """Test del método get_item_json"""
        item_data = {
            'ds': 'Producto JSON',
            'importe': '150.25',
            'importe_efectivo': '140.00',
            'qty': 2
        }
        ticket_item = TicketItem(item_data)
        
        # Test con efectivo=False
        json_data = ticket_item.get_item_json(efectivo=False)
        self.assertEqual(json_data['ds'], 'Producto JSON')
        self.assertEqual(json_data['importe'], 150.25)
        self.assertEqual(json_data['qty'], 2)
        
        # Test con efectivo=True
        json_data = ticket_item.get_item_json(efectivo=True)
        self.assertEqual(json_data['importe'], 140.00)


class TicketFacturaTest(TestCase):
    def setUp(self):
        # Crear datos de prueba
        self.cliente = Cliente.objects.create(
            razon_social='Cliente de Factura',
            cuit_dni='20345678901',
            responsabilidad_iva='I'
        )
        
        self.metodo_pago = MetodoPago.objects.create(
            display='Efectivo',
            ticket=True
        )
        
        self.usuario = get_user_model().objects.create_user(
            username='facturatest',
            password='testpass123'
        )
        
        # Crear transacción con artículos
        self.transaccion = Transaccion.objects.create(
            cliente=self.cliente,
            usuario=self.usuario,
            metodo_de_pago=self.metodo_pago,
            total=2500.00
        )
        
        # Crear artículos vendidos
        self.articulo1 = ArticuloVendido.objects.create(
            item=Item.objects.create(
                codigo='ART001',
                descripcion='Artículo 1',
                final=500.00,
                final_efectivo=450.00
            ),
            cantidad=2
        )
        
        self.articulo2 = ArticuloVendido.objects.create(
            item=Item.objects.create(
                codigo='ART002',
                descripcion='Artículo 2',
                final=750.00,
                final_efectivo=700.00
            ),
            cantidad=2
        )
        
        self.transaccion.articulos_vendidos.add(self.articulo1, self.articulo2)

    def test_creacion_ticket_factura(self):
        """Test de creación básica de TicketFactura"""
        ticket = TicketFactura(self.transaccion)
        self.assertEqual(ticket.cantidad, 1)  # No debería dividirse
        self.assertEqual(len(ticket.items), 2)  # Debería tener 2 artículos
        
        # Verificar que los artículos se cargaron correctamente
        self.assertEqual(ticket.items[0].ds, 'Artículo 1')
        self.assertEqual(ticket.items[1].ds, 'Artículo 2')
        
        # Verificar que la cabecera se creó correctamente
        self.assertEqual(ticket.cabecera.nombre_cliente, 'Cliente de Factura')
        self.assertEqual(ticket.cabecera.tipo_cbte, 'FA')  # Factura A para RI
        
        # Verificar formas de pago
        self.assertEqual(ticket.formas_pago.ds, 'Efectivo')
        self.assertEqual(float(ticket.formas_pago.importe), 2500.00)

    def test_setear_items(self):
        """Test del método setear_items"""
        ticket = TicketFactura(self.transaccion)
        ticket.cantidad = 2  # Forzar división
        ticket.setear_items()
        
        # Verificar que las cantidades se dividieron correctamente
        for item in ticket.items:
            self.assertEqual(item.qty, 1)  # 2 artículos / 2 = 1 cada uno

    def test_get_items_json(self):
        """Test del método get_items_json"""
        ticket = TicketFactura(self.transaccion)
        
        # Probar sin efectivo
        items_json = ticket.get_items_json(efectivo=False, boleta_a=False)
        
        # Verificar que se devuelve un diccionario con una clave 'items' que contiene la lista
        self.assertIsInstance(items_json, dict)
        self.assertIn('items', items_json)
        self.assertIsInstance(items_json['items'], list)
        self.assertEqual(len(items_json['items']), 2)
        
        # Verificar que el primer artículo tiene los campos esperados
        primer_item = items_json['items'][0]
        self.assertIn('ds', primer_item)
        self.assertIn('importe', primer_item)
        self.assertIn('qty', primer_item)
        self.assertIn('alic_iva', primer_item)
        
        # Probar con efectivo
        items_json_efectivo = ticket.get_items_json(efectivo=True, boleta_a=False)
        self.assertIsInstance(items_json_efectivo, dict)
        self.assertIn('items', items_json_efectivo)
        self.assertIsInstance(items_json_efectivo['items'], list)
        self.assertEqual(len(items_json_efectivo['items']), 2)

    def test_get_ticket_json(self):
        """Test del método get_ticket_json"""
        ticket = TicketFactura(self.transaccion)
        tickets_json = ticket.get_ticket_json()
        
        # Verificar que devuelve una lista de tickets
        self.assertIsInstance(tickets_json, list)
        self.assertGreaterEqual(len(tickets_json), 1)
        
        # Verificar que cada ticket tiene la estructura esperada
        for ticket_data in tickets_json:
            self.assertIsInstance(ticket_data, dict)
            self.assertIn('printTicket', ticket_data)
            
            ticket_content = ticket_data['printTicket']
            
            # Verificar estructura básica del ticket
            self.assertIn('cabecera', ticket_content)
            self.assertIn('items', ticket_content)
            self.assertIn('formasPago', ticket_content)
            
            # Verificar que hay al menos un artículo
            self.assertGreaterEqual(len(ticket_content['items']), 1)
            
            # Verificar que se incluye el nombre de la impresora
            self.assertIn('printerName', ticket_data)
