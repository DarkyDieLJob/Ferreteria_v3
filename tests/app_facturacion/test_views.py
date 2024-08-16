import pytest
from pytest import mark
from django.test import TestCase
from facturacion.models import Cliente
from facturacion.views import obtener_cliente
import json


class FacturacionTestCase(TestCase):
    def test_obtener_todos_los_clientes(self):
        # Utiliza los datos de prueba creados en setUpTestData
        response = self.client.get('/obtener_cliente/')
        self.assertEqual(response.status_code, 200)

    def test_obtener_metodos_pago(self):
        response = self.client.get("/obtener_metodos_pago/")
        self.assertEqual(response.status_code, 200)

    def test_prueba_post(self):
        data = {
            "dato":200,
        }
        response_post = self.client.post(
            "/prueba_post/",
            data=data,
            content_type='application/json'
            )
        self.assertEqual(response_post.status_code, 200)

    def test_procesar_transaccion(self):
        response_get = self.client.get("/procesar_transaccion/")
        self.assertEqual(response_get.status_code, 200)
        data = {
            'usuario': 'darkydiel',
            'carrito_id': 1,
            'cliente_id': 1,
            'total': 100.0,
            'total_efectivo': 90.0,
            'articulos_vendidos': [],  # Lista vacía
            'metodo_de_pago': 1
        }

        response = self.client.post(
            "/procesar_transaccion/",
            data=data,
            content_type='application/json',
        )
        self.assertEqual(response_post.status_code, 200)







