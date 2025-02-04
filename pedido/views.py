import json
from typing import Any
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from .models import ArticuloPedido, Pedido
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
    
class NuevoPedidoView(TemplateView):
    template_name = 'pedido/nuevo_pedido.html'
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

    def post(self, request):
        form = ArticuloPedidoForm(request.POST)
        if form.is_valid():
            form.save()
            print("Formulario válido, pedido guardado.")
        else:
            print("Formulario no válido.")
            print(form.errors)
            
        return JsonResponse({'status': 'ok'})

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

class ControlarPedidoView(View):
    template_name = 'pedido/controlar_pedido.html'
    
    def get(self, request, pedido_id):
        # Código para controlar un pedido
        pedido = Pedido.objects.get(id=pedido_id)
        articulos = pedido.articulo_pedido.all()
        return render(request, self.template_name, {'pedido': pedido, 'articulos': articulos})
    
    def post(self, request, pedido_id):
        # Código para controlar un pedido
        data = json.loads(request.body)
        print("Controlando pedido", data)
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.estado = 'Et'
        pedido.save()
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
    articulo_faltante.pedido = not articulo_faltante.pedido
    articulo_faltante.cantidad = articulo_faltante.cantidad - float(data.get('cantidad'))
    articulo_faltante.save()
    
    pedido_id = data.get('pedido_id')
    pedido = Pedido.objects.get(id=pedido_id)
    pedido.articulo_pedido.add(articulo_pedido)
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
    articulo_pedido.cantidad = data.get('cantidad')
    articulo_pedido.save()
    return JsonResponse({'status': 'ok'})

def enviar_pedido(request):
    # Código para enviar un pedido
    data = json.loads(request.body)
    print("Enviando pedido", data)
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
            return Item.objects.none()

        qs = Item.objects.all()
        
        codigo = self.request.GET.get('q', None)

        if codigo:
            print(f"Filtering items with codigo starting with {codigo}")
            qs = qs.filter(codigo__istartswith=codigo, trabajado=False)

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



