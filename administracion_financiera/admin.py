from django.contrib import admin

from .models import (
    Cuenta,
    TarjetaCredito,
    Servicio,
    Impuesto,
    Boleta,
    TicketDePago,
    Pago,
    CtaCteProveedor,
    MovimientoCtaCte,
    Cheque,
    DebitoAutomatico,
    ProveedorFinanciero,
)


@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "banco", "activa_desde", "activa_hasta")
    list_filter = ("tipo", "banco")
    search_fields = ("nombre", "banco", "identificador")


@admin.register(TarjetaCredito)
class TarjetaCreditoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ult4", "cierre_dia", "vencimiento_dia", "cuenta_liquidacion")


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "sujeto_pasivo", "periodo", "ult_fecha", "ult_monto")
    filter_horizontal = ("cuentas_permitidas",)


@admin.register(Impuesto)
class ImpuestoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "jurisdiccion", "periodo", "ult_fecha", "ult_monto")
    list_filter = ("tipo",)
    filter_horizontal = ("cuentas_permitidas",)


@admin.register(Boleta)
class BoletaAdmin(admin.ModelAdmin):
    list_display = (
        "proveedor",
        "numero_completo",
        "fecha_emision",
        "fecha_vencimiento",
        "monto",
        "estado",
    )
    list_filter = ("estado", "proveedor")
    search_fields = ("numero", "numero_completo")


@admin.register(TicketDePago)
class TicketDePagoAdmin(admin.ModelAdmin):
    list_display = (
        "servicio",
        "impuesto",
        "periodo",
        "vencimiento",
        "monto",
        "pagado",
        "cuenta_pago",
    )
    list_filter = ("pagado", "servicio__nombre", "impuesto__tipo")


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("importe", "fecha", "medio_pago", "cuenta", "semana_iso")
    list_filter = ("medio_pago", "cuenta")


@admin.register(CtaCteProveedor)
class CtaCteProveedorAdmin(admin.ModelAdmin):
    list_display = ("proveedor",)
    search_fields = ("proveedor__text_display",)


@admin.register(MovimientoCtaCte)
class MovimientoCtaCteAdmin(admin.ModelAdmin):
    list_display = ("ctacte", "fecha", "semana_iso", "tipo", "monto", "saldo_acumulado")
    list_filter = ("tipo",)


@admin.register(Cheque)
class ChequeAdmin(admin.ModelAdmin):
    list_display = (
        "numero",
        "proveedor",
        "cuenta_emisora",
        "monto",
        "estado",
        "fecha_emision",
    )
    list_filter = ("estado", "cuenta_emisora")
    search_fields = ("numero", "banco", "serie", "plaza")


@admin.register(DebitoAutomatico)
class DebitoAutomaticoAdmin(admin.ModelAdmin):
    list_display = ("servicio", "impuesto", "ticket", "cuenta", "tarjeta", "activo")
    list_filter = ("activo",)


@admin.register(ProveedorFinanciero)
class ProveedorFinancieroAdmin(admin.ModelAdmin):
    list_display = ("proveedor", "plazo_unidad", "plazo_valor", "punto_venta")
