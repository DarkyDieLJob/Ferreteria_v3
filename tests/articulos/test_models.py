import pytest
from articulos.models import Articulo, ArticuloProveedor, Cartel
from articulos.models import Categoria, CodigoBarras, Marca, Proveedor
from faker import Faker
from tests.articulos.custom_faker_proiders import CuitProvider

fake = Faker()
fake.add_provider(CuitProvider)



@pytest.mark.django_db
def test_marca_creation(articulos):
    assert isinstance(articulos.marca, Marca)
    
@pytest.mark.django_db
def test_categoria_creation(articulos):
    assert isinstance(articulos.categoria, Categoria)

@pytest.mark.django_db
def test_cartel_creation(articulos):
    assert isinstance(articulos.cartel, Cartel)
    
@pytest.mark.django_db
def test_proveedor_creation(articulos):
    assert isinstance(articulos.proveedor, Proveedor)
    
@pytest.mark.django_db
def test_articulo_creation(articulos):
    assert isinstance(articulos.articulo, Articulo)
    assert isinstance(articulos.articulo.marca, Marca)
    assert isinstance(articulos.articulo.categoria, Categoria)

@pytest.mark.django_db
def test_codigo_barras_creation(articulos):
    assert isinstance(articulos.codigo_barras, CodigoBarras)
    assert isinstance(articulos.codigo_barras.articulo, Articulo)

@pytest.mark.django_db
def test_articulo_proveedor_creation(articulos):
    assert isinstance(articulos.articulo_proveedor, ArticuloProveedor)
    assert isinstance(articulos.articulo, Articulo)
    assert isinstance(articulos.proveedor, Proveedor)
    assert isinstance(articulos.cartel, Cartel)

@pytest.mark.django_db
def test_articulo_proveedor_creation_fail(articulos):
    with pytest.raises(Exception):
        ArticuloProveedor.objects.create(
        articulo=articulos.articulo,
        proveedor=articulos.proveedor,
        codigo_base="CB123",
        descripcion="Descripción del artículo",
        precio_base=100.0,
        actualizado=25,
        codigo_final="CF123",
        precio_final=120.0,
        precio_contado=110.0,
        precio_cantidad=90.0,
        precio_cantidad_contado=80.0,
        cartel=articulos.cartel,
    )