from django.test import TestCase
from .models import Cliente
from .views import obtener_clientes

class FacturacionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Se ejecuta una vez por clase, antes de todos los tests
        cls.facturacion = facturacion()  # Asumiendo que 'facturacion' es tu fixture principal

    def test_obtener_todos_los_clientes(self):
        # Utiliza los datos de prueba creados en setUpTestData
        response = self.client.get('/obtener_cliente/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['clientes']), 3)

    def test_transaccion(self):
        clientes = [
            self.facturacion.cliente.responsable_inscripto,
            self.facturacion.cliente.exento,
            self.facturacion.cliente.consumidor_final,
        ]
        metodos_pago = [
            self.facturacion.metodos_pago.efectivo_sin_ticket,
            self.facturacion.metodos_pago.efectivo_con_ticket,
            # ... otros métodos de pago
        ]

        for cliente in clientes:
            for metodo_pago in metodos_pago:
                if metodo_pago == self.facturacion.metodos_pago.efectivo_sin_ticket:
                    # Crear transacción con método de pago efectivo sin ticket
                    
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





