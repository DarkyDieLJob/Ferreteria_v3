from django.urls import path
from .views import ListLogs

urlpatterns = [
    path('log/lista-general', ListLogs, name='listar-losgs'),
]