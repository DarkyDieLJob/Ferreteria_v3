import os
from bdd.classes import Patoba
from django.conf import settings as const
from x_cartel.models import Carteles, CartelesCajon
from bdd.models import  Item, Sub_Carpeta, Sub_Titulo, ListaProveedores
import os
import csv
import unicodedata

os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'

def limpiar_texto(texto):
    """Limpia un texto convirtiendo caracteres no ASCII a su equivalente ASCII."""
    texto = unicodedata.normalize('NFKD', texto)
    texto = texto.encode('ASCII', 'ignore').decode('ASCII')
    return texto

def validar_digitos_str(cadena):
    # Validar que el input es una cadena
    if not isinstance(cadena, str):
        return False

    # Iterar sobre cada caracter en la cadena
    for caracter in cadena:
        # Si el caracter no es un dígito y no es un punto o coma, retornar False
        if not caracter.isdigit() and caracter not in ['.', ',']:
            return False

    # Si todos los caracteres son dígitos, puntos o comas, retornar True
    return True

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

def crear_o_actualizar_registro(row):
    with open('items.csv', 'a', newline='', encoding='utf8') as file:
            writer = csv.writer(file)
            # Agrega la fila con error al archivo CSV
            writer.writerow(row.values())
    try:
        # Recuperar o crear una instancia de Sub_Carpeta
        sub_carpeta_nombre = row.pop('sub_carpeta')
        sub_carpeta, created = Sub_Carpeta.objects.get_or_create(nombre=sub_carpeta_nombre)
        row['sub_carpeta'] = sub_carpeta
        sub_carpeta = Sub_Carpeta.objects.get(nombre=sub_carpeta_nombre)
        sub_titulo_nombre = row.pop('sub_titulo')
        sub_titulo, created = Sub_Titulo.objects.get_or_create(nombre=sub_titulo_nombre)
        row['sub_titulo'] = sub_titulo
        if row['final_efectivo'] <= 0:
            row['final_efectivo'] == row['final']
    except:
        pass
    #print(row)
    try:
        item, created = Item.objects.get_or_create(codigo=row['codigo'], defaults=row)
        item.marcar_actualizado()
        if not created:
            for key, value in row.items():
                setattr(item, key, value)
        item.descripcion = limpiar_texto(row.pop('descripcion'))
        item.save()
    except Exception as e:
        print('Error al intentar guardar: ', row['codigo'], flush=True)
        print(e, flush=True)
    try:
        item.save()
    except Exception as e:
        print("item no se guardo porque el boludo tenia un error.",row, flush=True)
        print(e, flush=True)
        
        # Abre el archivo CSV donde se guardarán las filas con errores
        with open('errores.csv', 'a', newline='', encoding='utf8') as file:
            writer = csv.writer(file)
            # Agrega la fila con error al archivo CSV
            writer.writerow(row.values())
    #print('creado o guardado: ', item)

from django.db import transaction

import sys
import time
from django.db import transaction

