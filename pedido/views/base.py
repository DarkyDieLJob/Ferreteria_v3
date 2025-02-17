from django.views.generic import TemplateView
from dal_select2.views import Select2QuerySetView
from bdd.models import Item, Proveedor, Lista_Pedidos
from django.http import JsonResponse
import json
from pedido.models import ArticuloPedido

class GeneralPedidoView(TemplateView):
    ''' Vista a modo de interfaz para las operaciones generales de pedidos
    '''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['barra_de_navegacion']= [
            {'text_display': 'Listar Pedidos', 'url': {'ruta': 'pedidos/home/'}},
            {
                'text_display': 'Sección 2',
                'subsecciones': [
                    {'text_display': 'Subsección 2.1', 'url': {'ruta': 'subseccion21'}},
                    {'text_display': 'Subsección 2.2', 'url': {'ruta': 'subseccion22'}},
                ]
            },
            {'text_display': 'Listar Devoluciones', 'url': {'ruta': 'pedidos/listar_devoluciones/'}},
        ]
        return context
    

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
    
def agregar_al_stock(request):
    # Código para agregar un artículo al stock
    data = json.loads(request.body)
    print("Agregando al stock", data)
    articulo_pedido = ArticuloPedido.objects.get(id=data.get('articulo_id'))
    articulo_pedido.llego = data.get('llego')
    articulo_pedido.item.stock = articulo_pedido.item.stock + articulo_pedido.cantidad
    articulo_pedido.cantidad = 0
    
    articulo_faltante, _ = Lista_Pedidos.objects.get_or_create(proveedor_id=articulo_pedido.proveedor.id, item_id=articulo_pedido.item.id)
    articulo_faltante.pedido = False
    articulo_faltante.cantidad = articulo_faltante.cantidad - float(1)
    articulo_faltante.save()
    
    articulo_pedido.item.save()
    articulo_pedido.save()
    return JsonResponse({'status': 'ok'})

