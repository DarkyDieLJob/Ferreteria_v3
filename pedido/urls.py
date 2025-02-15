from django.urls import path
from .views import ItemAutocomplete, ListarPedidosView
from .views import EditarPedidoView
from .views import actualizar_llego, actualizar_cantidad
from .views import HomeView, ListarArticulosFaltantesView
from .views import nuevo_pedido, agregar_al_pedido
from .views import enviar_pedido, ControlarPedidoView
from .views import DetallePedidoView, cancelar_articulo_pedido
from .views import agregar_al_stock, agregar_devolucion
from .views import ListarDevolucionesView

app_name = 'pedido'
name = 'pedido'

urlpatterns = [
     #Home vista de inicio
     path('home/',
         HomeView.as_view(),
         name='home'
         ), 
     
     path('nuevo_pedido/<int:proveedor_id>',
         nuevo_pedido,
         name='nuevo-pedido'
         ),
     
     #Buscar articulos
     path('item_autocomplete/',
         ItemAutocomplete.as_view(),
         name='item-autocomplete'
         ),
     
     path('agregar_al_stock/',
         agregar_al_stock,
         name='agregar-al-stock'
         ),
     
     #Listar articulos faltantes
     path('listar_faltantes/<int:proveedor_id>',
         ListarArticulosFaltantesView.as_view(),
         name='listar-faltantes'
         ), 
     
     #Editar pedido por proveedor
     path('editar_pedido_por_proveedor/<int:proveedor_id>',
         EditarPedidoView.as_view(),
         name='editar-pedido-por-proveedor'
         ),
     
     path('editar_pedido/<int:pedido_id>',
         EditarPedidoView.as_view(),
         name='editar-pedido'
         ),
     
     path('actualizar_cantidad/<int:articulo_id>',
         actualizar_cantidad,
         name='actualizar-cantidad'
         ),
     
     path('agregar_al_pedido/',
         agregar_al_pedido,
         name='agregar-al-pedido'
         ),
     
     path('cancelar_articulo_pedido/',
         cancelar_articulo_pedido,
         name='cancelar-articulo-pedido'
         ),
     
     path('enviar_pedido/',
         enviar_pedido,
         name='enviar-pedido'
         ),
     
     #Detalle de pedido por proveedor
     path('detalle_pedido/<int:pedido_id>',
         DetallePedidoView.as_view(),
         name='detalle-pedido'
         ),
     
     #Controlar pedido por proveedor
     path('controlar_pedido/<int:pedido_id>',
         ControlarPedidoView.as_view(),
         name='controlar-pedido'
         ),
     
     path('agregar_devolucion/',
         agregar_devolucion,
         name='agregar-devolucion'
         ),
     
     path('actualizar_llego/<int:articulo_id>',
         actualizar_llego,
         name='actualizar-llego'
         ),
     
     path('marcar_controlado/',
         ControlarPedidoView.as_view(),
         name='marcar-controlado'
         ),
     
     #Listar devoluciones
     path('listar_devoluciones/',
         ListarDevolucionesView.as_view(),
         name='listar-devoluciones'
         ),
     
     path('actualizar_cantidad/<int:articulo_id>',
         actualizar_cantidad,
         name='actualizar-cantidad'
         ),
     
     path('listar_pedidos/',
         ListarPedidosView.as_view(),
         name='listar-pedidos'
         ),
     
     path('eliminar_devolucion/',
         ListarDevolucionesView.as_view(),
         name='eliminar-devolucion'
         ),
     

]