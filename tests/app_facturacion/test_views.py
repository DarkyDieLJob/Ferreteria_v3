import pytest
from pytest import mark
from facturacion.models import Cliente
from facturacion.views import obtener_cliente
import json
from django.test import TestCase
from .conftest import AppFacturacion
from tests.conftest import DefaultModels
from django.contrib.auth.models import User

class FacturacionTestCase(TestCase):
    def setUp(self):
        # Limpiar la base de datos
        self.app_Facturacion = AppFacturacion()
        self.default_models = DefaultModels()
        self.user_admin = self.default_models.user.admin
        self.assertTrue(User.objects.filter(id=self.user_admin.id).exists())
        self.client.force_login(self.user_admin)

    def test_obtener_todos_los_clientes(self):
        # Utiliza los datos de prueba creados en setUpTestData
        response = self.client.get('/obtener_cliente/')
        self.assertEqual(response.status_code, 200)

    def test_obtener_metodos_pago(self):
        response = self.client.get("/obtener_metodos_pago/")
        self.assertEqual(response.status_code, 200)

    def test_prueba_post(self):
        for metodo_de_pago in self.app_Facturacion.metodo_pago.get_metodos_de_pago():
            data = {
                "dato":metodo_de_pago.display,
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

        for transaccion in AppFacturacion().transaccion.get_transacciones():
            articulos_vendidos = list()
            for articulo_vendido in transaccion.articulos_vendidos.all():
                articulos_vendidos.append(articulo_vendido.get_item())

            data = {
                'usuario': transaccion.usuario.username,
                'carrito_id': self.default_models.carrito.id,
                'cliente_id': transaccion.cliente.pk,
                'total': 100.0,
                'total_efectivo': 90.0,
                'articulos_vendidos': articulos_vendidos,  # Lista vacía
                'metodo_de_pago': 1
            }

            response_post = self.client.post(
                "/procesar_transaccion/",
                data=data,
                content_type='application/json',
            )

            print("Response_post: ", response_post)
            self.assertEqual(response_post.status_code, 200)







