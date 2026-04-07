from django.urls import path
from .views import (
    dashboard,
    carga_boleta,
    carga_servicio,
    carga_impuesto,
    carga_cheque,
    liquidacion,
    proveedores_list,
    proveedor_financiero_edit,
    cuentas_list,
    cuenta_edit,
    tarjetas_list,
    tarjeta_edit,
    generar_ticket_impuestos,
    generar_ticket_servicios,
    servicios_list,
    servicio_edit,
    servicio_delete,
    impuestos_list,
    impuesto_edit,
    impuesto_delete,
    generar_ticket_servicio_actual,
    generar_ticket_impuesto_actual,
)

app_name = "administracion_financiera"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("carga/boleta/", carga_boleta, name="carga_boleta"),
    path("carga/servicio/", carga_servicio, name="carga_servicio"),
    path("carga/impuesto/", carga_impuesto, name="carga_impuesto"),
    path("carga/cheque/", carga_cheque, name="carga_cheque"),
    path("liquidacion/", liquidacion, name="liquidacion"),
    path("proveedores/", proveedores_list, name="proveedores_list"),
    path("proveedores/<int:proveedor_id>/editar/", proveedor_financiero_edit, name="proveedor_financiero_edit"),
    path("cuentas/", cuentas_list, name="cuentas_list"),
    path("cuentas/nueva/", cuenta_edit, name="cuenta_new"),
    path("cuentas/<int:cuenta_id>/editar/", cuenta_edit, name="cuenta_edit"),
    path("tarjetas/", tarjetas_list, name="tarjetas_list"),
    path("tarjetas/nueva/", tarjeta_edit, name="tarjeta_new"),
    path("tarjetas/<int:tarjeta_id>/editar/", tarjeta_edit, name="tarjeta_edit"),
    path("tickets/generar/impuestos/", generar_ticket_impuestos, name="generar_ticket_impuestos"),
    path("tickets/generar/servicios/", generar_ticket_servicios, name="generar_ticket_servicios"),
    # Servicios
    path("servicios/", servicios_list, name="servicios_list"),
    path("servicios/nuevo/", servicio_edit, name="servicio_new"),
    path("servicios/<int:servicio_id>/editar/", servicio_edit, name="servicio_edit"),
    path("servicios/<int:servicio_id>/eliminar/", servicio_delete, name="servicio_delete"),
    # Impuestos
    path("impuestos/", impuestos_list, name="impuestos_list"),
    path("impuestos/nuevo/", impuesto_edit, name="impuesto_new"),
    path("impuestos/<int:impuesto_id>/editar/", impuesto_edit, name="impuesto_edit"),
    path("impuestos/<int:impuesto_id>/eliminar/", impuesto_delete, name="impuesto_delete"),
    # Quick actions
    path("servicios/<int:servicio_id>/ticket_actual/", generar_ticket_servicio_actual, name="servicio_ticket_actual"),
    path("impuestos/<int:impuesto_id>/ticket_actual/", generar_ticket_impuesto_actual, name="impuesto_ticket_actual"),
]
