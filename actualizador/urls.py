from django.urls import path

from .views import Actualizar

urlpatterns = [
    path('actualizar/', Actualizar.as_view(), name='actualizar'),
]