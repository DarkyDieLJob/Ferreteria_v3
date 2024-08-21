import pytest
from pytest import mark
from facturacion.models import Cliente
from facturacion.views import obtener_cliente
import json
from django.test import TestCase
from .conftest import AppFacturacion
from .factories import TransaccionFixture, ClienteFixture
from tests.app_bdd.conftest import AppBdd
from tests.app_bdd.factories import CarritoFixture
from tests.conftest import DefaultModels
from tests.factories import UserFixture

from bdd.models import Articulo, ArticuloSinRegistro


class FacturacionTestCase(TestCase):
    def setUp(self):
        # Limpiar la base de datos
        self.default_models = DefaultModels()
        self.app_Facturacion = AppFacturacion(usuario=self.default_models.user.admin,)
        self.app_bdd = AppBdd()

        self.usuario = self.app_Facturacion.transaccion.efectivo_con_ticket_cliente_exento.usuario

        self.carrito_admin = CarritoFixture(usuario=self.default_models.user.admin).carrito_admin
        self.user_admin = self.app_Facturacion.transaccion.efectivo_con_ticket_cliente_exento.usuario

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


        articulos = Articulo.objects.filter(carrito=self.carrito_admin)
        articulos_sin_registro = ArticuloSinRegistro.objects.filter(carrito=self.carrito_admin)
        articulos_juntos = list(articulos)+list(articulos_sin_registro)

        clientes = ClienteFixture().get_clientes()
        transacciones = TransaccionFixture().get_transacciones()
        for cliente in clientes:
            for transaccion in transacciones:

                data = {
                    'usuario': self.carrito_admin.usuario.username,
                    'carrito_id': self.carrito_admin.id,
                    'cliente_id': cliente.pk,
                    'total': 100.0,
                    'total_efectivo': 90.0,
                    'articulos_vendidos': articulos_juntos,  # Lista vacía
                    'metodo_de_pago': transaccion.metodo_de_pago.id
                }

                response_post = self.client.post(
                    "/procesar_transaccion/",
                    data=data,
                    content_type='application/json',
                )

                print("Response_post: ", response_post)
                self.assertEqual(response_post.status_code, 200)







