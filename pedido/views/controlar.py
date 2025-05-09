from .base import GeneralPedidoView
import json
from django.http import JsonResponse
from pedido.models import ArticuloPedido, Pedido, ArticuloDevolucion
from bdd.models import Lista_Pedidos
from pedido.forms import ArticuloPedidoForm

class ControlarPedidoView(GeneralPedidoView):
    template_name = 'pedido/vistas/controlar_pedido/base.html'
    
    def get_context_data(self, pedido_id, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pedido'] = Pedido.objects.get(id=pedido_id)
        context['proveedor'] = context['pedido'].proveedor
        context['Lista_articulos_pedidos'] = ArticuloPedido.objects.filter(pedido=pedido_id)
        context['form'] = ArticuloPedidoForm()
        return context
    
    def get(self, request, pedido_id):
        # Código para controlar un pedido
        context = self.get_context_data(pedido_id=pedido_id)

        return self.render_to_response(context)
    
    def post(self, request):
        data = json.loads(request.body)
        pedido_id = data.get('pedido_id')
        context = self.get_context_data(pedido_id=pedido_id)
        print("Controlando pedido", data)
        pedido_controlado = Pedido.objects.get(id=pedido_id)
        pedido_controlado.estado = 'Co'
        context['lista_articulo_que_no_llegaron'] = ArticuloPedido.objects.filter(pedido=pedido_id, llego=False)
        pedido, _ = Pedido.objects.get_or_create(proveedor=pedido_controlado.proveedor, estado='Pd')
        pedido.articulo_pedido.add(*context['lista_articulo_que_no_llegaron'])
        
        pedido.save()
        pedido_controlado.save()
        return JsonResponse({'status': 'ok'})
    
def agregar_devolucion(request):
    # Código para agregar un artículo a una devolución
    data = json.loads(request.body)
    print("Agregando devolución", data)
    #se desvincula el articulo del pedido y se vincula a la lista de devolucion
    articulo_pedido = ArticuloPedido.objects.get(id=data.get('articulo_id'))

    pedido = Pedido.objects.get(id=data.get('pedido_id'))
    pedido.articulo_pedido.remove(articulo_pedido)
    
    articulo = Lista_Pedidos.objects.get(proveedor=articulo_pedido.proveedor, item=articulo_pedido.item)
    articulo.pedido = False
    
    devolucion = ArticuloDevolucion.objects.create(
        proveedor=articulo_pedido.proveedor,
        item=articulo_pedido.item,
        cantidad=articulo_pedido.cantidad
    )
    
    articulo_pedido.cantidad = 0   
     
    pedido.save()
    devolucion.save()
    articulo_pedido.save()
    articulo.save()
    return JsonResponse({'status': 'ok'})

def actualizar_llego(request, articulo_id):
    # Código para actualizar el campo llego de un pedido
    print("Actualizando llego de articulo", articulo_id)
    articulo_pedido = ArticuloPedido.objects.get(id=articulo_id)
    data = json.loads(request.body)
    articulo_pedido.llego = data.get('llego')
    # Process the data as needed
    
    
    articulo_faltante, _ = Lista_Pedidos.objects.get_or_create(proveedor_id=articulo_pedido.proveedor.id, item_id=articulo_pedido.item.id)
    articulo_faltante.pedido = False
    articulo_faltante.cantidad = articulo_faltante.cantidad - float(1)
    articulo_faltante.save()
    
    articulo_pedido.save()
    return JsonResponse({'status': 'ok'})

