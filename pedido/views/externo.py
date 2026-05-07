from django.http import JsonResponse
from pedido.models import ArticuloPedido, Pedido
from bdd.models import Lista_Pedidos, Item
import logging

logger = logging.getLogger(__name__)


def agregar_al_pedido(request, articulo_id):
    try:
        item = Item.objects.get(id=articulo_id)
    except Item.DoesNotExist:
        return JsonResponse(
            {"error": "item_not_found", "message": "Artículo no encontrado"},
            status=404,
        )
    if getattr(item, "proveedor", None) is None:
        logger.warning("Item %s no tiene proveedor asociado", articulo_id)
        return JsonResponse(
            {
                "error": "missing_proveedor",
                "message": "El artículo no tiene proveedor asociado",
            },
            status=400,
        )
    proveedor_id = item.proveedor.id
    articulo_pedido = ArticuloPedido.objects.create(
        proveedor_id=proveedor_id, item_id=articulo_id, cantidad=1, llego=False
    )
    articulo_pedido.save()

    articulo_faltante, _ = Lista_Pedidos.objects.get_or_create(
        proveedor_id=proveedor_id, item_id=articulo_id
    )
    articulo_faltante.pedido = True
    articulo_faltante.cantidad = articulo_faltante.cantidad - float(1)
    articulo_faltante.save()

    pedido, _ = Pedido.objects.get_or_create(proveedor_id=proveedor_id, estado="Pd")
    pedido.articulo_pedido.add(articulo_pedido)
    pedido.save()
    return JsonResponse({"status": "ok"})
