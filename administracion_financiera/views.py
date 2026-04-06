from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import (
    BoletaForm,
    ServicioForm,
    ImpuestoForm,
    ChequeForm,
    ProveedorFinancieroForm,
    CuentaForm,
    TarjetaCreditoForm,
    ImpuestoTicketForm,
    ServicioTicketForm,
)
from .models import Boleta, TicketDePago, MedioPago, Cuenta, TarjetaCredito, ProveedorFinanciero, Servicio, Impuesto
from bdd.models import Proveedor
from .services import (
    list_pending_for_week,
    liquidate_boleta,
    liquidate_ticket,
    current_iso_week_key,
    current_period,
    vencimiento_in_same_month,
)
import datetime


def staff_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_staff)(view_func)


@staff_required
def dashboard(request):
    week_key = current_iso_week_key()
    boletas_pend, tickets_pend = list_pending_for_week(week_key)
    ctx = {
        "week_key": week_key,
        "display_week": week_key.replace("-W", "-Semana"),
        "boletas_pendientes": len(boletas_pend),
        "tickets_pendientes": len(tickets_pend),
    }
    return render(request, "administracion_financiera/dashboard.html", ctx)


@staff_required
def carga_boleta(request):
    if request.method == "POST":
        form = BoletaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:dashboard"))
    else:
        form = BoletaForm()
    return render(request, "administracion_financiera/carga_boleta.html", {"form": form})


@staff_required
def carga_servicio(request):
    if request.method == "POST":
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:dashboard"))
    else:
        form = ServicioForm()
    return render(request, "administracion_financiera/carga_servicio.html", {"form": form})


@staff_required
def carga_impuesto(request):
    if request.method == "POST":
        form = ImpuestoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:dashboard"))
    else:
        form = ImpuestoForm()
    return render(request, "administracion_financiera/carga_impuesto.html", {"form": form})


@staff_required
def carga_cheque(request):
    if request.method == "POST":
        form = ChequeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:dashboard"))
    else:
        form = ChequeForm()
    return render(request, "administracion_financiera/carga_cheque.html", {"form": form})


@staff_required
def liquidacion(request):
    week_key = request.GET.get("week") or current_iso_week_key()
    message = None
    error = None
    if request.method == "POST":
        kind = request.POST.get("kind")  # 'boleta' o 'ticket'
        obj_id = request.POST.get("id")
        cuenta_id = request.POST.get("cuenta")
        medio = request.POST.get("medio")
        importe = request.POST.get("importe")
        ref = request.POST.get("referencia", "")
        fecha_str = request.POST.get("fecha")
        try:
            fecha = datetime.date.fromisoformat(fecha_str) if fecha_str else datetime.date.today()
            cuenta = Cuenta.objects.get(pk=cuenta_id)
            if kind == "boleta":
                boleta = Boleta.objects.get(pk=obj_id)
                liquidate_boleta(boleta, importe, fecha, medio, cuenta, ref)
                message = "Boleta liquidada correctamente"
            elif kind == "ticket":
                ticket = TicketDePago.objects.get(pk=obj_id)
                liquidate_ticket(ticket, importe, fecha, medio, cuenta, ref)
                message = "Ticket liquidado correctamente"
            else:
                error = "Tipo no reconocido"
        except Exception as e:
            error = str(e)

    boletas, tickets = list_pending_for_week(week_key)
    cuentas = Cuenta.objects.all()
    medios = list(MedioPago.choices)
    ctx = {
        "week_key": week_key,
        "display_week": week_key.replace("-W", "-Semana"),
        "boletas": boletas,
        "tickets": tickets,
        "cuentas": cuentas,
        "medios": medios,
        "message": message,
        "error": error,
    }
    return render(request, "administracion_financiera/liquidacion.html", ctx)


# Proveedores (lista + edición de atributos financieros relevantes)
@staff_required
def proveedores_list(request):
    proveedores = Proveedor.objects.all().select_related("financiero")
    return render(request, "administracion_financiera/proveedores_list.html", {"proveedores": proveedores})


@staff_required
def proveedor_financiero_edit(request, proveedor_id: int):
    proveedor = Proveedor.objects.get(pk=proveedor_id)
    fin, _ = ProveedorFinanciero.objects.get_or_create(proveedor=proveedor)
    if request.method == "POST":
        form = ProveedorFinancieroForm(request.POST, instance=fin)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:proveedores_list"))
    else:
        form = ProveedorFinancieroForm(instance=fin)
    return render(
        request,
        "administracion_financiera/proveedor_financiero_edit.html",
        {"proveedor": proveedor, "form": form},
    )


# Cuentas y Tarjetas (CRUD simple)
@staff_required
def cuentas_list(request):
    cuentas = Cuenta.objects.all()
    return render(request, "administracion_financiera/cuentas_list.html", {"cuentas": cuentas})


@staff_required
def cuenta_edit(request, cuenta_id: int | None = None):
    cuenta = Cuenta.objects.get(pk=cuenta_id) if cuenta_id else None
    if request.method == "POST":
        form = CuentaForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:cuentas_list"))
    else:
        form = CuentaForm(instance=cuenta)
    return render(request, "administracion_financiera/cuenta_edit.html", {"form": form, "cuenta": cuenta})


@staff_required
def tarjetas_list(request):
    tarjetas = TarjetaCredito.objects.select_related("cuenta_liquidacion").all()
    return render(request, "administracion_financiera/tarjetas_list.html", {"tarjetas": tarjetas})


