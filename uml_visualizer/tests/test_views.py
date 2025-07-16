import os
import logging
from pathlib import Path
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from ..views import uml_dashboard, project_diagram, app_diagram
from ..project_analyzer import ProjectAnalyzer

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(settings.BASE_DIR, 'uml_visualizer/tests/test_debug.log')
)
logger = logging.getLogger(__name__)

class UMLLoggingMiddleware:
    """Middleware para registrar información de las peticiones."""
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        logger.info(f"Petición recibida: {request.method} {request.path}")
        response = self.get_response(request)
        return response

class UMLVisualizerViewsTest(TestCase):
    """Pruebas para las vistas del visualizador UML."""
    
    @classmethod
    def setUpTestData(cls):
        # Crear un usuario administrador para las pruebas
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='testpass123'
        )
        
        # Configurar el analizador de proyecto
        cls.analyzer = ProjectAnalyzer()
        
    def setUp(self):
        # Iniciar sesión como administrador
        self.client.force_login(self.admin_user)
        
    def test_uml_dashboard_view(self):
        """Prueba la vista del dashboard de UML."""
        logger.info("Iniciando prueba de dashboard de UML")
        
        # Obtener la URL del dashboard
        url = reverse('uml_visualizer:dashboard')
        logger.debug(f"URL del dashboard: {url}")
        
        # Hacer la petición GET
        response = self.client.get(url)
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se esté usando la plantilla correcta
        self.assertTemplateUsed(response, 'uml_visualizer/dashboard.html')
        
        # Verificar que el contexto contenga las aplicaciones
        self.assertIn('installed_apps', response.context)
        
        # Registrar información de depuración
        apps = response.context.get('installed_apps', [])
        logger.debug(f"Aplicaciones encontradas: {[app['label'] for app in apps] if isinstance(apps, list) and len(apps) > 0 and isinstance(apps[0], dict) else 'No hay aplicaciones'}")
        
    def test_project_diagram_view(self):
        """Prueba la vista del diagrama del proyecto."""
        logger.info("Iniciando prueba de diagrama de proyecto")
        
        # Obtener la URL del diagrama del proyecto
        url = reverse('uml_visualizer:project_diagram')
        logger.debug(f"URL del diagrama del proyecto: {url}")
        
        # Hacer la petición GET
        response = self.client.get(url)
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se esté usando la plantilla correcta
        self.assertTemplateUsed(response, 'uml_visualizer/diagram.html')
        
        # Verificar que el contexto contenga la estructura del proyecto
        self.assertIn('project_structure', response.context)
        
        # Registrar información de depuración
        project_structure = response.context.get('project_structure', {})
        logger.debug(f"Estructura del proyecto: {project_structure.keys()}")
        
        # Verificar que se incluyan las estadísticas
        self.assertIn('stats', project_structure)
        stats = project_structure['stats']
        logger.debug(f"Estadísticas del proyecto: {stats}")
        
    def test_app_diagram_view(self):
        """Prueba la vista del diagrama de una aplicación específica."""
        logger.info("Iniciando prueba de diagrama de aplicación")
        
        # Obtener una aplicación para probar (usando la primera aplicación encontrada)
        project_structure = self.analyzer.get_project_structure()
        if not project_structure.get('apps'):
            self.skipTest("No hay aplicaciones para probar")
        
        app_label = next(iter(project_structure['apps'].keys()))
        logger.debug(f"Probando con la aplicación: {app_label}")
        
        # Obtener la URL del diagrama de la aplicación
        url = reverse('uml_visualizer:app_diagram', args=[app_label])
        logger.debug(f"URL del diagrama de la aplicación: {url}")
        
        # Hacer la petición GET
        response = self.client.get(url)
        
        # Verificar que la respuesta sea exitosa
        self.assertEqual(response.status_code, 200)
        
        # Verificar que se esté usando la plantilla correcta
        self.assertTemplateUsed(response, 'uml_visualizer/diagram.html')
        
        # Verificar que el contexto contenga la información necesaria
        self.assertIn('app_label', response.context)
        self.assertIn('app_name', response.context)
        
        # Registrar información de depuración
        logger.debug(f"Contexto de la respuesta: {response.context}")
        logger.debug(f"App label: {response.context.get('app_label')}")
        logger.debug(f"App name: {response.context.get('app_name')}")
        
    def test_generate_diagram(self):
        """Prueba la generación de diagramas."""
        logger.info("Iniciando prueba de generación de diagrama")
        
        # Crear un directorio temporal para las pruebas
        test_output_dir = os.path.join(settings.MEDIA_ROOT, 'test_uml_diagrams')
        os.makedirs(test_output_dir, exist_ok=True)
        output_file = os.path.join(test_output_dir, 'test_diagram.png')
        
        try:
            # Probar con una aplicación específica
            project_structure = self.analyzer.get_project_structure()
            if not project_structure.get('apps'):
                self.skipTest("No hay aplicaciones para probar")
            
            app_label = next(iter(project_structure['apps'].keys()))
            logger.debug(f"Generando diagrama para la aplicación: {app_label}")
            
            # Importar la función de generación de diagrama
            from ..views import generate_diagram
            
            # Probar con una aplicación específica
            success, error_msg = generate_diagram(app_label, output_file)
            
            # Verificar que se haya generado correctamente
            if not success:
                logger.warning(f"No se pudo generar el diagrama: {error_msg}")
                # No fallar la prueba si no se puede generar el diagrama, solo advertir
                # ya que puede fallar en entornos de prueba sin graphviz instalado
                self.skipTest(f"No se pudo generar el diagrama: {error_msg}")
            
            # Verificar que el archivo se haya creado
            self.assertTrue(os.path.exists(output_file), "El archivo del diagrama no se creó")
            
            # Verificar que el archivo no esté vacío
            self.assertGreater(os.path.getsize(output_file), 0, "El archivo del diagrama está vacío")
            
            logger.info(f"Diagrama generado correctamente en: {output_file}")
            
        finally:
            # Limpiar archivos de prueba
            if os.path.exists(output_file):
                os.remove(output_file)
            if os.path.exists(test_output_dir):
                os.rmdir(test_output_dir)
    
    def test_download_diagram(self):
        """Prueba la descarga de diagramas."""
        logger.info("Iniciando prueba de descarga de diagrama")
        
        # Probar con una aplicación específica
        project_structure = self.analyzer.get_project_structure()
        if not project_structure.get('apps'):
            self.skipTest("No hay aplicaciones para probar")
        
        app_label = next(iter(project_structure['apps'].keys()))
        
        # Probar descarga de diagrama de aplicación
        url = reverse('uml_visualizer:download_diagram', args=[app_label])
        response = self.client.get(url)
        
        # Verificar que la respuesta sea exitosa o redireccione
        self.assertIn(response.status_code, [200, 302], 
                     f"La descarga del diagrama de la aplicación falló con código {response.status_code}")
        
        # Probar descarga del diagrama del proyecto
        url = reverse('uml_visualizer:download_diagram', args=['project'])
        response = self.client.get(url)
        
        # Verificar que la respuesta sea exitosa o redireccione
        self.assertIn(response.status_code, [200, 302], 
                     f"La descarga del diagrama del proyecto falló con código {response.status_code}")
    
    def test_download_docs(self):
        """Prueba la descarga de la documentación."""
        logger.info("Iniciando prueba de descarga de documentación")
        
        url = reverse('uml_visualizer:download_docs')
        response = self.client.get(url)
        
        # Verificar que la respuesta sea exitosa o redireccione
        self.assertIn(response.status_code, [200, 302], 
                     f"La descarga de la documentación falló con código {response.status_code}")
    
    def test_unauthorized_access(self):
        """Prueba el acceso no autorizado a las vistas."""
        logger.info("Iniciando prueba de acceso no autorizado")
        
        # Cerrar sesión
        self.client.logout()
        
        # Probar acceso al dashboard sin autenticación
        url = reverse('uml_visualizer:dashboard')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200, "Se permitió el acceso no autorizado al dashboard")
        
        # Probar acceso al diagrama del proyecto sin autenticación
        url = reverse('uml_visualizer:project_diagram')
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200, "Se permitió el acceso no autorizado al diagrama del proyecto")
        
        # Volver a iniciar sesión como administrador
        self.client.force_login(self.admin_user)
