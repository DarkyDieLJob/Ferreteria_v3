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
#from pruebas_conexion_api import urls as urls_pruebas_conexion_api
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView


urlpatterns = [
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
    path('', RedirectView.as_view(url='/bienbenida/'), name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += [
    #path('',include(urls_pruebas_conexion_api)),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
]


urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/', include('allauth.urls')),

]


urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {
        'document_root':settings.MEDIA_ROOT,
        }),
    
    re_path(r"^static/(?P<path>.*)$", serve, {
        'document_root':settings.STATIC_ROOT,
        })

]