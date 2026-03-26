from django.contrib import admin
from .models import Cliente, MetodoPago, Transaccion, CierreZ, ArticuloVendido

# Register your models here.
admin.site.register(Cliente)
admin.site.register(MetodoPago)
admin.site.register(CierreZ)


class TransaccionAdmin(admin.ModelAdmin):
    readonly_fields = ("fecha",)


admin.site.register(Transaccion, TransaccionAdmin)


@admin.register(ArticuloVendido)
class ArticuloVendidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "item",
        "is_sin_registro",
        "descripcion_sin_registro",
        "precio_unitario_al_vender",
        "cantidad",
    )
    list_filter = ("is_sin_registro",)
    search_fields = ("descripcion_sin_registro",)
