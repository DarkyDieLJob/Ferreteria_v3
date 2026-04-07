from .base import GeneralPedidoView
from pedido.models import Pedido
import logging

logger = logging.getLogger(__name__)


class DetallePedidoView(GeneralPedidoView):
    template_name = "pedido/vistas/detalle_pedido/base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Código para listar los pedidos
        pedido_id = self.kwargs.get("pedido_id")
        context["pedido"] = Pedido.objects.get(id=pedido_id)
        context["articulos"] = context["pedido"].articulo_pedido.all()
        logger.info("Render detalle de pedido %s con %s articulos", pedido_id, context["articulos"].count())
        return context

    def get(self, request, pedido_id):
        context = self.get_context_data()
        return self.render_to_response(context)
