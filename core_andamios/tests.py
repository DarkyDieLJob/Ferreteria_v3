from django.test import TestCase
from core_andamios.models import Contenedor, Script, Pie, Url, Nav_Bar

class ModeloTest(TestCase):
    def setUp(self):
        self.contenedor = Contenedor.objects.create(nombre='Contenedor 0', text_display='Texto Visible', html='<div></div>')
        self.script = Script.objects.create(nombre='Script 0', text_display='Texto Visible', html='<script></script>')
        self.pie = Pie.objects.create(nombre='Pie 0', text_display='Texto Visible', html='<footer></footer>')
        self.url = Url.objects.create(nombre='Url 0', text_display='Texto Visible', ruta='/ruta/', contenedor=self.contenedor, script=self.script, pie=self.pie)
        self.nav_bar = Nav_Bar.objects.create(nombre='Nav_Bar 0', text_display='Texto Visible', url=self.url)

    def test_modelo_contenedor(self):
        self.assertEqual(self.contenedor.nombre, 'Contenedor 0')

    def test_modelo_script(self):
        self.assertEqual(self.script.nombre, 'Script 0')

    def test_modelo_pie(self):
        self.assertEqual(self.pie.nombre, 'Pie 0')

    def test_modelo_url(self):
        self.assertEqual(self.url.nombre, 'Url 0')

    def test_modelo_nav_bar(self):
        self.assertEqual(self.nav_bar.nombre, 'Nav_Bar 0')
