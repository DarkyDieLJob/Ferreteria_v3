from django.urls import path
from .views import BoletasView

app_name = 'boletas'

urlpatterns = [
    path('boletas_pendientes/', BoletasView.as_view(), name='boletas'), 
]