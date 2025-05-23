from .base import GeneralPedidoView
import json
from django.http import JsonResponse
from pedido.models import ArticuloPedido, ArticuloDevolucion
from bdd.models import Lista_Pedidos

class ListarDevolucionesView(GeneralPedidoView):
    template_name = 'pedido/vistas/devoluciones/base.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Código para listar las devoluciones
        context['devoluciones'] = ArticuloDevolucion.objects.all()
        return context
    
    def post(self, request):
        devolucion = ArticuloDevolucion.objects.get(id=request.POST.get('devolucion_id'))
        devolucion.delete()
        return JsonResponse({'status': 'ok'})
    
def actualizar_cantidad(request, articulo_id):
    # Código para actualizar la cantidad de un pedido
    print("Actualizando cantidad de articulo", articulo_id)
    articulo_pedido = ArticuloPedido.objects.get(id=articulo_id)
    data = json.loads(request.body)
    
    cantidad = float(data.get('cantidad'))
    
    if articulo_pedido.cantidad > cantidad:
        articulo_faltante,_ = Lista_Pedidos.objects.get_or_create(
            proveedor=articulo_pedido.proveedor, 
            item=articulo_pedido.item
            )
        articulo_faltante.cantidad = articulo_faltante.cantidad - (cantidad - articulo_pedido.cantidad)
        articulo_faltante.save()
        
    elif articulo_pedido.cantidad < cantidad:
        articulo_faltante,_ = Lista_Pedidos.objects.get_or_create(
            proveedor=articulo_pedido.proveedor, 
            item=articulo_pedido.item
            )
        articulo_faltante.cantidad = articulo_faltante.cantidad + (articulo_pedido.cantidad - cantidad)
        articulo_faltante.save()
    articulo_pedido.cantidad = cantidad
    articulo_pedido.save()
    return JsonResponse({'status': 'ok'})

