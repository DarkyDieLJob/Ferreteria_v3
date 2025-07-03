"""
URLs para el módulo de testing.
Define las rutas para acceder a las funcionalidades de testing.
"""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views, views_test

app_name = 'core_testing'

urlpatterns = [
    # Dashboard principal de testing
    path('', views.TestingDashboardView.as_view(), name='dashboard'),
    
    # Interfaz de testing específica
    path('interface/<str:interface_name>/', 
         views.InterfaceTestingView.as_view(), 
         name='interface'),
    
    # Obtener formulario para un test específico
    path('api/get-test-form/<str:interface_name>/', 
         views.get_test_form, 
         name='get_test_form'),
    
    # Ejecutar un test (API)
    path('api/run-test/<str:interface_name>/', 
         csrf_exempt(views.run_test_api), 
         name='run_test'),
    
    # Detalles de una ejecución de tests
    path('runs/<int:run_id>/', 
         views.TestRunDetailView.as_view(), 
         name='testrun_detail'),
    
    # Informe de cobertura
    path('coverage/', 
         views.TestCoverageReportView.as_view(), 
         name='coverage_report'),
    
    # Vistas de prueba (temporales)
    path('test/interfaces/', 
         views_test.list_testing_interfaces, 
         name='test_interfaces'),
    path('test/interface/<str:interface_name>/', 
         views_test.TestInterfaceView.as_view(), 
         name='test_interface'),
]
