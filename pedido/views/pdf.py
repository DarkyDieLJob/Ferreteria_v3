from django.http import HttpResponse, Http404
from django.utils.text import slugify
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from pedido.models import Pedido


def descargar_pedido_pdf(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
    except Pedido.DoesNotExist:
        raise Http404("Pedido no encontrado")

    proveedor_name = str(pedido.proveedor)
    fecha = pedido.fecha_entrega or pedido.fecha or timezone.now().date()
    filename = f"pedido_{slugify(proveedor_name)}_{fecha}.pdf"

    # Construir datos de la tabla: solo Ítem y Cantidad
    articulos = pedido.articulo_pedido.all().select_related("item")
    data = [["Ítem", "Cantidad"]]
    for art in articulos:
        item_text = str(getattr(art, "item", ""))
        cantidad = getattr(art, "cantidad", "")
        data.append([item_text, f"{cantidad}"])

    # Respuesta HTTP como attachment
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Documento PDF
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph(f"Pedido a {proveedor_name}", styles["Title"]))
    story.append(Paragraph(f"Fecha: {fecha}", styles["Normal"]))
    story.append(Spacer(1, 12))

    table = Table(data, colWidths=[360, 100])
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
            ]
        )
    )
    story.append(table)

    doc.build(story)
    return response