def crear_o_actualizar_registros_en_lotes(rows, tamaño_lote):
    for i in range(0, len(rows), tamaño_lote):
        lote = rows[i:i+tamaño_lote]
        items_para_actualizar = []
        inicio = time.time()  # Inicio del temporizador
        uso_memoria_inicial = sum(sys.getsizeof(i) for i in items_para_actualizar)
        with transaction.atomic():
            for row in lote:
                # Si la fila contiene algún valor None o vacío, la saltamos
                if any(value is None or value == '' or value == '           ' for key, value in row.items() if key not in ['sub_carpeta', 'sub_titulo']):
                    continue
                try:
                    # Recuperar o crear una instancia de Sub_Carpeta
                    sub_carpeta_nombre = row.pop('sub_carpeta')
                    sub_carpeta, created = Sub_Carpeta.objects.get_or_create(nombre=sub_carpeta_nombre)
                    row['sub_carpeta'] = sub_carpeta
                    # Recuperar o crear una instancia de Sub_Titulo
                    sub_titulo_nombre = row.pop('sub_titulo')
                    sub_titulo, created = Sub_Titulo.objects.get_or_create(nombre=sub_titulo_nombre)
                    row['sub_titulo'] = sub_titulo
                    if row['final_efectivo'] <= 0:
                        row['final_efectivo'] = row['final']
                except:
                    pass
                try:
                    item, created = Item.objects.get_or_create(codigo=row['codigo'], defaults=row)
                    if not created:
                        for key, value in row.items():
                            setattr(item, key, value)
                    if item.final_efectivo <= 0:
                        item.final_efectivo = row['final']
                    item.marcar_actualizado()  # Cambiar el campo 'actualizado' a 1
                    item.descripcion = limpiar_texto(row['descripcion'])
                    items_para_actualizar.append(item)
                except Exception as e:
                    print('Error al intentar guardar: ', row['codigo'], flush=True)
                    print(e, flush=True)
            # Asume que 'items_para_actualizar' es una lista de tus instancias de modelo
            Item.objects.bulk_update(items_para_actualizar, [field.name for field in Item._meta.fields if field.name != Item._meta.pk.name])

        fin = time.time()  # Fin del temporizador
        uso_memoria_final = sum(sys.getsizeof(i) for i in items_para_actualizar)
        print(f"Tiempo de ejecución: {fin - inicio} segundos")
        print(f"Uso de memoria: {uso_memoria_final - uso_memoria_inicial} bytes")

def desactualizar_anteriores(filtro):
    Item.objects.filter(codigo__endswith=filtro).update(actualizado=False)

def buscar_modificar_registros(csv_file, filtro):
    # Cargar el archivo CSV
    desactualizar_anteriores(filtro)
    with open(csv_file, newline='', encoding='utf8') as csvfile:

        reader = csv.DictReader(csvfile)
        
        for row in reader:
            # Filtrar filas con valores nulos o vacíos
            if not (row['precio_base'] is None or row['precio_base'] == '' or row['precio_base'] == ' ' or row['precio_base'] == '-' or row['precio_base'] == '.' or row['precio_base'] == '#N/A' or row['precio_base'] == '#VALUE!'):
                
                crear_o_actualizar_registro(row)
    print('cargado: ', filtro, flush=True)

def buscar_modificar_registros_lotes(csv_file, filtro):
    # Cargar el archivo CSV
    desactualizar_anteriores(filtro)
    with open(csv_file, newline='', encoding='utf8') as csvfile:

        reader = csv.DictReader(csvfile)
        rows = []
        for row in reader:
            #print(row)
            # Filtrar filas con valores nulos o vacíos
            if not (row['precio_base'] is None or row['precio_base'] == '' or row['precio_base'] == ' ' or row['precio_base'] == '-' or row['precio_base'] == '.' or row['precio_base'] == '#N/A' or row['precio_base'] == '#VALUE!'):
                if validar_digitos_str(row['precio_base']):
                    if validar_digitos_str(row['final']):
                        row['final'] = custom_round(float(row['final']))
                    if validar_digitos_str(row['final_efectivo']):
                        row['final_efectivo'] = custom_round(float(row['final_efectivo']))
                rows.append(row)
        crear_o_actualizar_registros_en_lotes(rows, 10000)
    print('cargado: ', filtro, flush=True)
    
