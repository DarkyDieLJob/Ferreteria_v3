from django.urls import path
from .views import ItemAutocomplete, ListarPedidosView, NuevoStockView, EditarPedidoView, actualizar_llego, actualizar_cantidad

urlpatterns = [
    path('nuevo_pedido/', NuevoStockView.as_view(), name='NuevoStockView'), 
    path('item_autocomplete/', ItemAutocomplete.as_view(), name='item-autocomplete'),
    path('listar_pedidos/', ListarPedidosView.as_view(), name='listar-pedidos'),
    path('editar_pedido/<int:pedido_id>', EditarPedidoView.as_view(), name='editar-pedido'),
    path('actualizar_llego/<int:articulo_id>', actualizar_llego, name='actualizar-llego'),
    path('actualizar_cantidad/<int:articulo_id>', actualizar_cantidad, name='actualizar-cantidad'),
]