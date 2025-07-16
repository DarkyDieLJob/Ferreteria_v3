"""
Módulo de vistas para el panel de pruebas.
Exporta las vistas necesarias para el sistema de pruebas.
"""
# Importar vistas desde views.py
from .views import (
    TestingDashboardView,
    TestRunDetailView,
    CoverageReportView
)

__all__ = [
    'TestingDashboardView',
    'InterfaceTestingView',
    'TestRunDetailView',
    'CoverageReportView',  # Corregido: Cambiado de TestCoverageReportView a CoverageReportView
    'TestRunListView',
    'ModuleCoverageDetailView',
    'TestHistoryView',
    'api_test_status',
    'api_coverage_data',
    'get_test_form',
    'run_test_api',
    'discover_testing_interfaces'
]