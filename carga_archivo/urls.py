from django.urls import path
from .views import upload_file

app_name = 'carga_archivo'

urlpatterns = [
    path('upload_file/', upload_file, name='upload_file'),
]