@staff_required
def tarjeta_edit(request, tarjeta_id: int | None = None):
    tarjeta = TarjetaCredito.objects.get(pk=tarjeta_id) if tarjeta_id else None
    if request.method == "POST":
        form = TarjetaCreditoForm(request.POST, instance=tarjeta)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:tarjetas_list"))
    else:
        form = TarjetaCreditoForm(instance=tarjeta)
    return render(request, "administracion_financiera/tarjeta_edit.html", {"form": form, "tarjeta": tarjeta})


# CRUD Servicio
@staff_required
def servicios_list(request):
    servicios = Servicio.objects.all().order_by("nombre")
    return render(request, "administracion_financiera/servicios_list.html", {"servicios": servicios})


@staff_required
def servicio_edit(request, servicio_id: int | None = None):
    servicio = Servicio.objects.get(pk=servicio_id) if servicio_id else None
    if request.method == "POST":
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:servicios_list"))
    else:
        form = ServicioForm(instance=servicio)
    return render(request, "administracion_financiera/servicio_edit.html", {"form": form, "servicio": servicio})


@staff_required
def servicio_delete(request, servicio_id: int):
    if request.method == "POST":
        Servicio.objects.filter(pk=servicio_id).delete()
    return redirect(reverse("administracion_financiera:servicios_list"))


# CRUD Impuesto
@staff_required
def impuestos_list(request):
    impuestos = Impuesto.objects.all().order_by("nombre")
    return render(request, "administracion_financiera/impuestos_list.html", {"impuestos": impuestos})


@staff_required
def impuesto_edit(request, impuesto_id: int | None = None):
    impuesto = Impuesto.objects.get(pk=impuesto_id) if impuesto_id else None
    if request.method == "POST":
        form = ImpuestoForm(request.POST, instance=impuesto)
        if form.is_valid():
            form.save()
            return redirect(reverse("administracion_financiera:impuestos_list"))
    else:
        form = ImpuestoForm(instance=impuesto)
    return render(request, "administracion_financiera/impuesto_edit.html", {"form": form, "impuesto": impuesto})


@staff_required
def impuesto_delete(request, impuesto_id: int):
    if request.method == "POST":
        Impuesto.objects.filter(pk=impuesto_id).delete()
    return redirect(reverse("administracion_financiera:impuestos_list"))


# Acciones rápidas: generar ticket del mes actual
@staff_required
def generar_ticket_servicio_actual(request, servicio_id: int):
    if request.method != "POST":
        return redirect(reverse("administracion_financiera:servicios_list"))
    serv = Servicio.objects.get(pk=servicio_id)
    today = datetime.date.today()
    periodo = current_period(today)
    last = TicketDePago.objects.filter(servicio=serv).order_by("-vencimiento").first()
    vto = vencimiento_in_same_month(last.vencimiento if last else today, today)
    monto = (last.monto if last else (serv.ult_monto or 0)) or 0
    TicketDePago.objects.create(
        servicio=serv,
        periodo=periodo,
        vencimiento=vto or today,
        monto=monto,
        pagado=False,
        semana_iso=current_iso_week_key(vto or today),
    )
    return redirect(reverse("administracion_financiera:servicios_list"))


@staff_required
def generar_ticket_impuesto_actual(request, impuesto_id: int):
    if request.method != "POST":
        return redirect(reverse("administracion_financiera:impuestos_list"))
    imp = Impuesto.objects.get(pk=impuesto_id)
    today = datetime.date.today()
    periodo = current_period(today)
    last = TicketDePago.objects.filter(impuesto=imp).order_by("-vencimiento").first()
    vto = vencimiento_in_same_month(last.vencimiento if last else today, today)
    monto = (last.monto if last else (imp.ult_monto or 0)) or 0
    TicketDePago.objects.create(
        impuesto=imp,
        periodo=periodo,
        vencimiento=vto or today,
        monto=monto,
        pagado=False,
        semana_iso=current_iso_week_key(vto or today),
    )
    return redirect(reverse("administracion_financiera:impuestos_list"))
# Generadores de Tickets por período (separados)
@staff_required
def generar_ticket_impuestos(request):
    if request.method == "POST":
        form = ImpuestoTicketForm(request.POST)
        if form.is_valid():
            imp = form.cleaned_data["impuesto"]
            periodo = form.cleaned_data["periodo"]
            vencimiento = form.cleaned_data["vencimiento"]
            monto = form.cleaned_data["monto"]
            TicketDePago.objects.create(
                impuesto=imp,
                periodo=periodo,
                vencimiento=vencimiento,
                monto=monto,
                pagado=False,
                semana_iso=current_iso_week_key(vencimiento),
            )
            return redirect(reverse("administracion_financiera:dashboard"))
    else:
        form = ImpuestoTicketForm()
    return render(request, "administracion_financiera/generar_ticket_impuestos.html", {"form": form})


@staff_required
def generar_ticket_servicios(request):
    if request.method == "POST":
        form = ServicioTicketForm(request.POST)
        if form.is_valid():
            serv = form.cleaned_data["servicio"]
            periodo = form.cleaned_data["periodo"]
            vencimiento = form.cleaned_data["vencimiento"]
            monto = form.cleaned_data["monto"]
            TicketDePago.objects.create(
                servicio=serv,
                periodo=periodo,
                vencimiento=vencimiento,
                monto=monto,
                pagado=False,
                semana_iso=current_iso_week_key(vencimiento),
            )
            return redirect(reverse("administracion_financiera:dashboard"))
    else:
        form = ServicioTicketForm()
    return render(request, "administracion_financiera/generar_ticket_servicios.html", {"form": form})
