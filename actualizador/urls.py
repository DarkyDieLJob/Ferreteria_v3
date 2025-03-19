from django.urls import path

from .views import Actualizar, Reckup

urlpatterns = [
    path('actualizar/', Actualizar.as_view(), name='actualizar'),
    path('reckup/', Reckup.as_view(), name='reckup'),
]