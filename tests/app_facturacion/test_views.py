from django.test import TestCase
from .models import Cliente
from .views import obtener_clientes

class FacturacionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Se ejecuta una vez por clase, antes de todos los tests
        cls.facturacion = facturacion()  # Asumiendo que 'facturacion' es tu fixture principal
        cls.clientes = [
            cls.facturacion.cliente.responsable_inscripto,
            cls.facturacion.cliente.exento,
            cls.facturacion.cliente.consumidor_final,
        ]
        cls.metodos_pago = [
            cls.facturacion.metodos_pago.efectivo_sin_ticket,
            cls.facturacion.metodos_pago.efectivo_con_ticket,
            cls.facturacion.metodos_pago.credito,
            cls.facturacion.metodos_pago.debito,
            cls.facturacion.metodos_pago.mercado_pago,
            cls.facturacion.metodos_pago.cuenta_dni,
            cls.facturacion.metodos_pago.maestro,
        ]

    def test_obtener_todos_los_clientes(self):
        # Utiliza los datos de prueba creados en setUpTestData
        response = self.client.get('/obtener_cliente/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['clientes']), 3)

    def test_transaccion(self):
        data = {}
        for cliente in self.clientes:
            data['cliente_id'] = cliente.id

            for metodo_pago in self.metodos_pago:
                data['metodo_de_pago'] = metodo_pago.id
                if metodo_pago == self.facturacion.metodos_pago.efectivo_sin_ticket:
                    # Crear transacción con método de pago efectivo sin ticket
                    response = self.client.get('procesar_transaccion', data=data)
                    
                    # Esperar que la transacción falle
                    with self.assertRaises(Exception):
                        # Llamada a la función que crea la transacción
                        crear_transaccion(cliente, metodo_pago)
                else:
                    # Crear transacción con otro método de pago
                    # Esperar que la transacción se cree correctamente
                    transaccion = crear_transaccion(cliente, metodo_pago)
                    self.assertIsNotNone(transaccion)
                    # Otras afirmaciones para verificar la transacción





