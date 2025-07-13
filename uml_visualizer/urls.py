from django.urls import path
from . import views

app_name = 'uml_visualizer'

urlpatterns = [
    path('', views.uml_dashboard, name='uml_dashboard'),
    path('diagram/<str:app_label>/', views.generate_diagram, name='generate_diagram'),
    path('project-diagram/', views.project_diagram, name='project_diagram'),
]
