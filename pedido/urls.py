from django.urls import path
from .views import ItemAutocomplete, ListarPedidosView
from .views import NuevoStockView, EditarPedidoView
from .views import actualizar_llego, actualizar_cantidad
from .views import HomeView, ListarArticulosFaltantesView
from .views import NuevoPedidoView

name = 'pedido'

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'), 
    
    path('listar_faltantes/<int:proveedor_id>',
         ListarArticulosFaltantesView.as_view(),
         name='listar-faltantes'
         ), 
    path('editar_pedido_por_proveedor/<int:proveedor_id>',
         EditarPedidoView.as_view(),
         name='editar-pedido-por-proveedor'
         ),
    path('nuevo_pedido/<int:proveedor_id>',
         NuevoPedidoView.as_view(),
         name='nuevo-pedido'
         ),
    
    # En el siguiente path, se encuentra un buscador de artículos en tiempo real.
    path('pedir_nuevo_articulo/', NuevoStockView.as_view(), name='NuevoStockView'), 
    
    path('item_autocomplete/', ItemAutocomplete.as_view(), name='item-autocomplete'),
    path('listar_pedidos/', ListarPedidosView.as_view(), name='listar-pedidos'),
    path('editar_pedido/<int:pedido_id>', EditarPedidoView.as_view(), name='editar-pedido'),
    
    path('actualizar_llego/<int:articulo_id>', actualizar_llego, name='actualizar-llego'),
    path('actualizar_cantidad/<int:articulo_id>', actualizar_cantidad, name='actualizar-cantidad'),
    
]