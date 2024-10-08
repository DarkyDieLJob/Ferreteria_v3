from django.contrib import admin
from .models import Cliente, MetodoPago, Transaccion, CierreZ

# Register your models here.
admin.site.register(Cliente)
admin.site.register(MetodoPago)
admin.site.register(CierreZ)

class TransaccionAdmin(admin.ModelAdmin):
    readonly_fields = ('fecha',)

admin.site.register(Transaccion, TransaccionAdmin)

