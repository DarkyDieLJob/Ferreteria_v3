from django.contrib import admin


from .models import ArticuloPedido, Pedido

# Register your models here.
admin.site.register(ArticuloPedido)
admin.site.register(Pedido)