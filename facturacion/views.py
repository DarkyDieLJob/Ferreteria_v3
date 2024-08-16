from django.shortcuts import redirect
from bdd.views import Inicio
from bdd.models import Carrito, Articulo, ArticuloSinRegistro, Item, Lista_Pedidos, NavBar
from boletas.models import Boleta
from facturacion.forms import ClienteForm
from .models import Cliente, CierreZ, Transaccion
from .funtions import cliente_to_dict, request_on_procesar_transaccion_to_dict
from django.http import JsonResponse
from django.http import HttpResponse
from .models import MetodoPago
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from bdd.models import ArticuloSinRegistro, Carrito
import json
from .funtions import registrar_articulos_vendidos
from .cliente import conectar_a_websocket
import asyncio
from django.views.generic import TemplateView
from django.shortcuts import redirect

def obtener_metodos_pago(request):
    metodos_pago = MetodoPago.objects.all()
    data = [{"id": metodo_pago.id, "display": metodo_pago.display} for metodo_pago in metodos_pago]
    return JsonResponse(data, safe=False)

def obtener_cliente(request):
    clientes = Cliente.objects.all()
    data = {'clientes':[]}
    for cliente in clientes:
        c = cliente_to_dict(cliente)
        data['clientes'].append(c)
    return JsonResponse(data, safe=False)

def prueba_post(request):
    if request.method == 'POST':
        print(request)
        print(request.META)
        data = json.loads(request.body)
        print(data)
        return HttpResponse(status=200)


def procesar_transaccion(request):
    if request.method == 'POST':
        print("procesar_transaccion... request:")
        print(request)
        print("Datos recibidos en request.POST:")
        print(request.POST)
        print("Datos recibidos en request.body")
        
        try:
            data = json.loads(request.body)
            print(data)
            # ... your logic using 'data' ...
        except json.JSONDecodeError:
            # Handle invalid JSON data here
            print("Error: Invalid JSON format")
            return HttpResponseBadRequest("Invalid JSON data")
        
        request_dict = request_on_procesar_transaccion_to_dict(request)
        print("request_dict: ")
        print(request_dict)
        
        registro_dic = registrar_articulos_vendidos(request_dict)
        print(registro_dic)
        json_data = registro_dic["json"]
        print("boleta json: ")
        print(json)

        for boleta in json_data:
            try:
                rta = asyncio.run(conectar_a_websocket(boleta))
                print("Respuesta: ")
                print(rta)
            except asyncio.CancelledError as e:
                print("ticket cancelado")
            except asyncio.TimeoutError as e:
                print("tiempo de respuesta excedido")
            except Exception as e:
                print("sin boletas??")
                print(e)
        articulos = registro_dic["articulos"]
        articulos.delete()
        articulos_sin_registro = registro_dic["articulos_sin_registro"]
        articulos_sin_registro.delete()
        transaccion = registro_dic["transaccion"]
        transaccion.save()


    return HttpResponse(status=200)

def vista_cierre_z(request):
    cierre_z = {
    "dailyClose": "Z",
    "printerName": "IMPRESORA_FISCAL"
    }
    respuesta = asyncio.run(conectar_a_websocket(cierre_z))
    return redirect("/buscador/")

@csrf_exempt
@require_POST
def agregar_articulo_sin_registro(request):
    # Parse the JSON data from the request
    data = json.loads(request.body)

    # Get the data from the request
    descripcion = data.get('descripcion')
    cantidad = data.get('cantidad')
    precio = data.get('precio')
    carrito_id = data.get('carrito_id')

    # Get the Carrito instance
    carrito = Carrito.objects.get(id=carrito_id)
    contador = ArticuloSinRegistro.objects.filter(carrito=carrito, descripcion__icontains=descripcion).count()
    print("contador: ",contador)
    if (contador + 1) > 1:
        descripcion += str(contador + 1)
    # Create the ArticuloSinRegistro instance
    articulo_sin_registro, created = ArticuloSinRegistro.objects.get_or_create(
        descripcion=descripcion,
        carrito=carrito,
        defaults={'cantidad': cantidad, 'precio': precio}
    )

    # If the ArticuloSinRegistro already exists, update the quantity and price
    if not created:
        articulo_sin_registro.cantidad = cantidad
        articulo_sin_registro.precio = precio
        articulo_sin_registro.save()

    # Return the JSON response
    return JsonResponse({'articulo_sin_registro': articulo_sin_registro.id}, status=201)

@csrf_exempt
@require_POST
def eliminar_articulo(request):
    # Parse the JSON data from the request
    data = json.loads(request.body)

    # Get the ID from the request
    id = data.get('id')
    print("id articulo a borrar: ", id)
    # Get the Articulo instance
    articulo = Articulo.objects.get(id=id)
    
    # Delete diferencia de cantidad to Pedido
    try:
        pedido = Lista_Pedidos.objects.get(item=articulo.item)
        pedido.cantidad -= articulo.cantidad
        pedido.save()
    except:
        pass

    # Delete the Articulo
    articulo.delete()

    # Return the JSON response
    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_POST
