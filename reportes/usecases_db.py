from datetime import datetime, timedelta, date
from typing import Tuple, Dict, List
from django.db import transaction
from django.db.models import Sum

from facturacion.models import Transaccion, ArticuloVendido
from bdd.models import Item, Proveedor
from .models import WeeklySalesSnapshot


def get_week_bounds_for(dt: date) -> Tuple[date, date]:
    # Semana Lunes a Sábado: inicio = lunes, fin = sábado
    weekday = dt.weekday()  # 0=lunes..6=domingo
    monday = dt - timedelta(days=weekday)
    saturday = monday + timedelta(days=5)
    return monday, saturday


def get_last_completed_week(today: date | None = None) -> Tuple[date, date]:
    today = today or date.today()
    # Semana de trabajo: Lunes(0) a Sábado(5); Domingo(6) no se trabaja.
    # 1) Calcular el sábado de la semana actual (Mon..Sat)
    monday = today - timedelta(days=today.weekday())  # lunes de la semana actual
    current_week_sat = monday + timedelta(days=5)

    # 2) Si hoy es domingo, la semana cerró ayer (sábado actual)
    #    Si hoy es lunes..sábado pero aún no llegó el sábado (hoy < sábado actual),
    #    la última semana cerrada es la anterior (restar 7 días).
    if today.weekday() == 6:  # domingo
        last_sat = current_week_sat
    else:
        last_sat = current_week_sat if today >= current_week_sat else current_week_sat - timedelta(days=7)

    start, end_sat = get_week_bounds_for(last_sat)
    return start, end_sat


@transaction.atomic
def generate_weekly_snapshot(week_start: date, week_end: date) -> int:
    # Eliminar/limpiar existentes para idempotencia y luego bulk_create
    WeeklySalesSnapshot.objects.filter(week_start=week_start, week_end=week_end).delete()

    # Ventas con item registrado (agregado total, sin dividir por vendedor)
    vendidos_qs = ArticuloVendido.objects.filter(
        transaccion__fecha__date__gte=week_start,
        transaccion__fecha__date__lte=week_end,
        item__isnull=False,
    ).values('item', 'item__proveedor').annotate(cantidad=Sum('cantidad'))

    snapshots = []
    for row in vendidos_qs:
        proveedor_id = row['item__proveedor']
        item_id = row['item']
        cantidad = float(row['cantidad'] or 0.0)
        snapshots.append(WeeklySalesSnapshot(
            week_start=week_start,
            week_end=week_end,
            proveedor_id=proveedor_id,
            item_id=item_id,
            vendedor=None,
            vendedor_username=None,
            is_sin_registro=False,
            cantidad_vendida=cantidad,
            total_estimado=0.0,
        ))

    # Ventas sin registro: agregado total, sin dividir por vendedor
    sin_reg_total = ArticuloVendido.objects.filter(
        transaccion__fecha__date__gte=week_start,
        transaccion__fecha__date__lte=week_end,
        item__isnull=True,
    ).aggregate(cantidad=Sum('cantidad'))
    cantidad_sr = float(sin_reg_total.get('cantidad') or 0.0)
    if cantidad_sr > 0:
        snapshots.append(WeeklySalesSnapshot(
            week_start=week_start,
            week_end=week_end,
            proveedor=None,
            item=None,
            vendedor=None,
            vendedor_username=None,
            is_sin_registro=True,
            cantidad_vendida=cantidad_sr,
            total_estimado=0.0,
        ))

    if snapshots:
        WeeklySalesSnapshot.objects.bulk_create(snapshots, batch_size=1000)
    return len(snapshots)


def get_annual_monthly_summary(year: int) -> List[Dict]:
    qs = (
        Transaccion.objects.filter(fecha__year=year)
        .values("fecha__month")
        .annotate(total=Sum("total"), cantidad=Sum(1))
        .order_by("fecha__month")
    )
    # cantidad: usar count
    qs = (
        Transaccion.objects.filter(fecha__year=year)
        .values("fecha__month")
        .annotate(total=Sum("total"), tickets=Sum(1))
        .order_by("fecha__month")
    )
    out = []
    for r in qs:
        month = int(r["fecha__month"]) if r.get("fecha__month") else None
        total = float(r.get("total") or 0.0)
        tickets = int(r.get("tickets") or 0)
        out.append({"month": month, "total": total, "tickets": tickets})
    return out


def get_month_daily_summary(year: int, month: int) -> List[Dict]:
    qs = (
        Transaccion.objects.filter(fecha__year=year, fecha__month=month)
        .values("fecha__date")
        .annotate(total=Sum("total"))
        .order_by("fecha__date")
    )
    out = []
    for r in qs:
        d = r.get("fecha__date")
        total = float(r.get("total") or 0.0)
        out.append({"date": d, "total": total})
    return out


def get_weekly_provider_item_breakdown(week_start: date, week_end: date) -> List[Dict]:
    qs = WeeklySalesSnapshot.objects.filter(week_start=week_start, week_end=week_end)
    data = []
    for s in qs.select_related("proveedor", "item"):
        data.append(
            {
                "proveedor": s.proveedor.text_display if s.proveedor else ("Sin registro" if s.is_sin_registro else "-"),
                "item": str(s.item) if s.item else ("Sin item" if s.is_sin_registro else "-"),
                "item_id": s.item_id,
                "proveedor_id": s.proveedor_id,
                "is_sin_registro": s.is_sin_registro,
                "cantidad": s.cantidad_vendida,
                "total_estimado": s.total_estimado,
            }
        )
    return data


def build_weekly_csv_rows(week_start: date, week_end: date) -> List[List[str]]:
    rows: List[List[str]] = [["Proveedor", "Item", "Cantidad", "Total estimado"]]
    for r in get_weekly_provider_item_breakdown(week_start, week_end):
        rows.append(
            [
                r["proveedor"],
                r["item"],
                f"{r['cantidad']:.2f}",
                f"{r['total_estimado']:.2f}",
            ]
        )
    return rows
