from django.contrib import admin
from .models import Boleta, Comando, OrdenComando

# Register your models here.
admin.site.register(Boleta)
admin.site.register(Comando)
admin.site.register(OrdenComando)