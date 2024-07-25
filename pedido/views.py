from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from pedido.models import Pedido
from .forms import PedidoForm

class ListarPedidosView(TemplateView):
    template_name = 'pedido/listar_pedidos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Código para listar los pedidos
        context['lista_pedidos'] = Pedido.objects.all()
        return context

class EditarPedidoView(View):
    def get(self, request, pedido_id):
        # Código para obtener el formulario de edición de pedidos
        pass

    def post(self, request, pedido_id):
        # Código para procesar el formulario de edición de pedidos
        pass

class EnviarPedidoView(View):
    def post(self, request, pedido_id):
        # Código para enviar el pedido
        
        pass

class NuevoStockView(View):
    def get(self, request):
        form = PedidoForm()
        return render(request, 'pedido/nuevo_stock.html', {'form': form})

    def post(self, request):
        form = PedidoForm(request.POST)
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



