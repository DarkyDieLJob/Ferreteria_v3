from django.urls import path
from core_index.views import Vista_Index

urlpatterns = [
    path('bienbenida/', Vista_Index.as_view(), name='index'),
]