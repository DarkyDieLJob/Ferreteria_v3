"""core_config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

# Función auxiliar para incluir URLs con namespace de manera segura
def include_with_namespace(namespace, module_path, app_name=None):
    """Incluye URLs con namespace manejando correctamente app_name"""
    if app_name is None:
        app_name = module_path.split('.')[-2] if '.' in module_path else module_path
    return include((module_path, app_name), namespace=namespace)

# URL patterns para la API v3 (sin prefijo para mantener compatibilidad)
urlpatterns_api_v3 = [
    # Incluir las URLs directamente sin prefijo para mantener compatibilidad
    path('', include('carga_archivo.urls')),
    path('', include('facturacion.urls')),
    path('', include('boletas.urls')),
    path('pedidos/', include('pedido.urls')),
    path('', include('x_cartel.urls')),
    path('', include('x_articulos.urls')),
    path('', include('bdd.urls')),
    path('', include('core_docs.urls')),
    path('', include('core_index.urls')),
    path('', include('actualizador.urls')),
]

# Configuración principal de URLs
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API v3 (mantener sin prefijo para compatibilidad)
    # Incluimos directamente las URLs sin prefijo
    *urlpatterns_api_v3,
    
    # API v4 (nueva con DRF) - Solo a partir de v4 usamos prefijo de versión
    path('api/v4/', include_with_namespace('v4', 'core_config.api.v4.urls')),
    
    # URLs de UI (mantener compatibilidad)
    path('uml/', include('uml_visualizer.urls')),
    
    # Redirección por defecto
    path('', RedirectView.as_view(url='/bienvenida/'), name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# URLs de documentación de administración
urlpatterns += [
    path('admin/doc/', include('django.contrib.admindocs.urls')),
]

# URLs de autenticación
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),
]

# URLs para servir archivos estáticos y de medios
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
    re_path(r"^static/(?P<path>.*)$", serve, {
        'document_root': settings.STATIC_ROOT,
    })
]