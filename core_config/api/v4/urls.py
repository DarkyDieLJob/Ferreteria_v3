"""
URLs para la API v4
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de la documentación de la API
schema_view = get_schema_view(
   openapi.Info(
      title="Ferretería Paoli API",
      default_version='v4',
      description="API para el sistema de gestión de Ferretería Paoli",
      terms_of_service="https:/terms/",
      contact=openapi.Contact(email="contacto@ferreteriapaoli.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

# Router principal
router = DefaultRouter()

# Aquí se registrarán las rutas de las aplicaciones
# Ejemplo:
# router.register(r'articulos', ArticuloViewSet, basename='articulo')

urlpatterns = [
    # Documentación
    path('docs/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Rutas de la API
    path('', include(router.urls)),
    
    # Incluir aquí otras rutas de la API
    # path('', include('mi_app.api.v4.urls')),
]
