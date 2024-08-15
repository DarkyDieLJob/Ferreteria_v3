import pytest
from django.test import TestCase
from facturacion.models import Cliente
from facturacion.views import obtener_cliente
from .conftest import facturacion

class SetAtributos:
    def __init__(self, facturacion):
        self.facturacion = facturacion
        self.clientes = [
            self.facturacion.cliente.responsable_inscripto,
            self.facturacion.cliente.exento,
            self.facturacion.cliente.consumidor_final,
        ]
        self.metodos_pago = [
            self.facturacion.metodos_pago.efectivo_sin_ticket,
            self.facturacion.metodos_pago.efectivo_con_ticket,
            self.facturacion.metodos_pago.credito,
            self.facturacion.metodos_pago.debito,
            self.facturacion.metodos_pago.mercado_pago,
            self.facturacion.metodos_pago.cuenta_dni,
            self.facturacion.metodos_pago.maestro,
        ]

@pytest.fixture(scope="class")
def set_atributos(facturacion):
    return SetAtributos(facturacion)

@pytest.mark.parametrize("facturacion", [facturacion])
class FacturacionTestCase(TestCase, SetAtributos):
    def __init__(self, facturacion, *args, **kwargs):
        super().__init__(facturacion, *args, **kwargs)
        
        self.set_atributos = set_atributos(facturacion)

    def test_obtener_todos_los_clientes(self):
        # Utiliza los datos de prueba creados en setUpTestData
        response = self.client.get('/obtener_cliente/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data['clientes']), 3)

    def test_transaccion(self):
        data = {}
        for cliente in self.set_atributos.clientes:
            data['cliente_id'] = cliente.id

            for metodo_pago in self.metodos_pago:
                data['metodo_de_pago'] = metodo_pago.id
                if metodo_pago == self.facturacion.metodos_pago.efectivo_sin_ticket:
                    # Crear transacción con método de pago efectivo sin ticket
                    response = self.client.get('procesar_transaccion', data=data)
                    self.assertIsNotNone(response)

                    # Esperar que la transacción falle
                    with self.assertRaises(Exception):
                        # Llamada a la función que crea la transacción
                        response = self.client.get('procesar_transaccion', data=data)
                        self.assertIsNotNone(response)
                else:
                    # Crear transacción con otro método de pago
                    # Esperar que la transacción se cree correctamente                        
                    response = self.client.get('procesar_transaccion', data=data)
                    self.assertIsNotNone(response)
                    # Otras afirmaciones para verificar la transacción





