import json
from django.http import JsonResponse
from django.shortcuts import redirect
from pedido.models import ArticuloPedido, Pedido
from bdd.models import Proveedor, Lista_Pedidos
from pedido.forms import ArticuloPedidoForm
from .base import GeneralPedidoView

class EditarPedidoView(GeneralPedidoView):
    template_name = 'pedido/vistas/editar_pedido/base.html'
    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        # Código para listar los pedidos
        return context
    
    def get(self, request, pedido_id=0, proveedor_id=0):
        context = self.get_context_data()
        # Código para obtener el formulario de edición de pedidos
        if pedido_id != 0:
            context['pedido'] = Pedido.objects.get(id=pedido_id)
            context['proveedor'] = context['pedido'].proveedor
            context['Lista_articulos_pedidos'] = ArticuloPedido.objects.filter(pedido=pedido_id)
        elif proveedor_id != 0:
            context['proveedor'] = Proveedor.objects.get(id=proveedor_id)
            context['pedido'] = Pedido.objects.filter(proveedor=proveedor_id).exclude(estado='Et').first()
            context['Lista_articulos_pedidos'] = ArticuloPedido.objects.filter(proveedor=proveedor_id)
        context['Lista_articulos_faltantes'] = Lista_Pedidos.objects.filter(proveedor=context['proveedor']).order_by('item')
        print("Listado_articulos_pedido:", context['Lista_articulos_pedidos'])
        
        context['form'] = ArticuloPedidoForm()
        return self.render_to_response(context)

    def post(self, request, pedido_id=0, proveedor_id=0):
        form = ArticuloPedidoForm(request.POST)
        pedido = Pedido.objects.get(id=pedido_id)
        
        if form.is_valid():
            print(form.cleaned_data)
            articulo_pedido=ArticuloPedido(
                proveedor=pedido.proveedor,
                item=form.cleaned_data['item'],
                cantidad=form.cleaned_data['cantidad'],
                llego=False
            )
            
            articulo_en_lista_pedido = Lista_Pedidos.objects.get_or_create(
                proveedor=pedido.proveedor, 
                item=form.cleaned_data['item']
                )
            articulo_en_lista_pedido[0].pedido = True
            articulo_en_lista_pedido[0].save()
            
            articulo_pedido.save()
            pedido.articulo_pedido.add(articulo_pedido)
            pedido.save()
            #form.save()
            print("Formulario válido, pedido guardado.")
        else:
            print("Formulario no válido.")
            print(form.errors)
        
        
        context = self.get_context_data()
        
        if pedido_id != 0:
            context['pedido'] = Pedido.objects.get(id=pedido_id)
            context['proveedor'] = context['pedido'].proveedor
            context['Lista_articulos_pedidos'] = ArticuloPedido.objects.filter(pedido=pedido_id)
        elif proveedor_id != 0:
            context['proveedor'] = Proveedor.objects.get(id=proveedor_id)
            context['pedido'] = Pedido.objects.filter(proveedor=proveedor_id).exclude(estado='Et').first()
            context['Lista_articulos_pedidos'] = ArticuloPedido.objects.filter(proveedor=proveedor_id)
        
        context['Lista_articulos_faltantes'] = Lista_Pedidos.objects.filter(proveedor=context['proveedor']).order_by('item')
        print("Listado_articulos_pedido:", context['Lista_articulos_pedidos'])
        
        context['form'] = ArticuloPedidoForm()
        url_destino = request.POST.get('url_destino')
        if url_destino == 'controlar_pedido':
            return redirect('pedido:controlar-pedido', pedido_id=pedido_id)
        else:
            return self.render_to_response(context)
        
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

def agregar_al_pedido(request):
    # Código para agregar un artículo a un pedido
    data = json.loads(request.body)
    print("Agregando al pedido", data)
    articulo_pedido = ArticuloPedido.objects.create(
        proveedor_id=data.get('proveedor_id'),
        item_id=data.get('item_id'),
        cantidad=data.get('cantidad'),
        llego=False
    )
    articulo_pedido.save()
    
    articulo_faltante = Lista_Pedidos.objects.get(proveedor_id=data.get('proveedor_id'), item_id=data.get('item_id'))
    articulo_faltante.pedido = True
    articulo_faltante.cantidad = articulo_faltante.cantidad - float(data.get('cantidad'))
    articulo_faltante.save()
    
    pedido_id = data.get('pedido_id')
    pedido = Pedido.objects.get(id=pedido_id)
    pedido.articulo_pedido.add(articulo_pedido)
    pedido.save()
    return JsonResponse({'status': 'ok'})

def cancelar_articulo_pedido(request):
    # Código para cancelar un artículo de un pedido proceso inverso al de agregar_al_pedido
    data = json.loads(request.body)
    print("Cancelando artículo de pedido", data)
    articulo_pedido = ArticuloPedido.objects.get(id=data.get('articulo_id'))
    
    articulo_faltante,_ = Lista_Pedidos.objects.get_or_create(
        proveedor=articulo_pedido.proveedor, 
        item=articulo_pedido.item
        )
    print("Articulo faltante:", articulo_faltante)
    articulo_faltante.pedido = False
    articulo_faltante.cantidad = articulo_faltante.cantidad + articulo_pedido.cantidad
    articulo_faltante.save()
    
    pedido_id = int(data.get('pedido_id'))
    pedido = Pedido.objects.get(id=pedido_id)
    pedido.articulo_pedido.remove(articulo_pedido)
    pedido.save()
    return JsonResponse({'status': 'ok'})

def enviar_pedido(request):
    # Código para enviar un pedido
    data = json.loads(request.body)
    print("Enviando pedido", data)
    #Si el pedido no tiene articulos no se puede enviar
    if not Pedido.objects.get(id=data.get('pedido_id')).articulo_pedido.all():
        return JsonResponse({'status': 'error', 'message': 'El pedido no tiene artículos'})
    else:
        pedido = Pedido.objects.get(id=data.get('pedido_id'))
        pedido.estado = 'En'
        pedido.save()
    return JsonResponse({'status': 'ok'})