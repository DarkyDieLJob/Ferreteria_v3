"""
URLs para el módulo de dashboard de pruebas.
Define las rutas para acceder al dashboard informativo de pruebas.
"""
from django.urls import path
from .views.views import TestingDashboardView, CoverageReportView

app_name = 'core_testing'

urlpatterns = [
    # Dashboard principal
    path('', TestingDashboardView.as_view(), name='dashboard'),
    
    # Reporte de cobertura
    path('coverage/', CoverageReportView.as_view(), name='coverage_report'),
]
