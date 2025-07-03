"""
Módulo de vistas para el panel de pruebas.
Exporta las vistas necesarias para el sistema de pruebas.
"""
from .views import (
    TestingDashboardView,
    InterfaceTestingView,
    TestRunDetailView,
    TestCoverageReportView,
    get_test_form,
    run_test_api,
    discover_testing_interfaces
)

__all__ = [
    'TestingDashboardView',
    'InterfaceTestingView',
    'TestRunDetailView',
    'TestCoverageReportView',
    'get_test_form',
    'run_test_api',
    'discover_testing_interfaces'
]