from django.shortcuts import redirect
from .base import GeneralPedidoView
from bdd.models import Proveedor
from pedido.models import Pedido
import logging

logger = logging.getLogger(__name__)


class HomeView(GeneralPedidoView):
    template_name = "pedido/vistas/home/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedores = Proveedor.objects.all()
        pedidos_activos = {}

        for proveedor in proveedores:
            pedidos_activos[proveedor] = proveedor.pedido_set.exclude(estado="Et")

        context["proveedores"] = proveedores
        context["pedidos_activos"] = pedidos_activos  # Añade el diccionario al contexto
        logger.debug("Pedidos activos: %s", {str(k): list(v.values_list('id', flat=True)) for k, v in pedidos_activos.items()})
        return context


def nuevo_pedido(request, proveedor_id):
    # Código para crear un nuevo pedido
    proveedor = Proveedor.objects.get(id=proveedor_id)
    pedido_pendiente, _ = Pedido.objects.get_or_create(proveedor=proveedor, estado="Pd")

    pedido_pendiente.save()

    return redirect("pedido:editar-pedido", pedido_id=pedido_pendiente.id)
