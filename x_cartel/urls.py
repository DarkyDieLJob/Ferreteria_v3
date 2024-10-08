from django.urls import path
from x_cartel.views import Cartel, Cartelito, CrearCartelitoView, PruebaEdicion, precios_articulos, precios_articulos_cajon

urlpatterns = [
    path('x_cartel/', Cartel.as_view(), name='cartel'),
    #path('x_cartel/imprimir/<int:item_id>', PruebaEdicion.as_view(), name='PruebaEdicion'),
    path('x_cartel/imprimir/<int:item_id>', Cartel.as_view(), name='cartel_x_id'),
    path('x_cartel/imprimir_cajon/<int:cajon_id>', Cartel.as_view(), name='cartel_cajon_x_id'),
    path('x_cartel/cartelito/', CrearCartelitoView.as_view(), name='crear_cartelito'),
    path('precios_articulos/<int:articulo_id>', precios_articulos, name='precios_articulos'),
    path('precios_articulos_cajon/<int:cajon_id>', precios_articulos_cajon, name='precios_articulos_cajon'),
    path('x_cartel/imprimir_cartelitos/', Cartelito.as_view(), name='Cartelito'),
    
]