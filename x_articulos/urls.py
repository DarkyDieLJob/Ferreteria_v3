from django.urls import path
from x_articulos.views import Crud

urlpatterns = [
    path('articulos/', Crud.as_view(), name='articulos'),
    path('articulos/<int:x_articulo_id>', Crud.as_view(), name='articulos'),
]