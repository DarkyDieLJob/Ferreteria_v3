from django.shortcuts import render
from bdd.views import MiVista, MyForm
from bdd.classes import Patoba
from bdd.models import Listado_Planillas, Proveedor
from .task import recolectar_procesar, actualizar
from core_config.celery import app
import io
from googleapiclient.http import MediaIoBaseDownload
import os
from django.conf import settings
from django.db.models import Max
import pandas as pd

# Create your views here.

class Actualizar(MiVista):
    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)
        self.context['lista_html'] = ['actualizar.html',]


        patoba = Patoba(request=self.request)
        self.drive_service = patoba.drive_service
        print("detectando: ", self.request.path)

        datos = Listado_Planillas.objects.filter(listo=False, descargar=False)


        hojas_por_item = []

        for dato in datos:
            sheet_names = ["",]
            # Descargar el archivo de Excel desde Google Drive
            request = self.drive_service.files().get_media(fileId=dato.identificador)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            # Leer el contenido del archivo de Excel
            file.seek(0)
            try:
                #pd = "x"
                xls = pd.read_excel(file, sheet_name=None)

                # Obtener los nombres de las hojas
                sheet_names.extend(xls.keys())
                hojas_por_item.append(sheet_names)
            except Exception as e:
                print("error con pandas")
                print(e)
                hojas_por_item.append([])

        self.context['datos'] = datos#[::-1]
        self.context['hojas_por_item'] = hojas_por_item#[::-1]
        seleccion_planillas = Listado_Planillas.objects.filter(listo=True)
        self.context['seleccion_planillas'] = seleccion_planillas


        formulario = MyForm(model_name=self.context['model_name'],fields_to_show=self.context['lista_formulario_campos'])
        self.context['form'] = formulario
        self.context['seleccion_planillas'] = Listado_Planillas.objects.filter(listo=True, descargar=False)
        self.context['seleccion_descargar'] = Listado_Planillas.objects.filter(descargar=True)[::-1]


        # Obtén el archivo más reciente de cada proveedor
        latest_files = Listado_Planillas.objects.values('proveedor').annotate(latest_date=Max('fecha'))

        for latest_file in latest_files:
            # Obtén el proveedor y la fecha del archivo más reciente
            proveedor = latest_file['proveedor']
            latest_date = latest_file['latest_date']

            # Obtén todos los archivos de este proveedor que no sean el más reciente
            old_files = Listado_Planillas.objects.filter(proveedor=proveedor).exclude(fecha=latest_date)

            for old_file in old_files:
                # Construye la ruta al archivo físico
                file_path = os.path.join(settings.MEDIA_ROOT, 'descargas', f'{old_file.proveedor}-{old_file.fecha}.xlsx')
                file_path_ods = os.path.join(settings.MEDIA_ROOT, 'descargas', f'{old_file.proveedor}-{old_file.fecha}.ods')

                # Elimina el archivo físico si existe
                if os.path.isfile(file_path):
                    os.remove(file_path)
                if os.path.isfile(file_path_ods):
                    os.remove(file_path_ods)

                # Elimina el registro de la base de datos
                old_file.delete()
                
        for latest_file in latest_files:
            # Obtén el proveedor y la fecha del archivo más reciente
            proveedor = latest_file['proveedor']
            latest_date = latest_file['latest_date']

            # Elimina todos los archivos de este proveedor que no sean el más reciente
            Listado_Planillas.objects.filter(proveedor=proveedor).exclude(fecha=latest_date).delete()

        return self.context

    def get(self, request, *args, **kwargs):
        self.context = self.get_context_data()
        print("GET")
        print(self.request.GET)
        print(self.context['datos'])

        return self.render_to_response(self.context)

    def post(self, request, *args, **kwargs):
        self.context = self.get_context_data()
        print("POST")
        print(self.request.POST)
        print(self.context['seleccion_planillas'])

        print("Aqui ver que envia cada boton del formulario...")
        lista = ["tipo-boton",]
        for name in lista:
            print("{}: ".format(name), self.request.POST.get(name))
        
        if self.request.POST.get("tipo-boton") == "enviar":
            recolectar_procesar()
            #return JsonResponse({'task_id': task.id})

        if self.request.POST.get("tipo-boton") == "actualizar":
            actualizar()    

            
        print("actualizar_planillas: ",self.request.POST.get("actualizar_planillas"))

        if self.request.POST.get('actualizar_planillas')!='True':
            proveedor = []
            elementos_seleccionados = self.request.POST.getlist('elemento_seleccionado')
            proveedor = self.request.POST.getlist('proveedor')
            '''
            check = Listado_Planillas.objects.all()
            for c in check:
                c.listo=False
                c.save()'''
            for elemento in elementos_seleccionados:
                id, i = elemento.split(':')
                planilla = Listado_Planillas.objects.get(id=id)
                if i == "":
                    planilla.listo = False
                    planilla.save()
                    continue
                i = int(i)-1
                planilla.listo = True
                print("i: ",i,"planilla: ",planilla.listo)

                if proveedor[i]:
                    planilla.proveedor = Proveedor.objects.get(id=proveedor[i])
                else:
                    print("proveedor vacio")

                hoja = self.request.POST.get('hoja_{}'.format(id))
                if hoja != "":
                    planilla.hoja = hoja
                planilla.save()

            self.context['seleccion_planillas'] = Listado_Planillas.objects.filter(listo=True, descargar=False)
            print("seleccion: ",self.context['seleccion_planillas'])

        else:
            print("no entro aca, o si?")
            id_carpeta_inbox = cosnt.INBOX
            id_carpeta_plantillas = cosnt.PLANTILLAS
            id_carpeta_descargar = cosnt.DESCARGAR
            patoba = Patoba(request=self.request)

            # -Iterar sobre la tabla y procesar cada archivo
            ids = []
            ids_enviar = []
            mi_diccionario = {}
            ids = self.request.POST.getlist('seleccionados')


            ids_list = ast.literal_eval(ids[0])
            ids_enviar = [int(id) for id in ids_list]
            print("ids_enviar: ",ids_enviar)


            '''
            check = Listado_Planillas.objects.all()
            for c in check:
                c.listo=False
                c.save()'''
            seleccion_planillas = Listado_Planillas.objects.filter(id__in=ids_enviar)
            for sp in seleccion_planillas:
                nombre_proveedor = sp.descripcion
                nombre_plantilla = sp.proveedor
                nombre_descargable = "{}-{}".format(sp.proveedor,sp.fecha)
                hoja_seleccionada = sp.hoja

                print(nombre_proveedor, nombre_plantilla, nombre_descargable, hoja_seleccionada)

                id_archivo_proveedor = patoba.obtener_id_por_nombre(
                    nombre_proveedor, id_carpeta_inbox)

                id_archivo_plantilla = patoba.obtener_id_por_nombre(
                    nombre_plantilla, id_carpeta_plantillas)
                id_hoja_reemplazable = patoba.obtener_id_hoja_por_nombre(
                    "Reemplazable", id_archivo_plantilla)
                if id_archivo_proveedor:
                    request = patoba.drive_service.files().get_media(fileId=id_archivo_proveedor)
                    hoja_proveedor = io.BytesIO()
                    downloader = MediaIoBaseDownload(hoja_proveedor, request)
                    done = False
                    while done is False:
                        status, done = downloader.next_chunk()
                    hoja_proveedor.seek(0)
                    hoja_proveedor = pd.read_excel(
                        hoja_proveedor, sheet_name=None)
                else:
                    print(
                        f"No se encontró el archivo {nombre_proveedor}.xlsx en la carpeta Inbox")
                    hoja_proveedor = None

                print(type(hoja_proveedor))

                patoba.copiar_reemplazable(
                    id_archivo_proveedor, hoja_seleccionada, id_hoja_reemplazable, id_archivo_plantilla)

                patoba.crear_buscar_copia_descarga(id_archivo_plantilla, id_carpeta_descargar)
                identificador = patoba.obtener_id_por_nombre(nombre_plantilla, id_carpeta_descargar)

                print("nombre: {}, identificador: {}".format(nombre_descargable, identificador))
                mi_diccionario[str(nombre_descargable)] = str(identificador)

                sp.listo = True
                sp.save()
            print("diccionario: ",mi_diccionario)
            self.context['seleccion_planillas'] = Listado_Planillas.objects.filter(listo=True)


            if self.request.POST.get('descargar')=='True':
                # Descargar los archivos y crear el archivo zip
                zip_content = patoba.download_and_zip_files(mi_diccionario)
                # Crear una respuesta HTTP con el contenido del archivo zip
                response = HttpResponse(zip_content, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename=files.zip'

                # Retornar la respuesta HTTP
                return response



        ids_borrar = self.request.POST.getlist('seleccionado_borrar')
        Listado_Planillas.objects.filter(id__in=ids_borrar).delete()
        #context['datos'] = Item.objects.filter(id__in=ids)
        self.context['datos'] = Listado_Planillas.objects.filter(listo=False, descargar=False).reverse()
        return self.render_to_response(self.context)