def actualizar_cantidad_articulo(request):
    # Parse the JSON data from the request
    data = json.loads(request.body)

    # Get the ID and new quantity from the request
    id = data.get('id')
    cantidad = data.get('cantidad')

    # Get the Articulo instance
    articulo = Articulo.objects.get(id=id)
    item = articulo.item
    
    try:
        cantidad = float(cantidad)
    except ValueError:
        print("Error: La cadena no es un número válido.")
        
    # Set difference of quantity of the Articulo.cantidad y new.cantidad
    diferencia_cantidad =  cantidad - articulo.cantidad
    
    # Add diferencia de cantidad to Pedido
    pedido = Lista_Pedidos.objects.get(item=item)
    pedido.cantidad += diferencia_cantidad

    # Update the quantity of the Articulo
    articulo.cantidad = cantidad
    
    # Save instances of models
    articulo.save()
    pedido.save()

    # Return the JSON response
    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_POST
def eliminar_articulo_sin_registro(request):
    # Parse the JSON data from the request
    data = json.loads(request.body)

    # Get the values from the request
    id = data.get('id')

    # Get the ArticuloSinRegistro instance
    articulo_sin_registro = ArticuloSinRegistro.objects.get(id=id)

    # Delete the ArticuloSinRegistro
    articulo_sin_registro.delete()

    # Return the JSON response
    return JsonResponse({'status': 'success'}, status=200)


@csrf_exempt
@require_POST
def actualizar_cantidad_articulo_sin_registro(request):
    # Parse the JSON data from the request
    data = json.loads(request.body)

    # Get the ID and new quantity from the request
    id = data.get('id')
    cantidad = data.get('cantidad')

    # Get the ArticuloSinRegistro instance
    articulo_sin_registro = ArticuloSinRegistro.objects.get(id=id)

    # Update the quantity of the ArticuloSinRegistro
    articulo_sin_registro.cantidad = cantidad
    articulo_sin_registro.save()

    # Return the JSON response
    return JsonResponse({'status': 'success'}, status=200)

from datetime import datetime
from django.db.models import Sum

class Facturacion(TemplateView):
    template_name = 'facturacion/facturacion.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["barra_de_navegacion"] = NavBar.objects.all()
        fecha_actual = datetime.now()
        transacciones = Transaccion.objects.filter(fecha__date=fecha_actual.date())
        context["datos"] = transacciones
        
        context["totales"] = []
        for i in range(1, MetodoPago.objects.all().count()):
            data = {}
            data["nombre"] = MetodoPago.objects.get(id=i).display
            
            ventas = transacciones.filter(metodo_de_pago=i)
            data["total"] = ventas.aggregate(Sum("total"))["total__sum"]
            data["cantidad"] = ventas.count()
            data["datos"] = ventas
            context["totales"].append(data)
        return context
    
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
class CierreZVieW(TemplateView):
    template_name = 'facturacion/cierre_z.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barra_de_navegacion'] = NavBar.objects.all()
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["cierres_fiscales"] = CierreZ.objects.all()
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        cierre_z = {
        "dailyClose": "Z",
        "printerName": "IMPRESORA_FISCAL"
        }
        s = asyncio.run(conectar_a_websocket(cierre_z))

        import ast
        data = ast.literal_eval(s)

        print(type(dict(data)))

        # Extraemos los valores relevantes del diccionario
        rta = data["rta"][0]["rta"]
        print("RTA: ",rta)

        # Creamos una instancia del modelo CierreZ con los valores extraídos
        cierre_z = CierreZ(
            RESERVADO_SIEMPRE_CERO=int(rta["RESERVADO_SIEMPRE_CERO"]),
            cant_doc_fiscales=int(rta["cant_doc_fiscales"]),
            cant_doc_nofiscales_homologados=int(rta["cant_doc_nofiscales_homologados"]),
            ultima_nc_a=int(rta["ultima_nc_a"]),
            ultima_nc_b=int(rta["ultima_nc_b"]),
            monto_percepciones=float(rta["monto_percepciones"]),
            monto_percepciones_nc=float(rta["monto_percepciones_nc"]),
            monto_credito_nc=float(rta["monto_credito_nc"]),
            ultimo_doc_a=int(rta["ultimo_doc_a"]),
            ultimo_doc_b=int(rta["ultimo_doc_b"]),
            zeta_numero=rta["zeta_numero"],
            monto_imp_internos_nc=float(rta["monto_imp_internos_nc"]),
            cant_doc_fiscales_cancelados=int(rta["cant_doc_fiscales_cancelados"]),
            monto_iva_doc_fiscal=float(rta["monto_iva_doc_fiscal"]),
            monto_imp_internos=float(rta["monto_imp_internos"]),
            status_fiscal=rta["status_fiscal"],
            status_impresora=rta["status_impresora"],
            monto_iva_nc=float(rta["monto_iva_nc"]),
            monto_ventas_doc_fiscal=float(rta["monto_ventas_doc_fiscal"]),
            cant_doc_nofiscales=int(rta["cant_doc_nofiscales"])
        )

        # Guardamos la instancia en la base de datos
        cierre_z.save()

        return self.render_to_response(context)


class Clientes(TemplateView):
    template_name = 'facturacion/add_client.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        form = ClienteForm()
        context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # Procesa el formulario aquí
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda el cliente en la base de datos

            # Redirige al usuario a /buscador/
            return redirect('/buscador/')

        # Si el formulario no es válido, vuelve a mostrar la página con errores
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)





    