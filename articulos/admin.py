from django.contrib import admin

from articulos.models import Articulo, ArticuloProveedor, Cartel, Categoria, CodigoBarras, Marca, Proveedor

# Register your models here.
admin.site.register(ArticuloProveedor)     
admin.site.register(CodigoBarras)
admin.site.register(Articulo)
admin.site.register(Proveedor)
admin.site.register(Cartel)
admin.site.register(Categoria)
admin.site.register(Marca)