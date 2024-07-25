#marcar lista de pedidos, como trabajados. agregar "eliminar pedido"
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'
import django
django.setup()

from bdd.models import  Item, Lista_Pedidos




def principal():
    pedidos = Lista_Pedidos.objects.all()
    for pedido in pedidos:
        print(pedido.item.id)
        articulo_trabajado = Item.objects.get(id=pedido.item.id)
        articulo_trabajado.trabajado = True
        articulo_trabajado.proveedor = pedido.proveedor
        articulo_trabajado.save()
        print(articulo_trabajado," Guardado puto!!")

def lista():
    listado = Item.objects.filter(trabajado=True)
    for item in listado:
        print(item.proveedor)
        
from x_cartel.models import Carteles
from bdd.models import Proveedor

def listar_carteles():
    listado = Carteles.objects.all()
    for cartel in listado:
        try:
            item = cartel.item
            print("articulo: ", item)
            print("proveedor actual: ", item.proveedor)

            # Si el proveedor del item o del cartel no está definido, intentamos actualizarlo
            if item.proveedor is None or cartel.proveedor is None:
                # Suponemos que el código tiene el formato '#####/abreviatura'
                codigo_parts = item.codigo.split('/')
                if len(codigo_parts) == 2:
                    abreviatura = '/' + codigo_parts[1]  # Agregamos la barra a la abreviatura
                    try:
                        proveedor = Proveedor.objects.get(identificador__abreviatura=abreviatura)
                        item.proveedor = proveedor
                        cartel.proveedor = proveedor
                        item.save()  # Guardamos el cambio en el item
                        cartel.save()  # Guardamos el cambio en el cartel
                        print(f"Proveedor actualizado a {proveedor} para el item {item} y el cartel {cartel}")
                    except Proveedor.DoesNotExist:
                        print(f"No se encontró un proveedor con la abreviatura {abreviatura}")
        except:
            pass

def agregar_precio():
    lista = ['13019/V',]
    precio = [194580]
    
    for i in range(len(lista)):
        print(lista[i])
        item = Item.objects.get(codigo=lista[i])
        item.final_efectivo = precio[i]
        item.save()
    
from facturacion.classes import ComandoFiscal

def get_status_fiscal():
    fiscal = ComandoFiscal(carrito_id=2, id_cliente=0, tipo_pago='Debito', monto_abonado='0')
    fiscal.get_status()
    
from django.db import transaction
from bdd.models import Item

def update_items():
    # Obtén todos los objetos Item donde final_efectivo es 0 o 0.0
    items_to_update = Item.objects.filter(final_efectivo__in=[0, 0.0])

    # Actualiza final_efectivo al valor de final en lotes de 10000
    for i in range(0, items_to_update.count(), 10000):
        with transaction.atomic():
            batch = items_to_update[i:i+10000]
            for item in batch:
                item.final_efectivo = item.final
            Item.objects.bulk_update(batch, ['final_efectivo'])

    # Obtén todos los objetos Item donde codigo no contiene una barra ('/')
    items_to_delete = Item.objects.exclude(codigo__contains='/')

    # Elimina todos estos objetos de una vez
    with transaction.atomic():
        items_to_delete.delete()

def custom_round(price):
    # Obtén el número de dígitos en el precio
    digits = len(str(price))

    # Aplica las reglas de redondeo basadas en el número de dígitos
    if digits == 1:
        if price == 0:
            pass
        else:
            return 10
    elif digits == 2:
        return round(price / 5) * 5 if price > 10 else 10
    elif digits == 3:
        return round(price / 10) * 10
    elif digits == 4:
        return round(price / 50) * 50
    elif digits == 5:
        return round(price / 50) * 50
    elif digits == 6:
        return round(price / 50) * 50
    elif digits >= 7:
        return round(price / 500) * 500
    else:
        return price

def redondear():
    items = Item.objects.all()
    items_para_actualizar = []
    for item in items:
        item.final = custom_round(item.final)
        item.final_efectivo = custom_round(item.final_efectivo)
        items_para_actualizar.append(item)
        
    Item.objects.bulk_update(items_para_actualizar,["final","final_efectivo"])

import time

def dibujo():
    import time
    import os

    # Dibujo del vaquero y la PC
    vaquero = "V"
    pc = "P"

    # Dibujo del látigo
    latigo = "---"

    # Animación
    for _ in range(5):  # Número de veces que se repite la animación
        os.system('cls' if os.name == 'nt' else 'clear')  # Limpia la pantalla
        print(vaquero + latigo + pc)
        time.sleep(0.5)
        os.system('cls' if os.name == 'nt' else 'clear')  # Limpia la pantalla
        print(vaquero + "   " + pc)
        time.sleep(0.5)



if __name__ == '__main__':
    pass