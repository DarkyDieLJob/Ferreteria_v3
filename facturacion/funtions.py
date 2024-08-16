from .classes import ComandoFiscal, TicketFactura
from bdd.models import Carrito, Articulo, ArticuloSinRegistro
from .models import Cliente, MetodoPago, Transaccion
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import ArticuloVendido
from schema import Schema, And, Use
import json

def ciclo(fiscal=ComandoFiscal):
    i = 1
    fiscal.set_encabezado(i)
    fiscal.set_tipo_cliente()
    fiscal.set_articulos()
    fiscal.set_cierre()   
     
def ciclo_desborde(fiscal=ComandoFiscal):
    for i in range(fiscal.cantidad_tickets):
        print(fiscal.cantidad_tickets)
        fiscal.set_encabezado(i)
        fiscal.set_tipo_cliente()
        fiscal.set_articulos_desborde()
        fiscal.set_cierre()

def cliente_to_dict(cliente):
    data = {
        'id':cliente.id,
        "razon_social":cliente.razon_social,
        "cuit_dni":cliente.cuit_dni,
        "domicilio":cliente.domicilio,
        "telefono":cliente.telefono,
    }
    return data

def mapear_datos(data):
    return {
        "nombre_usuario": data["usuario"],
        "carrito_id": data["carrito_id"],
        "id_cliente": data["cliente_id"],
        "total": data["total"],
        "total_efectivo": data["total_efectivo"],
        "articulos_vendidos": data["articulos_vendidos"],
        "id_metodo_de_pago": data["metodo_de_pago"],
    }


def request_on_procesar_transaccion_to_dict(request):
    schema = Schema({
        "usuario": str,
        "carrito_id": int,
        "cliente_id": int,
        "total": float,
        "total_efectivo": float,
        "articulos_vendidos": list,
        "metodo_de_pago": int,
    })

    try:
        data = json.loads(request.body)
        schema.validate(data)  # Validación de los datos
        
        return mapear_datos(data)
    except (json.JSONDecodeError, SchemaError) as e:
        # Manejar el error, por ejemplo, devolver un mensaje de error personalizado
        return {'error': str(e)}

def registrar_articulos_vendidos(request_dict):
    try:
        usuario = User.objects.get(username=request_dict['nombre_usuario'])
    except User.DoesNotExist:
        return HttpResponse(status=500)
        
    metodo_de_pago = MetodoPago.objects.get(id=request_dict['id_metodo_de_pago'])
    
    metodo_de_pago_display = metodo_de_pago.display
    print("metodo de pago: ", metodo_de_pago_display)
    print("total: ", request_dict['total'])
    print("total_efectivo: ", request_dict['total_efectivo'])
    if metodo_de_pago_display == "Efectivo con Ticket" and request_dict['total_efectivo']:
        monto_abonado = request_dict['total_efectivo']
    else:
        monto_abonado = request_dict['total']
    print("Monto abonado: ", monto_abonado)
    
    carrito = Carrito.objects.get(id=request_dict['carrito_id'])
    
    # Obtén los Articulo y ArticuloSinRegistro del carrito
    articulos = Articulo.objects.filter(carrito=carrito)
    articulos_sin_registro = ArticuloSinRegistro.objects.filter(carrito=carrito)
    
    # Luego, creamos la Transaccion.
    transaccion = Transaccion.objects.create(
        usuario=usuario,
        metodo_de_pago=metodo_de_pago,  # Aquí asignamos la instancia de MetodoPago, no el ID.
        total=monto_abonado,
    )
    
    for articulo in list(articulos) + list(articulos_sin_registro):
        # Crea una instancia de ArticuloVendido con los detalles proporcionados
        if isinstance(articulo, Articulo):
            articulo_vendido = ArticuloVendido.objects.create(
                item=articulo.item,
                cantidad=articulo.cantidad
            )
        else:  # ArticuloSinRegistro
            articulo_vendido = ArticuloVendido.objects.create(
                sin_registrar=articulo,
                cantidad=articulo.cantidad
            )

        # Asigna el ArticuloVendido a la Transaccion
        transaccion.articulos_vendidos.add(articulo_vendido)
    
    json = {}
    
    if request_dict['id_metodo_de_pago'] != 1 and request_dict['id_cliente'] != None:
        #fiscal = ComandoFiscal(request_dict['carrito_id'], request_dict['id_cliente'], metodo_de_pago_display, monto_abonado)
        #ciclo_desborde(fiscal)
        if request_dict['id_cliente'] == '':
            cliente_id = 1
        else:
            cliente_id = request_dict['id_cliente']
        
        print("cliente_id: ")
        print(cliente_id)
        transaccion.cliente = Cliente.objects.get(id=cliente_id)
    
    
        ticket_factura = TicketFactura(transaccion)
        json = ticket_factura.get_ticket_json()    
    
    return {
        "json" : json,
        "articulos" : articulos,
        "articulos_sin_registro" : articulos_sin_registro,
        "transaccion" : transaccion,
        }