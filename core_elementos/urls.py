from django.urls import path

from .views import listar_botones

urlpatterns = [
    path('elementos/listar_botones', listar_botones, name='listar-botones'),
]