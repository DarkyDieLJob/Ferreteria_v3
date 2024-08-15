import pytest
from pytest import mark
from django.test import TestCase
from facturacion.models import Cliente
from facturacion.views import obtener_cliente


class FacturacionTestCase(TestCase):
    def test_obtener_todos_los_clientes(self):
        # Utiliza los datos de prueba creados en setUpTestData
        response = self.client.get('/obtener_cliente/')
        self.assertEqual(response.status_code, 200)







