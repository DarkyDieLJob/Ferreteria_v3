from django.http import HttpResponse
from django.utils.text import slugify
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet

from pedido.models import ArticuloDevolucion


def _parse_date(param_value):
    if not param_value:
        return None
    try:
        # Formato esperado YYYY-MM-DD
        return timezone.datetime.strptime(param_value, "%Y-%m-%d").date()
    except Exception:
        return None


def _build_filename_global(fecha_desde, fecha_hasta):
    today = timezone.now().date()
    if fecha_desde and fecha_hasta:
        return f"devoluciones_{today}_rango_{fecha_desde}_{fecha_hasta}.pdf"
    return f"devoluciones_{today}.pdf"


def _build_filename_by_proveedor(proveedor_name):
    today = timezone.now().date()
    return f"devoluciones_{slugify(str(proveedor_name))}_{today}.pdf"


def _apply_filters(qs, request, proveedor_id=None):
    fecha_desde = _parse_date(request.GET.get("fecha_desde"))
    fecha_hasta = _parse_date(request.GET.get("fecha_hasta"))
    if fecha_desde and fecha_hasta and fecha_desde <= fecha_hasta:
        qs = qs.filter(fecha__range=(fecha_desde, fecha_hasta))
    if proveedor_id:
        qs = qs.filter(proveedor_id=proveedor_id)
    else:
        pid = request.GET.get("proveedor_id")
        if pid:
            try:
                qs = qs.filter(proveedor_id=int(pid))
            except Exception:
                pass
    q = request.GET.get("q")
    if q:
        qs = qs.filter(
            item__codigo__icontains=q
        ) | qs.filter(
            item__descripcion__icontains=q
        )
    return qs, fecha_desde, fecha_hasta


def _render_table_for_devoluciones(devoluciones):
    # Encabezados
    data = [["Ítem", "Cantidad", "Proveedor", "Fecha"]]
    for dev in devoluciones:
        item_text = str(getattr(dev, "item", ""))
        proveedor_text = str(getattr(dev, "proveedor", ""))
        fecha = getattr(dev, "fecha", "") or ""
        cantidad = getattr(dev, "cantidad", 0)
        data.append([item_text, f"{cantidad:.2f}", proveedor_text, str(fecha)])
    table = Table(data, colWidths=[280, 80, 160, 80])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 1), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lightcyan]),
            ]
        )
    )
    return table


def _render_totales(devoluciones, styles):
    # Totales por proveedor y global
    subtotales = {}
    total_global = 0.0
    for dev in devoluciones:
        prov = str(getattr(dev, "proveedor", ""))
        cant = float(getattr(dev, "cantidad", 0.0) or 0.0)
        subtotales[prov] = subtotales.get(prov, 0.0) + cant
        total_global += cant

    story = []
    if len(subtotales) > 1:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Totales por proveedor:", styles["Heading4"]))
        data = [["Proveedor", "Total"]]
        for prov, tot in sorted(subtotales.items()):
            data.append([prov, f"{tot:.2f}"])
        t = Table(data, colWidths=[360, 100])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("ALIGN", (1, 1), (1, -1), "RIGHT"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]
            )
        )
        story.append(t)

    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Total global: {total_global:.2f}", styles["Heading4"]))
    return story


def descargar_devoluciones_pdf(request):
    if not request.user.is_authenticated:
        # Devuelve 401 sin contenido PDF
        response = HttpResponse(status=401)
        return response

    qs = ArticuloDevolucion.objects.select_related("proveedor", "item").all()
    qs, fecha_desde, fecha_hasta = _apply_filters(qs, request)
    qs = qs.order_by("proveedor__nombre", "fecha", "item__descripcion")

    filename = _build_filename_global(fecha_desde, fecha_hasta)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(
        response, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("Devoluciones", styles["Title"]))
    subtitulo = []
    if fecha_desde and fecha_hasta:
        subtitulo.append(f"Rango: {fecha_desde} a {fecha_hasta}")
    story.append(Paragraph(" ".join(subtitulo) if subtitulo else f"Fecha: {timezone.now().date()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    if qs.exists():
        story.append(_render_table_for_devoluciones(qs))
        story.extend(_render_totales(qs, styles))
    else:
        story.append(Paragraph("No hay devoluciones para los filtros seleccionados.", styles["Normal"]))

    doc.build(story)
    return response


def descargar_devoluciones_por_proveedor_pdf(request, proveedor_id: int):
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    qs = ArticuloDevolucion.objects.select_related("proveedor", "item").all()
    qs, fecha_desde, fecha_hasta = _apply_filters(qs, request, proveedor_id=proveedor_id)
    qs = qs.order_by("fecha", "item__descripcion")

    proveedor_name = qs.first().proveedor if qs.exists() else f"prov_{proveedor_id}"
    filename = _build_filename_by_proveedor(proveedor_name)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    doc = SimpleDocTemplate(
        response, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph(f"Devoluciones - {proveedor_name}", styles["Title"]))
    subtitulo = []
    if fecha_desde and fecha_hasta:
        subtitulo.append(f"Rango: {fecha_desde} a {fecha_hasta}")
    story.append(Paragraph(" ".join(subtitulo) if subtitulo else f"Fecha: {timezone.now().date()}", styles["Normal"]))
    story.append(Spacer(1, 12))

    if qs.exists():
        story.append(_render_table_for_devoluciones(qs))
        # Totales: para un proveedor, mostramos solo global
        total = sum(float(getattr(d, "cantidad", 0.0) or 0.0) for d in qs)
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"Total: {total:.2f}", styles["Heading4"]))
    else:
        story.append(Paragraph("No hay devoluciones para los filtros seleccionados.", styles["Normal"]))

    doc.build(story)
    return response
