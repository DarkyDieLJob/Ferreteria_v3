"""
URLs para el módulo de dashboard de pruebas.
Define las rutas para acceder al dashboard informativo de pruebas.
"""
from django.urls import path
from .views.views import (
    TestingDashboardView, 
    CoverageReportView, 
    TestRunDetailView,
    TestRunListView
)

app_name = 'core_testing'

urlpatterns = [
    # Dashboard principal
    path('', TestingDashboardView.as_view(), name='dashboard'),
    
    # Reporte de cobertura
    path('coverage/', CoverageReportView.as_view(), name='coverage_report'),
    
    # Detalle de ejecución de pruebas
    path('test-run/<int:pk>/', TestRunDetailView.as_view(), name='test_run_detail'),
    
    # Lista de ejecuciones de pruebas
    path('test-runs/', TestRunListView.as_view(), name='testrun_list'),
    
]