def principal_csv():
    patoba = Patoba(None)
    
    proveedores = ListaProveedores.objects.filter(hay_csv_pendiente=True)
    #proveedores = ListaProveedores.objects.all()
    for proveedor in proveedores:
        print(f"Actualizando registros de {proveedor.nombre}")
        ruta_csv = os.path.join(const.BASE_DIR, f'{proveedor.nombre}.csv')
        abreviatura = proveedor.abreviatura
        id_archivo_plantilla = patoba.obtener_id_por_nombre(
            proveedor.nombre, const.PLANTILLAS)
        try:
            # Obtener los datos de la hoja de cálculo
            result = patoba.sheet_service.spreadsheets().values().get(
                spreadsheetId=id_archivo_plantilla, range='BDD').execute()
            values = result.get('values', [])

            # Guardar los datos en un archivo CSV
            with open(ruta_csv, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(values)
            
        except Exception as e:
            print("No se encontro BDD")
            print(e)
           
        try: 
            buscar_modificar_registros_lotes(ruta_csv, abreviatura)
        except Exception as e:
            print("Error al buscar y modificar registros...")
            print(e)
        
        lista_proveedor = ListaProveedores.objects.get(nombre=proveedor.nombre)
        lista_proveedor.hay_csv_pendiente = False
        lista_proveedor.save()
        
        carteles = Carteles.objects.filter(proveedor=proveedor.id)
        carteles_cajon = CartelesCajon.objects.filter(proveedor=proveedor.id)
        
        for cartel in carteles:
            cartel.revisar = True
            cartel.save()
        
        for cartel_cajon in carteles_cajon:
            cartel_cajon.revisar = True
            cartel_cajon.save()
        
    print("fin", flush=True)

def apply_custom_round(batch_size=10000):
    items = Item.objects.all()
    total_items = items.count()
    offset = 0

    while offset < total_items:
        batch = items[offset:offset + batch_size]
        for item in batch:
            item.final = custom_round(item.final)
            item.final_efectivo = custom_round(item.final_efectivo)
            item.final_rollo = custom_round(item.final_rollo)
            item.final_rollo_efectivo = custom_round(item.final_rollo_efectivo)

        Item.objects.bulk_update(batch, ['final', 'final_efectivo', 'final_rollo', 'final_rollo_efectivo'])
        offset += batch_size 
def mostrara_boletas(bool):
    from boletas.models import Boleta
    
    boletas = Boleta.objects.all()
    for b in boletas:
        b.impreso = bool
        b.save()

from django.contrib.auth.models import User

def reset(username, contraseña):
    u = User.objects.get(username=username)
    u.set_password(contraseña)
    u.save()

import csv

import csv
from django.db.models import Q

def filtrar_trabajados():
    # Obtener todos los proveedores
    proveedores = Proveedor.objects.all()

    for proveedor in proveedores:
        # Filtrar items por proveedor y si están trabajados
        filtrados = Item.objects.filter(Q(trabajado=True) & Q(proveedor=proveedor))

        # Crear un nombre de archivo único para cada proveedor
        filename = f'{proveedor.text_display}_trabajado.csv'

        # Abrir (o crear) el archivo CSV
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            # Crear un escritor CSV
            writer = csv.writer(csvfile)
            writer.writerow(['Codigo', 'Descripción', 'Stock', 'Carga Stock'])  # Ajusta los nombres de las columnas a tus campos

            # Escribir los datos de los items
            for item in filtrados:
                writer.writerow([item.codigo, item.descripcion, item.stock, ''])  # Ajusta los atributos a tus campos

from bdd.models import Proveedor

def asociar_proveedores():
    # Obtener todos los items y proveedores
    items = Item.objects.all()
    lista_proveedores = ListaProveedores.objects.all()

    # Crear un diccionario para mapear las abreviaturas a los proveedores
    abreviatura_a_lista_proveedores = {lp.abreviatura: lp for lp in lista_proveedores}

    # Lista para almacenar los items que necesitan ser actualizados
    items_para_actualizar = []

    for item in items:
        # Obtener la abreviatura del código del item
        abreviatura = '/' + item.codigo.split('/')[-1]

        # Buscar la lista de proveedores correspondiente
        lista_prov = abreviatura_a_lista_proveedores.get(abreviatura)

        if lista_prov:
            # Buscar el proveedor correspondiente
            proveedor = Proveedor.objects.get(identificador=lista_prov)

            if proveedor:
                # Asociar el item con el proveedor
                item.proveedor = proveedor
                items_para_actualizar.append(item)

    # Actualizar los items en la base de datos
    Item.objects.bulk_update(items_para_actualizar, ['proveedor'])

from bdd.classes import Patoba

if __name__ == "__main__":
    #reset(input("usuario"),input("contraseña"))
    #patoba = Patoba(None)
    #patoba.filtrar_trabajados()
    #asociar_proveedores()
    
    
    principal_csv()
    apply_custom_round()