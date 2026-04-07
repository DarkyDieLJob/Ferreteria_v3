from bdd.models import Lista_Pedidos
from .base import GeneralPedidoView
import logging

logger = logging.getLogger(__name__)


class ListarArticulosFaltantesView(GeneralPedidoView):
    template_name = "pedido/listar_faltantes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Código para listar los artículos faltantes
        proveedor_id = self.kwargs.get("proveedor_id")
        context["lista_articulos_faltantes"] = Lista_Pedidos.objects.filter(
            proveedor=proveedor_id
        ).order_by("item")
        logger.debug("Lista de artículos faltantes: %s", list(context["lista_articulos_faltantes"]))
        return context
