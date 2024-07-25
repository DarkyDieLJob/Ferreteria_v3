from django.urls import path
from .views import ItemAutocomplete, ListarPedidosView, NuevoStockView

urlpatterns = [
    path('nuevo_pedido/', NuevoStockView.as_view(), name='NuevoStockView'), 
    path('item_autocomplete/', ItemAutocomplete.as_view(), name='item-autocomplete'),
    path('listar_pedidos/', ListarPedidosView.as_view(), name='listar-pedidos'),
]