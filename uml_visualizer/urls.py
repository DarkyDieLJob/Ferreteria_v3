from django.urls import path
from . import views

app_name = 'uml_visualizer'

urlpatterns = [
    # Panel principal
    path('', views.uml_dashboard, name='dashboard'),
    
    # Diagrama del proyecto completo
    path('project/', views.project_diagram, name='project_diagram'),
    
    # Vista de diagrama para una aplicación específica
    path('app/<str:app_label>/', views.app_diagram, name='app_diagram'),
    
    # Descargar diagrama
    path('app/<str:app_label>/download/', views.download_diagram, name='download_diagram'),
    
    # Descargar documentación del proyecto
    path('download-docs/', views.download_docs, name='download_docs'),
]
