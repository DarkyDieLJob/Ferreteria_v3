"""
URLs para el módulo de testing.
Define las rutas para acceder a las funcionalidades de testing.
"""
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views
from .views.views_test import list_testing_interfaces, TestInterfaceView
from .testing_interfaces.views.example import ExampleInterfaceView
from .testing_interfaces.views.example_interface import ExampleInterfaceTestingView

app_name = 'core_testing'

# URLs para interfaces de testing específicas
urlpatterns = [
    # Dashboard principal de testing
    path('', views.TestingDashboardView.as_view(), name='dashboard'),
    
    # URLs de interfaces específicas - Usando las vistas directamente
    path('interface/example/', 
         ExampleInterfaceView.as_view(), 
         name='example_interface'),
         
    path('interface/example_interface/', 
         ExampleInterfaceTestingView.as_view(), 
         name='example_advanced_interface'),
    
    # Interfaz de testing genérica (para compatibilidad)
    path('interface/<str:interface_name>/', 
         views.InterfaceTestingView.as_view(), 
         name='interface'),
    
    # API endpoints
    path('api/get-test-form/<str:interface_name>/', 
         views.get_test_form, 
         name='get_test_form'),
    
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
    
    # Rutas de prueba
    path('test/interfaces/', 
         list_testing_interfaces, 
         name='test_interfaces'),
    path('test/interface/<str:interface_name>/', 
         TestInterfaceView.as_view(), 
         name='test_interface'),
]
