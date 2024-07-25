import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'
import django
django.setup()

import csv
from django.apps import apps

def cargar_csv_a_modelo(ruta_csv, nombre_de_tu_app, nombre_modelo):
    Modelo = apps.get_model(nombre_de_tu_app, nombre_modelo)

    with open(ruta_csv, 'r', encoding='utf-8', errors='ignore') as archivo:
        lector = csv.reader(archivo, delimiter=';')
        encabezados = next(lector)
        print(encabezados)
        for fila in lector:
            datos = dict(zip(encabezados, fila))
            try:
                # Buscar un objeto existente por razon_social y cuit_dni
                modelo_objeto = Modelo.objects.get(
                    razon_social=datos['RazonSocial'],
                    cuit_dni=datos['CUIT']
                )
                # Actualizar los campos según corresponda
                modelo_objeto.responsabilidad_iva = datos['SituacionIVAKey']
                modelo_objeto.tipo_documento = datos['TipoDocumentoKey']
                modelo_objeto.domicilio = datos['Domicilio']
                modelo_objeto.telefono = datos['Telefono']
                modelo_objeto.save()
                print(f"Se actualizó el objeto existente: {modelo_objeto}")
            except Modelo.DoesNotExist:
                # Si no se encuentra, crear un nuevo objeto
                modelo_objeto = Modelo(
                    razon_social=datos['RazonSocial'],
                    cuit_dni=datos['CUIT'],
                    responsabilidad_iva=datos['SituacionIVAKey'],
                    tipo_documento=datos['TipoDocumentoKey'],
                    domicilio=datos['Domicilio'],
                    telefono=datos['Telefono']
                )
                modelo_objeto.save()
                print(f"Se creó un nuevo objeto: {modelo_objeto}")

if __name__ == '__main__':
    cargar_csv_a_modelo('bdd-clientes.csv', 'facturacion', 'Cliente')



