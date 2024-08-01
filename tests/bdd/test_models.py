import pytest

from bdd.models import ListaProveedores, Proveedor, Sub_Carpeta, Sub_Titulo, Tipo_Cartel, Archivo, Sector
from bdd.models import Cajonera, Cajon, Marca, Item, Cod_Barras, Lista_Pedidos, NavBar, Muro, Plantilla
from bdd.models import Contenedor, Modelo_Campos, Formulario_Campos, Formulario_Campos_Contiene
from bdd.modles import Formulario_Campos_Empieza_Con, Armador


@pytest.mark.django_db
def test_lista_proveedores_creation(bdd):
    assert isinstance(bdd.lista_proveedores, ListaProveedores)

@pytest.mark.django_db
def test_proveedores_creation(bdd):
    assert isinstance(bdd.proveedores, Proveedor)

@pytest.mark.django_db
def test_sub_carpeta_creation(bdd):
    assert isinstance(bdd.sub_carpeta, Sub_Carpeta)

@pytest.mark.django_db
def test_sub_titulo_creation(bdd):
    assert isinstance(bdd.sub_titulo, Sub_Titulo)

@pytest.mark.django_db
def test_tipo_cartel_creation(bdd):
    assert isinstance(bdd.tipo_cartel, Tipo_Cartel)

@pytest.mark.django_db
def test_archivo_creation(bdd):
    assert isinstance(bdd.archivo, Archivo)

@pytest.mark.django_db
def test_sector_creation(bdd):
    assert isinstance(bdd.sector, Sector)

@pytest.mark.django_db
def test_cajonera_creation(bdd):
    assert isinstance(bdd.cajonera, Cajonera)

@pytest.mark.django_db
def test_cajon_creation(bdd):
    assert isinstance(bdd.cajon, Cajon)

@pytest.mark.django_db
def test_marca_creation(bdd):
    assert isinstance(bdd.marca, Marca)

@pytest.mark.django_db
def test_item_creation(bdd):
    assert isinstance(bdd.item, Item)

@pytest.mark.django_db
def test_cod_barras_creation(bdd):
    assert isinstance(bdd.cod_barras, Cod_Barras)

@pytest.mark.django_db
def test_item_creation(bdd):
    assert isinstance(bdd.item, Lista_Pedidos)

@pytest.mark.django_db
def test_nav_bar_creation(bdd):
    assert isinstance(bdd.nav_bar, NavBar)

@pytest.mark.django_db
def test_muro_creation(bdd):
    assert isinstance(bdd.muro, Muro)

@pytest.mark.django_db
def test_plantilla_creation(bdd):
    assert isinstance(bdd.plantilla, Plantilla)

@pytest.mark.django_db
def test_contenedor_creation(bdd):
    assert isinstance(bdd.plantilla, Contenedor)

@pytest.mark.django_db
def test_plantilla_creation(bdd):
    assert isinstance(bdd.plantilla, Modelo_Campos)

@pytest.mark.django_db
def test_plantilla_creation(bdd):
    assert isinstance(bdd.plantilla, Formulario_Campos)

@pytest.mark.django_db
def test_plantilla_creation(bdd):
    assert isinstance(bdd.plantilla, Formulario_Campos_Contiene)

@pytest.mark.django_db
def test_plantilla_creation(bdd):
    assert isinstance(bdd.plantilla, Formulario_Campos_Empieza_Con)

@pytest.mark.django_db
def test_plantilla_creation(bdd):
    assert isinstance(bdd.plantilla, Armador)