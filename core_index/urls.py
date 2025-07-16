from django.urls import path
from core_index.views import Vista_Index

app_name = 'core_index'

urlpatterns = [
    path('bienbenida/', Vista_Index.as_view(), name='index'),
]