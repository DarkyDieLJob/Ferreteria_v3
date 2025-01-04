import pytest

from bdd.models import ListaProveedores, Proveedor, Sub_Carpeta, Sub_Titulo, Tipo_Cartel, Archivo, Sector
from bdd.models import Cajonera, Cajon, Marca, Item, Cod_Barras, Lista_Pedidos, NavBar, Muro, Plantilla
from bdd.models import Contenedor, Modelo_Campos, Formulario_Campos, Formulario_Campos_Contiene
from bdd.models import Formulario_Campos_Empieza_Con, Armador, Tipo_Registro, Registros, Compras
from bdd.models import Listado_Planillas, Carrito, Articulo, ArticuloSinRegistro


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
    assert isinstance(bdd.lista_pedidos, Lista_Pedidos)

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
    assert isinstance(bdd.contenedor, Contenedor)

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
    assert isinstance(bdd.armador, Armador)

@pytest.mark.django_db
def test_tipo_registro_creation(bdd):
    assert isinstance(bdd.tipo_registro, Tipo_Registro)

@pytest.mark.django_db
def test_Registros_creation(bdd):
    assert isinstance(bdd.registros, Registros)

@pytest.mark.django_db
def test_compras_creation(bdd):
    assert isinstance(bdd.compras, Compras)

@pytest.mark.django_db
def test_listado_planillas_creation(bdd):
    assert isinstance(bdd.listado_planillas, Listado_Planillas) 

@pytest.mark.django_db
def test_carrito_creation(bdd):
    assert isinstance(bdd.carrito.carrito_admin , Carrito)

@pytest.mark.django_db
def test_articulo_creation(bdd):
    assert isinstance(bdd.articulo.articulo_asci_carrito_admin, Articulo)
    assert isinstance(bdd.articulo.articulo_no_asci_carrito_admin, Articulo)

@pytest.mark.django_db
def test_articulo_sin_registro_creation(bdd):
    assert isinstance(bdd.articulo_sin_registro.articulo_sr_asci_carrito_admin, ArticuloSinRegistro)
    assert isinstance(bdd.articulo_sin_registro.articulo_sr_no_asci_carrito_admin, ArticuloSinRegistro)