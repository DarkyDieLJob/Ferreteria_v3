import json
from typing import Any
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView
from .models import ArticuloPedido, Pedido, Devolucion
from bdd.models import Proveedor, Lista_Pedidos
from .forms import ArticuloPedidoForm

class HomeView(TemplateView):
    template_name = 'pedido/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        proveedores = Proveedor.objects.all()
        pedidos_activos = {}

        for proveedor in proveedores:
            pedidos_activos[proveedor] = proveedor.pedido_set.exclude(estado='Et')

        context['proveedores'] = proveedores
        context['pedidos_activos'] = pedidos_activos  # Añade el diccionario al contexto
        print("Pedidos activos:", pedidos_activos)
        return context
    

def nuevo_pedido(request, proveedor_id):
    # Código para crear un nuevo pedido
    proveedor = Proveedor.objects.get(id=proveedor_id)
    pedido_pendiente, _ = Pedido.objects.get_or_create(proveedor=proveedor, estado='Pd')
    
    pedido_pendiente.save()
    
    return redirect('pedido:editar-pedido', pedido_id=pedido_pendiente.id)        
    
class NuevoPedidoView(TemplateView):
    '''Vista para crear un nuevo pedido
    
    Se encarga de listar los artículos faltantes y de crear un 
    nuevo pedido
    
    '''
    
    template_name = 'pedido/editar_pedido.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Código para listar los artículos faltantes
        proveedor_id = self.kwargs.get('proveedor_id')
        context['proveedor'] = Proveedor.objects.get(id=proveedor_id)
        context['lista_articulos_faltantes'] = Lista_Pedidos.objects.filter(proveedor=proveedor_id).order_by('item')
        
        context['pedido'] = None
        context['pedido'] = Pedido.objects.filter(proveedor=proveedor_id).exclude(estado='Et').first()
        #Si el listado de pedidos esta vacio entonces crear un nuevo pedido
        if not context['pedido']:
            nuevo_pedido = Pedido.objects.create(proveedor=context['proveedor'])
            nuevo_pedido.save()
            context['pedido'] = nuevo_pedido
            context['lista_articulos_faltantes'] = Lista_Pedidos.objects.filter(proveedor=proveedor_id).order_by('item')
        print("pedido:", context['pedido'])
        print("Lista de artículos faltantes:", context['lista_articulos_faltantes'])
        return context

    def post(self, request, proveedor_id):
        # Código para procesar el formulario de nuevo pedido
        pass
    
class ListarArticulosFaltantesView(TemplateView):
    template_name = 'pedido/listar_faltantes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Código para listar los artículos faltantes
        proveedor_id = self.kwargs.get('proveedor_id')
        context['lista_articulos_faltantes'] = Lista_Pedidos.objects.filter(proveedor=proveedor_id).order_by('item')
        print("Lista de artículos faltantes:", context['lista_articulos_faltantes'])
        return context


class ListarArticulosPedidosView(TemplateView):
    template_name = 'pedido/listar_pedidos_descontinuado.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Código para listar los pedidos
        context['lista_pedidos'] = ArticuloPedido.objects.all()
        return context

class EditarPedidoView(TemplateView):
    template_name = 'pedido/editar_pedido.html'
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

class DetallePedidoView(TemplateView):
    template_name = 'pedido/detalle_pedido.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Código para listar los pedidos
        pedido_id = self.kwargs.get('pedido_id')
        context['pedido'] = Pedido.objects.get(id=pedido_id)
        context['articulos'] = context['pedido'].articulo_pedido.all()
        return context

    def get(self, request, pedido_id):
        context = self.get_context_data()
        return self.render_to_response(context)

    def post(self, request, pedido_id):
        # Código para procesar el formulario de edición de pedidos
        pass

class ControlarPedidoView(TemplateView):
    template_name = 'pedido/controlar_pedido.html'
    
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
    
def agregar_al_stock(request):
    # Código para agregar un artículo al stock
    data = json.loads(request.body)
    print("Agregando al stock", data)
    articulo_pedido = ArticuloPedido.objects.get(id=data.get('articulo_id'))
    articulo_pedido.llego = data.get('llego')
    articulo_pedido.item.stock = articulo_pedido.item.stock + articulo_pedido.cantidad
    articulo_pedido.cantidad = 0
    articulo_pedido.item.save()
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

def actualizar_llego(request, articulo_id):
    # Código para actualizar el campo llego de un pedido
    print("Actualizando llego de articulo", articulo_id)
    articulo_pedido = ArticuloPedido.objects.get(id=articulo_id)
    data = json.loads(request.body)
    articulo_pedido.llego = data.get('llego')
    # Process the data as needed
    articulo_pedido.save()
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

class EnviarPedidoView(View):
    def post(self, request, pedido_id):
        # Código para enviar el pedido
        
        pass

class NuevoStockView(View):
    def get(self, request):
        form = ArticuloPedidoForm()
        return render(request, 'pedido/nuevo_stock.html', {'form': form})

    def post(self, request):
        form = ArticuloPedidoForm(request.POST)
        if form.is_valid():
            form.save()
            print("Formulario válido, pedido guardado.")
        else:
            print("Formulario no válido.")
            print(form.errors)
        return render(request, 'pedido/nuevo_stock.html', {'form': form})

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
    
    devolucion = Devolucion.objects.create(
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

class CargarStockView(View):
    def post(self, request, producto_id):
        # Código para actualizar el stock de un producto
        pass
    
class ListarPedidosView(TemplateView):
    template_name = 'pedido/listar_pedidos.html'
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        # Código para listar los pedidos
        context['lista_pedidos'] = Pedido.objects.all()
        return context

from dal_select2.views import Select2QuerySetView
from bdd.models import Item

class ItemAutocomplete(Select2QuerySetView):
    def get_queryset(self):
        print("get_queryset called")
        if not self.request.user.is_authenticated:
            print("User is not authenticated")
            return Item.objects.none()

        qs = Item.objects.all()
        
        codigo = self.request.GET.get('q', None)
        proveedor_id = self.request.GET.get('proveedor_id')
        proveedor = Proveedor.objects.get(id=proveedor_id)
        print(f"codigo: {codigo}, proveedor_id: {proveedor_id}")
        
        if codigo:
            print(f"Filtering items with codigo starting with {codigo}")
            qs = qs.filter(codigo__istartswith=codigo, codigo__endswith=proveedor.identificador.abreviatura)
            print('abreviatura:', proveedor.identificador.abreviatura)
        print(f"Returning {len(qs)} items")
        print(qs)
        return qs
    
    def render_to_response(self, context):
        # Transforma la lista de items a una lista de diccionarios con 'id' y 'text'
        data = {
            'items': [{'id': item.id, 'text': str(item)} for item in context['object_list']],
            'total_count': len(context['object_list'])
        }
        return JsonResponse(data)



