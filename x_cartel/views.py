from django.views.generic import TemplateView
from django.shortcuts import render
from .models import Carteles, CartelesCajon, Cartelitos

class Cartelito(TemplateView):
    template_name = 'x_cartel/cartelitos_x6.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cartelitos = Cartelitos.objects.filter(habilitado=True)
        context['cartelitos'] = cartelitos
        print(cartelitos)
        return context
    

class Cartel(TemplateView):
    template_name = 'x_cartel/prueba_edicion.html'
    def get_context_data(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        
        item_id = self.kwargs.get('item_id')
        
        cajon_id = self.kwargs.get('cajon_id')
        
        try:
            if item_id is not None:
                item = Item.objects.get(id=item_id)
                context['descripcion'] = item.descripcion
                context['cartel'] = None
                if item_id is not None:
                    try:
                        cartel, created = Carteles.objects.get_or_create(id=item_id)
                        context['cartel'] = cartel
                    except Exception as e:
                        print(e)
        except Exception as e:
                    print(e)
        try:
            if cajon_id is not None:
                context['articulos'] = Item.objects.filter(cajon=cajon_id)
                context['hay_descripciones'] = True
                context['cartel'] = None
                if cajon_id is not None:
                    try:
                        cartel, created = CartelesCajon.objects.get_or_create(id=cajon_id)
                        context['cartel'] = cartel
                    except Exception as e:
                        print(e)
        except Exception as e:
                    print(e)    
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        print(context)
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(request)
        descripcion = request.POST.get('descripcion')
        tamano_descripcion = request.POST.get('tamano_descripcion')
        if tamano_descripcion == '':
            tamano_descripcion = 0  # Valor por defecto
        else:
            tamano_descripcion = int(tamano_descripcion)

        texto_final = request.POST.get('texto_final')
        tamano_texto_final = request.POST.get('tamano_texto_final')
        if tamano_texto_final == '':
            tamano_texto_final = 0  # Valor por defecto
        else:
            tamano_texto_final = int(tamano_texto_final)

        final = request.POST.get('final')
        tamano_final = request.POST.get('tamano_final')
        if tamano_final == '':
            tamano_final = 0  # Valor por defecto
        else:
            tamano_final = int(tamano_final)

        texto_final_efectivo = request.POST.get('texto_final_efectivo')
        tamano_texto_final_efectivo = request.POST.get('tamano_texto_final_efectivo')
        if tamano_texto_final_efectivo == '':
            tamano_texto_final_efectivo = 0  # Valor por defecto
        else:
            tamano_texto_final_efectivo = int(tamano_texto_final_efectivo)

        final_efectivo = request.POST.get('final_efectivo')
        tamano_final_efectivo = request.POST.get('tamano_final_efectivo')
        if tamano_final_efectivo == '':
            tamano_final_efectivo = 0  # Valor por defecto
        else:
            tamano_final_efectivo = int(tamano_final_efectivo)

        item_id = self.kwargs.get('item_id')
        cajon_id = self.kwargs.get('cajon_id')
        
        revisar = request.POST.get('revisar')
        
        if item_id is not None or cajon_id is not None:
            if item_id is not None:
                cartel = Carteles.objects.get(id=item_id)
                item = Item.objects.get(id=item_id)
                cartel.proveedor = item.proveedor
                cartel.item = item
                print(item.proveedor)
            elif cajon_id is not None:
                cartel = CartelesCajon.objects.get(id=cajon_id)
                items_cajon = Item.objects.filter(cajon = cajon_id)
                #Aca revisar filtros de carteles asociados a cajon con revisar en True. fin.
            
                print("revisar: ", revisar)
                if revisar is not None:
                    if revisar == 'true':
                        cartel.revisar = True
                        for item in items_cajon:
                            cartel_item, _ = Carteles.objects.get_or_create(id=item.id)
                            cartel_item.revisar = True
                            cartel_item.save()
                else:
                    cartel.revisar = False
                    for item in items_cajon:
                        cartel_item, _ = Carteles.objects.get_or_create(id=item.id)
                        cartel_item.revisar = False
                        cartel_item.save()
                
            cartel.descripcion = descripcion
            cartel.tamano_descripcion = tamano_descripcion
            cartel.texto_final = texto_final
            cartel.tamano_texto_final = tamano_texto_final
            cartel.final = final
            cartel.tamano_final = tamano_final
            cartel.texto_final_efectivo = texto_final_efectivo
            cartel.tamano_texto_final_efectivo = tamano_texto_final_efectivo
            cartel.final_efectivo = final_efectivo
            cartel.tamano_final_efectivo = tamano_final_efectivo
        cartel.save()
        return render(request, self.template_name, context)

class PruebaEdicion(TemplateView):
    template_name = 'x_cartel/prueba_edicion.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_id'] = self.kwargs.get('item_id')
        return context

from bdd.models import Item
from django.http import JsonResponse

def precios_articulos(request, articulo_id):
    if request.method == 'GET':
        item = Item.objects.get(id=articulo_id)
        dato = {
            'id': item.id,
            'final': item.final,
            'final_efectivo': item.final_efectivo,
            'final_rollo': item.final_rollo,
            'final_rollo_efectivo': item.final_rollo_efectivo,
        }
    return JsonResponse(dato, safe=False)

def precios_articulos_cajon(request, cajon_id):
    if request.method == 'GET':
        items = Item.objects.filter(cajon=cajon_id)
        datos = []
        for item in items:
            dato = {
                'id': item.id,
                'final': item.final,
                'final_efectivo': item.final_efectivo,
                'final_rollo': item.final_rollo,
                'final_rollo_efectivo': item.final_rollo_efectivo,
            }
            datos.append(dato)
    return JsonResponse(datos, safe=False)

from django.http import JsonResponse
from django.views import View

class CrearCartelitoView(View):
    
    def get(self, request, *args, **kwargs):
        item_id = request.GET.get('item_id')
        if item_id == '':
            data = {'descripcion': '', 'habilitado': False}
            return JsonResponse(data)
        item = Item.objects.get(id=item_id)
        try:
            cartelito = Cartelitos.objects.get(item=item)
            data = {'descripcion': cartelito.descripcion, 'habilitado': cartelito.habilitado}
        except Cartelitos.DoesNotExist:
            data = {'descripcion': '', 'habilitado': False}
        return JsonResponse(data)
    
    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('item_id')
        descripcion = request.POST.get('descripcion', None)
        item = Item.objects.get(id=item_id)
        cartelito, created = Cartelitos.objects.get_or_create(item=item, defaults={'descripcion': item.descripcion})
        if not created:
            cartelito.habilitado = not cartelito.habilitado
            if descripcion is not None:  # Aquí verificamos si se proporcionó una descripción
                cartelito.descripcion = descripcion  # Si se proporcionó, actualizamos la descripción
            cartelito.save()
        return JsonResponse({'descripcion': cartelito.descripcion, 'habilitado': cartelito.habilitado})


