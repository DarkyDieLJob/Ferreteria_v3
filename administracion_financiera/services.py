import datetime
from typing import List, Tuple, Optional
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from .models import (
    Boleta,
    TicketDePago,
    Pago,
    MedioPago,
    Cuenta,
    MovimientoCtaCte,
    CtaCteProveedor,
)


def current_iso_week_key(d: Optional[datetime.date] = None) -> str:
    if d is None:
        d = datetime.date.today()
    iso_year, iso_week, _ = d.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def list_pending_for_week(week_key: Optional[str] = None) -> Tuple[List[Boleta], List[TicketDePago]]:
    if not week_key:
        week_key = current_iso_week_key()
    boletas = Boleta.objects.filter(semana_iso=week_key, estado="pendiente")
    tickets = TicketDePago.objects.filter(semana_iso=week_key, pagado=False)
    return list(boletas), list(tickets)


def _next_period(periodo: Optional[str]) -> Optional[str]:
    if not periodo:
        return None
    try:
        year, month = periodo.split("-")
        y = int(year)
        m = int(month)
        m += 1
        if m > 12:
            m = 1
            y += 1
        return f"{y:04d}-{m:02d}"
    except Exception:
        return None


def current_period(d: Optional[datetime.date] = None) -> str:
    if d is None:
        d = datetime.date.today()
    return f"{d.year:04d}-{d.month:02d}"


def vencimiento_in_same_month(base_date: Optional[datetime.date], target_month_date: Optional[datetime.date] = None) -> Optional[datetime.date]:
    """Given a base_date (e.g., previous vencimiento), return a date in the same month as target_month_date
    keeping the day as close as possible.
    """
    if target_month_date is None:
        target_month_date = datetime.date.today()
    if base_date is None:
        return target_month_date
    y = target_month_date.year
    m = target_month_date.month
    d = base_date.day
    for off in range(0, 5):
        try:
            return datetime.date(y, m, d - off)
        except ValueError:
            continue
    # fallback
    for dd in (28, 27, 26):
        try:
            return datetime.date(y, m, dd)
        except ValueError:
            continue
    return None


def _next_vencimiento_like(date_: Optional[datetime.date]) -> Optional[datetime.date]:
    if not date_:
        return None
    y = date_.year
    m = date_.month + 1
    d = date_.day
    if m > 12:
        m = 1
        y += 1
    # Ajustar día si el mes siguiente no tiene ese día (p.ej. 31)
    for day in range(0, 5):
        try:
            return datetime.date(y, m, d - day)
        except ValueError:
            continue
    # fallback a último día del mes
    for dd in (28, 27, 26):
        try:
            return datetime.date(y, m, dd)
        except ValueError:
            continue
    return None


def _validate_allowed_account_for_ticket(ticket: TicketDePago, cuenta: Cuenta) -> None:
    # Validación dura: si el Ticket proviene de una Carga con reglas, la cuenta debe estar permitida
    carga = ticket.servicio or ticket.impuesto
    if carga is None:
        return
    if carga.cuentas_permitidas.exists() and not carga.cuentas_permitidas.filter(pk=cuenta.pk).exists():
        raise ValueError("La cuenta seleccionada no está permitida para esta carga")


@transaction.atomic
def liquidate_boleta(boleta: Boleta, importe, fecha: datetime.date, medio_pago: str, cuenta: Cuenta, referencia: str = "") -> Pago:
    # Para boleta no hay restricción de cuentas a nivel Carga; se marca pagada y se genera pago y ctacte
    pago = Pago.objects.create(
        content_type=ContentType.objects.get_for_model(Boleta),
        object_id=boleta.pk,
        importe=importe,
        fecha=fecha,
        medio_pago=medio_pago,
        cuenta=cuenta,
        referencia=referencia,
        semana_iso=boleta.semana_iso,
    )
    boleta.estado = "pagada"
    boleta.fecha_pago = fecha
    boleta.save(update_fields=["estado", "fecha_pago"])

    # Movimiento en CtaCte del proveedor (abono por pago realizado)
    ctacte, _ = CtaCteProveedor.objects.get_or_create(proveedor=boleta.proveedor)
    saldo_prev = (
        ctacte.movimientos.order_by("id").last().saldo_acumulado if ctacte.movimientos.exists() else 0
    )
    nuevo_saldo = saldo_prev + float(importe)
    MovimientoCtaCte.objects.create(
        ctacte=ctacte,
        fecha=fecha,
        semana_iso=boleta.semana_iso or current_iso_week_key(fecha),
        content_type=ContentType.objects.get_for_model(Pago),
        object_id=pago.pk,
        tipo=MovimientoCtaCte.Tipo.ABONO,
        monto=importe,
        saldo_acumulado=nuevo_saldo,
    )
    return pago


@transaction.atomic
def liquidate_ticket(ticket: TicketDePago, importe, fecha: datetime.date, medio_pago: str, cuenta: Cuenta, referencia: str = "") -> Pago:
    _validate_allowed_account_for_ticket(ticket, cuenta)
    pago = Pago.objects.create(
        content_type=ContentType.objects.get_for_model(TicketDePago),
        object_id=ticket.pk,
        importe=importe,
        fecha=fecha,
        medio_pago=medio_pago,
        cuenta=cuenta,
        referencia=referencia,
        semana_iso=ticket.semana_iso,
    )
    ticket.pagado = True
    ticket.fecha_pago = fecha
    ticket.cuenta_pago = cuenta
    ticket.metodo_pago = medio_pago
    ticket.save(update_fields=["pagado", "fecha_pago", "cuenta_pago", "metodo_pago"])

    # Auto-generar próximo ticket si corresponde (misma carga, siguiente período)
    carga = ticket.servicio or ticket.impuesto
    if carga and ticket.periodo:
        siguiente_periodo = _next_period(ticket.periodo)
        siguiente_vto = _next_vencimiento_like(ticket.vencimiento)
        if siguiente_periodo and siguiente_vto:
            TicketDePago.objects.create(
                servicio=ticket.servicio if ticket.servicio_id else None,
                impuesto=ticket.impuesto if ticket.impuesto_id else None,
                periodo=siguiente_periodo,
                vencimiento=siguiente_vto,
                monto=ticket.monto,  # por ahora replicamos último monto
                pagado=False,
                semana_iso=current_iso_week_key(siguiente_vto),
            )

    # No hay proveedor directo en ticket; si el pago impacta proveedor, se haría por la Carga o por reglas extra.
    return pago
