# Importamos la función path para definir patrones de URL
from django.urls import path
# Importamos la vista WelcomeView que acabamos de crear
from .views import Imprimir, usuarios_caja, consultar_carrito, crear_modificar_lista_pedidos, ItemsView 
from .views import seleccionar_proveedor, cambiar_cantidad_pedido, editar_item, agregar_articulo_a_carrito
from .views import carrito, eliminar_articulo_pedido, ListarCarteles, descargar_archivo


from .models import NavBar, Armador
from django.utils.module_loading import import_string


try:
    # Generamos una lista de objetos path a partir de la información almacenada en el modelo Armador
    armador_paths = []
    #print('1')
    dos = NavBar.objects.all()
    #print('2')
    i = 0
    for nav_bar in NavBar.objects.all():
        try:
            i = i + 1
            #print(i, "-", nav_bar)
            armador = Armador.objects.get(nav_bar=nav_bar)
            vista = import_string(f'bdd.views.{armador.vista}')
            armador_paths.append(path(nav_bar.url_inicial, vista.as_view(), name=nav_bar.text_display))
            #print(armador)
            #print(vista)
            #print(armador_paths)
        except:
            pass
    #print('3')
    print('armador_paths: \n')
    for p in armador_paths:
        print(p)
except Exception as e:
    armador_paths = []
    print("'Error en urls.py; se establecera 'armador_paths = []'")
    print('Error:')
    print(e)
# Definimos nuestros patrones de URL
urlpatterns = [
    # Incluimos los patrones de URL generados dinámicamente
    *armador_paths,
]

# Agregamos los patrones de URL para la vista Imprimir después de agregar los patrones dinámicos
urlpatterns += [
    path('items/<int:cajon_id>', ItemsView.as_view(), name='items'),
    path('seleccionar_proveedor/', seleccionar_proveedor, name='seleccionar_proveedor'),
    path('carrito/', carrito, name='carrito'),
    path('editar_item/<int:id_articulo>/', editar_item, name='editar_item'),
    path('agregar_articulo_a_carrito/<int:id_articulo>/', agregar_articulo_a_carrito, name='agregar_articulo_a_carrito'),
    path('cambiar_cantidad_pedido/<int:id_articulo>/<int:cantidad>/', cambiar_cantidad_pedido, name='cambiar_cantidad_pedido'),
    path('crear_modificar_lista_pedidos/', crear_modificar_lista_pedidos, name='mi_vista_ajax'),
    path('consultar_carrito/', consultar_carrito, name='consultar_carrito'),
    path('usuarios_caja/', usuarios_caja, name='usuarios_caja'),
    path('eliminar_articulo_pedido/', eliminar_articulo_pedido, name='eliminar_articulo_pedido'),
    path('crear_modificar_lista_pedidos/<int:proveedor_id>', crear_modificar_lista_pedidos, name='mi_vista_ajax_get'),
    path('imprimir/',Imprimir.as_view(), name='imprimir'),
    path('imprimir/tabla/',Imprimir.as_view(), name='imprimir tabla'),
    path('imprimir/carteles/1/',Imprimir.as_view(), name='imprimir 1 cartel'),
    path('listar_carteles/',ListarCarteles.as_view(), name='listar_carteles'),
    path('descargar_archivo/', descargar_archivo, name='descargar_archivo'),
]
for url in urlpatterns:
    print(url)
# Incluimos otros patrones de URL estáticos
#urlpatterns += [
#    path('inicio/', MiVista.as_view(), name='inicio'),
#    path('', MiVista.as_view(), name='inicio'),
#]
