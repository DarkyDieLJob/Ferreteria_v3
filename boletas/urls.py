from django.urls import path
from .views import BoletasView

urlpatterns = [
    path('boletas_pendientes/', BoletasView.as_view(), name='boletas'), 
]