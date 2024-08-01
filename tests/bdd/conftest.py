import pytest
from ddf import G
from bdd.models import ListaProveedores, Proveedor, Sub_Carpeta, Sub_Titulo, Tipo_Cartel, Archivo, Sector
from bdd.models import Cajonera, Cajon, Marca, Item, Cod_Barras, Lista_Pedidos, NavBar, Muro, Plantilla
from bdd.models import Contenedor, Modelo_Campos, Formulario_Campos, Formulario_Campos_Contiene
from bdd.modles import Formulario_Campos_Empieza_Con, Armador

class AppBdd:
    def __init__(self):
        self.lista_proveedores = G(ListaProveedores)
        self.proveedores = G(Proveedor)
        self.sub_carpeta = G(Sub_Carpeta)
        self.sub_titulo = G(Sub_Titulo)
        self.tipo_cartel = G(Tipo_Cartel)
        self.archivo = G(Archivo)
        self.sector = G(Sector)
        self.cajonera = G(Cajonera)
        self.cajon = G(Cajon)
        self.marca = G(Marca)
        self.item = G(Item)
        self.cod_barras = G(Cod_Barras)
        self.lista_pedidos = G(Lista_Pedidos)
        self.nav_bar = G(NavBar)
        self.muro = G(Muro)
        self.plantilla = G(Plantilla)
        self.contenedor = G(Contenedor)
        self.modelo_campos = G(Modelo_Campos)
        self.formulario_campos = G(Formulario_Campos)
        self.formulario_campos_contiene = G(Formulario_Campos_Contiene)
        self.formulario_campos_empieza_con = G(Formulario_Campos_Empieza_Con)
        self.armador = G(Armador)

@pytest.fixture
def bdd():
    return AppBdd()
