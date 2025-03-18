import time
from allauth.socialaccount.models import SocialToken
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
import io
from zipfile import ZipFile
from .models import Item, Proveedor
from django.db.models import Q
import pandas as pd
import os
from django.conf import settings

SCOPES = ["https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.file",
          'https://www.googleapis.com/auth/',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.compose',
          ]

class Patoba():
    def __init__(self, request) -> None:
        self.request = request
        if self.request == None:
            social_token = SocialToken.objects.get(account__user=1)
        else:
            print("Usuario: ",self.request.user)
            social_token = SocialToken.objects.get(account__user=self.request.user)
        self.credenciales = Credentials(
            token=social_token.token,
            refresh_token=social_token.token_secret,
            client_id=social_token.app.client_id,
            client_secret=social_token.app.secret,
            token_uri = "https://oauth2.googleapis.com/token",
        )
        self.gmail_service = build(
            'gmail', 'v1', credentials=self.credenciales)
        self.drive_service = build(
            'drive', 'v3', credentials=self.credenciales)
        self.sheet_service = build(
            'sheets', 'v4', credentials=self.credenciales)
        self.filtro_hojas_descarga = [
            'Reemplazable', 'Intermedio', 'BDD', 'Diccionario', 'Etiquetado',
        ]
    
        self.id_carpeta_pedidos = '1kkoTDNOCbWwzjmTzWOZPR3xVMUAYtYOj'
    
    def subir_sqlite3_a_drive(self, ruta_archivo, nombre_archivo, carpeta_id):
        """
        Sube o actualiza un archivo SQLite3 en Google Drive.

        Args:
            ruta_archivo (str): Ruta completa al archivo local.
            nombre_archivo (str): Nombre del archivo en Drive.
            carpeta_id (str): ID de la carpeta en Drive.
        """
        # Buscar el archivo existente
        query = f"name='{nombre_archivo}' and '{carpeta_id}' in parents and trashed=false"
        results = self.drive_service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])

        media = MediaFileUpload(ruta_archivo, mimetype='application/x-sqlite3', resumable=True)

        if files:
            # Actualizar el archivo existente
            file_id = files[0]['id']
            request = self.drive_service.files().update(fileId=file_id, media_body=media)
            file = request.execute()
            print(f'Archivo SQLite3 actualizado en Drive, ID: {file.get("id")}')
        else:
            # Crear un nuevo archivo
            file_metadata = {
                'name': nombre_archivo,
                'parents': [carpeta_id]
            }
            request = self.drive_service.files().create(body=file_metadata, media_body=media)
            file = request.execute()
            print(f'Archivo SQLite3 subido a Drive, ID: {file.get("id")}')
    
    def descargar_sqlite3_de_drive(self, nombre_archivo, carpeta_id, ruta_destino):
        """
        Descarga un archivo SQLite3 desde Google Drive.

        Args:
            nombre_archivo (str): Nombre del archivo en Drive.
            carpeta_id (str): ID de la carpeta en Drive.
            ruta_destino (str): Ruta completa donde guardar el archivo descargado.
        """
        # Buscar el archivo en Drive
        query = f"name='{nombre_archivo}' and '{carpeta_id}' in parents and trashed=false"
        results = self.drive_service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])

        if files:
            file_id = files[0]['id']
            request = self.drive_service.files().get_media(fileId=file_id)
            fh = io.FileIO(ruta_destino, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print(f"Descargando {int(status.progress() * 100)}%.")
            print(f'Archivo SQLite3 descargado a: {ruta_destino}')
        else:
            print(f'No se encontró el archivo SQLite3 "{nombre_archivo}" en Drive.')
        
    def crear_hoja_google_drive(self, nombre_libro, datos, libro_id=None):
        if libro_id is None:
            # Crear un nuevo libro de Google Sheets con el nombre especificado
            libro = self.sheet_service.spreadsheets().create(body={'properties': {'title': nombre_libro}}).execute()
            libro_id = libro['spreadsheetId']
        else:
            # Borrar el contenido de la hoja existente
            self.sheet_service.spreadsheets().values().clear(
                spreadsheetId=libro_id,
                range='A1:Z1000'  # Ajusta esto al rango que desees borrar
            ).execute()
            self.desaturar()

        # Escribir los datos en la hoja
        cuerpo = {
            'values': datos
        }
        rango = 'A1'
        self.sheet_service.spreadsheets().values().update(
            spreadsheetId=libro_id,
            range=rango,
            valueInputOption='RAW',
            body=cuerpo
        ).execute()
        self.desaturar()

        # Aplicar formato a las celdas
        requests = [
            # Agregar borde a las celdas
            {
                'updateBorders': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': len(datos),
                        'startColumnIndex': 0,
                        'endColumnIndex': len(datos[0])
                    },
                    'innerHorizontal': {
                        'style': 'SOLID',
                        'width': 1,
                        'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}
                    },
                    'innerVertical': {
                        'style': 'SOLID',
                        'width': 1,
                        'color': {'red': 0, 'green': 0, 'blue': 0, 'alpha': 1}
                    }
                }
            },
            # Ajustar el tamaño de la columna B
            {
                'updateDimensionProperties': {
                    'range': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 1,
                        'endIndex': 2
                    },
                    'properties': {
                        'pixelSize': 400  # Ajusta esto al tamaño deseado
                    },
                    'fields': 'pixelSize'
                }
            },
            # Centrar el texto en las columnas C y D
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': len(datos),
                        'startColumnIndex': 2,
                        'endColumnIndex': 4
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'horizontalAlignment': 'CENTER'
                        }
                    },
                    'fields': 'userEnteredFormat.horizontalAlignment'
                }
            }
        ]
        body = {
            'requests': requests
        }
        self.sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=libro_id,
            body=body
        ).execute()
        self.desaturar()

        # Mover el libro a la carpeta deseada
        archivo = self.drive_service.files().get(fileId=libro_id,
                                                fields='parents').execute()
        anterior_padre = ",".join(archivo.get('parents'))
        archivo = self.drive_service.files().update(fileId=libro_id,
                                                    addParents=self.id_carpeta_pedidos,
                                                    removeParents=anterior_padre,
                                                    fields='id, parents').execute()

        return libro_id




    def filtrar_trabajados(self):
        # Obtener todos los proveedores
        proveedores = Proveedor.objects.all()

        for proveedor in proveedores:
            # Filtrar items por proveedor y si están trabajados
            filtrados = Item.objects.filter(Q(trabajado=True) & Q(proveedor=proveedor)).order_by('codigo')

            # Preparar los datos para la hoja de Google Sheets
            datos = [['Codigo', 'Descripción', 'Stock', 'Carga Stock']]  # Ajusta los nombres de las columnas a tus campos

            # Agregar los datos de los items
            for item in filtrados:
                datos.append([item.codigo, item.descripcion, item.stock, ''])  # Ajusta los atributos a tus campos

            # Crear un nombre de hoja único para cada proveedor
            nombre_libro = f'{proveedor.text_display}_trabajado'

            # Obtener el ID del libro si ya existe
            libro_id = self.obtener_id_por_nombre(nombre_libro, self.id_carpeta_pedidos)

            # Crear o actualizar la hoja de Google Sheets
            self.crear_hoja_google_drive(nombre_libro, datos, libro_id)


    def desaturar(self):
        time.sleep(0.07)

    def listar(self, cant, id_carpeta):
        print("listar")
        query = f"'{id_carpeta}' in parents and trashed = false"
        resultado = self.drive_service.files().list(
            q=query, pageSize=cant, fields="nextPageToken, files(id,name)").execute()
        listado = resultado.get('files', [])
        self.desaturar()
        return listado

    def obtener_id_por_nombre(self, nombre_archivo, id_carpeta):
        try:
            query = f"mimeType!='application/vnd.google-apps.folder' and trashed = false and name='{nombre_archivo}' and parents in '{id_carpeta}'"
            results = self.drive_service.files().list(
                q=query, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
            self.desaturar()
            return items[0]['id']
        except Exception as e:
            print(
                f"No se encontró un archivo con el nombre {nombre_archivo} en la carpeta especificada")
            print(e)
            return None

    def copiar_reemplazable(self, id_archivo_proveedor, hoja_seleccionada, id_hoja_reemplazable, id_archivo_plantilla) -> None:
        """
        Copia el contenido de una hoja de cálculo de un archivo .xls o .xlsx alojado en Google Drive a una hoja de cálculo
        de un archivo de Google Sheets.

        :param id_archivo_proveedor: El ID del archivo .xls o .xlsx que contiene la hoja a copiar.
        :type id_archivo_proveedor: str
        :param hoja_seleccionada: El nombre de la hoja a copiar.
        :type hoja_seleccionada: str
        :param id_hoja_reemplazable: El ID de la hoja de destino en el archivo de Google Sheets.
        :type id_hoja_reemplazable: str
        :param id_archivo_plantilla: El ID del archivo de Google Sheets que contiene la hoja de destino.
        :type id_archivo_plantilla: str
        """
        # Descarga el archivo .xls o .xlsx
        request = self.drive_service.files().get_media(fileId=id_archivo_proveedor)
        xls_file = io.BytesIO()
        downloader = MediaIoBaseDownload(xls_file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()

        # Lee el contenido del archivo en un DataFrame
        xls_file.seek(0)
        df = pd.read_excel(xls_file, sheet_name=hoja_seleccionada).fillna("")

        # Convierte los datos del DataFrame a una lista de listas
        valores = [df.columns.values.tolist()] + df.values.tolist()

        # Ajusta el tamaño de la hoja de destino si es necesario
        sheet_properties = self.sheet_service.spreadsheets().get(spreadsheetId=id_archivo_plantilla).execute()['sheets']
        for sheet in sheet_properties:
            if sheet['properties']['sheetId'] == int(id_hoja_reemplazable):
                sheet_rows = sheet['properties']['gridProperties']['rowCount']
                break

        if len(valores) > sheet_rows:
            body = {
                'requests': [
                    {
                        'appendDimension': {
                            'sheetId': id_hoja_reemplazable,
                            'dimension': 'ROWS',
                            'length': len(valores) - sheet_rows
                        }
                    }
                ]
            }
            self.sheet_service.spreadsheets().batchUpdate(spreadsheetId=id_archivo_plantilla, body=body).execute()

        # Actualiza el contenido de la hoja de destino con los nuevos valores
        body = {
            'requests': [
                {
                    'updateCells': {
                        'range': {
                            'sheetId': id_hoja_reemplazable,
                            'startRowIndex': 0,
                            'startColumnIndex': 0,
                            'endRowIndex': len(valores),
                            'endColumnIndex': len(valores[0])
                        },
                        'rows': [{'values': [{'userEnteredValue': {'stringValue': str(c)}} for c in row]} for row in valores],
                        'fields': 'userEnteredValue'
                    }
                }
            ]
        }
        self.sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=id_archivo_plantilla, body=body).execute()

    def obtener_id_hoja_por_nombre(self, nombre_hoja, id_archivo):
        """
        Obtiene el ID de una hoja de cálculo de Google Sheets a partir de su nombre y el ID del archivo que la contiene.

        :param nombre_hoja: El nombre de la hoja de cálculo cuyo ID se desea obtener.
        :type nombre_hoja: str
        :param id_archivo: El ID del archivo que contiene la hoja de cálculo.
        :type id_archivo: str
        :return: El ID de la hoja de cálculo, o None si no se encuentra.
        :rtype: str or None
        """
        hojas = self.sheet_service.spreadsheets().get(
            spreadsheetId=id_archivo).execute().get('sheets', [])
        for hoja in hojas:
            if hoja['properties']['title'] == nombre_hoja:
                return hoja['properties']['sheetId']
        return None

    def obtener_g_sheet_por_id(self, id_archivo_plantilla):
        try:
            g_sheet = self.sheet_service.spreadsheets().get(
                spreadsheetId=id_archivo_plantilla).execute()
            self.desaturar()
        except:
            print(
                f"No se encontro un archivo con el ID: {id_archivo_plantilla}")
            g_sheet = None
        return g_sheet

    def copiar_hoja(self, id_hoja, id_archivo, id_archivo_destino):
        response = self.sheet_service.spreadsheets().sheets().copyTo(
            spreadsheetId=id_archivo,
            sheetId=id_hoja,
            body={
                'destinationSpreadsheetId': id_archivo_destino
            }
        ).execute()
        self.desaturar()
        id_hoja_copiada = response['sheetId']
        titulo_hoja_copiada = response['title']
        return id_hoja_copiada, titulo_hoja_copiada

    def eliminar_hoja(self, id_hoja, id_archivo):
        self.sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=id_archivo,
            body={
                'requests': [
                    {
                        'deleteSheet': {
                            'sheetId': id_hoja
                        }
                    }
                ]
            }
        ).execute()
        self.desaturar()

    def renombrar_hoja(self, id_hoja, id_archivo, nuevo_nombre):
        self.sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=id_archivo,
            body={
                'requests': [
                    {
                        'updateSheetProperties': {
                            'properties': {
                                'sheetId': id_hoja,
                                'title': nuevo_nombre
                            },
                            'fields': 'title'
                        }
                    }
                ]
            }
        ).execute()
        self.desaturar()

    def buscar_copia_por_nombre(self, id_archivo, id_carpeta):
        # Obtener el nombre del archivo y buscar si ya existe un archivo con el mismo nombre en la carpeta destino
        archivo = self.drive_service.files().get(fileId=id_archivo).execute()
        query = f"name='{archivo['name']}' and mimeType='application/vnd.google-apps.spreadsheet' and trashed=false and parents in '{id_carpeta}'"
        response = self.drive_service.files().list(q=query).execute()
        files = response.get('files', [])
        return archivo, files

    def actualizar_contenido_copiar(self, id_hoja_entrante, valores, id_hoja_archivo):
        """
        Actualiza el contenido de una hoja de cálculo de Google Sheets con nuevos valores.

        :param id_hoja_entrante: El ID de la hoja de cálculo a actualizar.
        :type id_hoja_entrante: str
        :param valores: Una lista de listas que contiene los nuevos valores para la hoja de cálculo.
        :type valores: list[list]
        :param id_hoja_archivo: El ID de la hoja de cálculo que contiene la hoja a actualizar.
        :type id_hoja_archivo: str
        """
        # Ajusta el tamaño de la hoja de destino si es necesario
        sheet_properties = self.sheet_service.spreadsheets().get(spreadsheetId=id_hoja_archivo).execute()['sheets']
        for sheet in sheet_properties:
            if sheet['properties']['sheetId'] == int(id_hoja_entrante):
                sheet_rows = sheet['properties']['gridProperties']['rowCount']
                sheet_columns = sheet['properties']['gridProperties']['columnCount']
                break

        requests = []
        if len(valores) > sheet_rows:
            requests.append({
                'appendDimension': {
                    'sheetId': id_hoja_entrante,
                    'dimension': 'ROWS',
                    'length': len(valores) - sheet_rows
                }
            })
        if len(valores[0]) > sheet_columns:
            requests.append({
                'appendDimension': {
                    'sheetId': id_hoja_entrante,
                    'dimension': 'COLUMNS',
                    'length': len(valores[0]) - sheet_columns
                }
            })
        if requests:
            body = {'requests': requests}
            self.sheet_service.spreadsheets().batchUpdate(spreadsheetId=id_hoja_archivo, body=body).execute()

        # Actualiza el contenido de la hoja de destino con los nuevos valores
        body = {
            'requests': [
                {
                    'updateCells': {
                        'range': {
                            'sheetId': id_hoja_entrante,
                            'startRowIndex': 0,
                            'startColumnIndex': 0,
                            'endRowIndex': len(valores),
                            'endColumnIndex': len(valores[0])
                        },
                        'rows': [{'values': [{'userEnteredValue': {'stringValue': c}} for c in row]} for row in valores],
                        'fields': 'userEnteredValue'
                    }
                }
            ]
        }
        self.sheet_service.spreadsheets().batchUpdate(
            spreadsheetId=id_hoja_archivo, body=body).execute()

    def crear_hoja_por_nombre(self, id_hoja, nombre):
        print("nombre: ",nombre)
        nueva_hoja = self.sheet_service.spreadsheets().batchUpdate(spreadsheetId=id_hoja, body={
            'requests': [
                {
                    'addSheet': {
                        'properties': {
                            'title': nombre
                        }
                    }
                }
            ]
        }).execute()['replies'][0]['addSheet']['properties']
        self.desaturar()
        return nueva_hoja

    def crear_buscar_copia_descarga(self, id_archivo, id_carpeta):
        archivo, files = self.buscar_copia_por_nombre(id_archivo, id_carpeta)

        if len(files) > 0:
            # Si ya existe un archivo con el mismo nombre, actualizar su contenido
            copia_id = files[0]['id']
            hojas_copia = self.sheet_service.spreadsheets().get(
                spreadsheetId=copia_id).execute()['sheets']
            hojas_copia_dict = {hoja['properties']
                                ['title']: hoja for hoja in hojas_copia}
        else:
            # Si no existe un archivo con el mismo nombre, crear una copia
            copia = self.drive_service.files().copy(fileId=id_archivo, body={
                'name': archivo['name'],
                'parents': [id_carpeta]
            }).execute()
            copia_id = copia['id']
            hojas_copia_dict = {}

        # Obtener todas las hojas del archivo original
        hojas = self.sheet_service.spreadsheets().get(
            spreadsheetId=id_archivo).execute()['sheets']

        # Filtrar las hojas para excluir las que están en la lista de filtro
        hojas = [hoja for hoja in hojas if hoja['properties']['title'] not in self.filtro_hojas_descarga]

        # Recorrer todas las hojas y copiar sus valores al archivo destino
        for hoja in hojas:
            rango = f"{hoja['properties']['title']}!A1:Z"
            valores = self.sheet_service.spreadsheets().values().get(
                spreadsheetId=id_archivo, range=rango).execute()['values']
            if hoja['properties']['title'] in hojas_copia_dict:
                # Si ya existe una hoja con el mismo nombre, actualizar su contenido
                nueva_hoja_id = hojas_copia_dict[hoja['properties']
                                                 ['title']]['properties']['sheetId']
                self.actualizar_contenido_copiar(
                    nueva_hoja_id, valores, copia_id)
            else:
                # Si no existe una hoja con el mismo nombre, crear una nueva
                nueva_hoja = self.crear_hoja_por_nombre(
                    copia_id, hoja['properties']['title'])
                nueva_hoja_id = nueva_hoja['sheetId']
                self.actualizar_contenido_copiar(
                    nueva_hoja_id, valores, copia_id)
        '''
        # Eliminar las hojas que no existen en el archivo original
        for _, hoja in hojas_copia_dict.items():
            try:
                self.eliminar_hoja(hoja['properties']['sheetId'], copia_id)
            except:
                pass'''

    def download_and_zip_files(self, files_dict):
        # Crear un objeto ZipFile en memoria
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            # Recorrer el diccionario de archivos
            for file_name, file_id in files_dict.items():
                # Descargar el archivo de Google Drive en formato .xls
                file = self.drive_service.files().get(fileId=file_id).execute()
                mime_type = file.get('mimeType')
                if mime_type == 'application/vnd.google-apps.document':
                    # Exportar como documento de Microsoft Word
                    request = self.drive_service.files().export(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                elif mime_type == 'application/vnd.google-apps.spreadsheet':
                    # Exportar como hoja de cálculo de Microsoft Excel
                    request = self.drive_service.files().export(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                else:
                    # Descargar el archivo directamente
                    request = self.drive_service.files().get_media(fileId=file_id)
                xls_buffer = io.BytesIO()
                downloader = MediaIoBaseDownload(xls_buffer, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()

                # Cargar el archivo .xls con pandas
                xls_buffer.seek(0)
                xls_data = pd.read_excel(xls_buffer, sheet_name=None)
                print("Cargar el archivo .xls con pandas")

                xls_buffer.seek(0)

                # Guardar el archivo .xls con pandas
                with pd.ExcelWriter(xls_buffer, engine='xlsxwriter') as writer:
                    for sheet_name, df in xls_data.items():
                        df = df.fillna("")
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

                # Agregar el archivo .xls al archivo zip
                xls_buffer.seek(0)
                zip_file.writestr(f'{file_name}.xlsx', xls_buffer.read())


        # Obtener el contenido del archivo zip
        zip_buffer.seek(0)
        zip_content = zip_buffer.read()

        # Retornar el contenido del archivo zip
        return zip_content

    def actualizar_plantilla(self, spreadsheets, sp):
        import requests
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        filtros = ['Reemplazable','Intermedio','Diccionario','Etiquetado','BDD']


        # Exporta la hoja de cálculo como un archivo xlsx
        export_url = f'https://docs.google.com/spreadsheets/d/{spreadsheets["spreadsheetId"]}/export?format=xlsx'
        response = requests.get(export_url, headers={'Authorization': f'Bearer {self.credenciales.token}'})
        xlsx_data = response.content

        file_name = f'{spreadsheets["properties"]["title"]}.xlsx'

        try:
            file_path = os.path.join(settings.MEDIA_ROOT, 'descargas', file_name)

            if default_storage.exists(file_path):
                default_storage.delete(file_path)
        except:
            file_path = f'/Users/DarkyDieL/Documents/GitHub/pagina-pf-paoli/media/descargas/{file_name}'

            if default_storage.exists(file_path):
                default_storage.delete(file_path)

        default_storage.save(file_path, ContentFile(xlsx_data))

        # Lee todas las hojas del archivo xlsx
        xlsx_file = pd.read_excel(file_path, sheet_name=None)

        try:
            # Crea un objeto ExcelWriter para guardar en formato xlsx
            file_path_xlsx = os.path.join(settings.MEDIA_ROOT, 'descargas', f"{spreadsheets['properties']['title']}-{sp.fecha}.xlsx")
            if default_storage.exists(file_path_xlsx):
                default_storage.delete(file_path_xlsx)
            xlsx_writer = pd.ExcelWriter(file_path_xlsx)
        except:
            # Crea un objeto ExcelWriter para guardar en formato xls
            file_path_xlsx = f'/Users/DarkyDieL/Documents/GitHub/pagina-pf-paoli/media/descargas/{spreadsheets["properties"]["title"]}-{sp.fecha}.xlsx'
            if default_storage.exists(file_path_xlsx): #<-- File "/home/darkydiel/mysite/bdd/gestor_google.py", line 533
                default_storage.delete(file_path_xlsx)
            xlsx_writer = pd.ExcelWriter(file_path_xlsx)

        try:
            # Crea un objeto ExcelWriter para guardar en formato ods
            file_path_ods = os.path.join(settings.MEDIA_ROOT, 'descargas', f"{spreadsheets['properties']['title']}-{sp.fecha}.ods")
            if default_storage.exists(file_path_ods):
                default_storage.delete(file_path_ods)
            ods_writer = pd.ExcelWriter(file_path_ods, engine='odf')
        except:
            # Crea un objeto ExcelWriter para guardar en formato ods
            file_path_ods = f'/Users/DarkyDieL/Documents/GitHub/pagina-pf-paoli/media/descargas/{spreadsheets["properties"]["title"]}-{sp.fecha}.ods'
            if default_storage.exists(file_path_ods):
                default_storage.delete(file_path_ods)
            ods_writer = pd.ExcelWriter(file_path_ods, engine='odf')

        # Itera sobre las hojas del archivo xlsx
        for sheet_name, df in xlsx_file.items():
            if sheet_name in filtros:
                if sheet_name == 'BDD':
                    continue
                continue
            else:
                # Guarda la hoja en formato xlsx
                df.to_excel(xlsx_writer, sheet_name=sheet_name, index=False)

                # Guarda la hoja en formato ods
                df.to_excel(ods_writer, sheet_name=sheet_name, index=False)

        # Guarda los archivos xls y ods
        xlsx_writer.close()
        ods_writer.close()


        try:
            # Genera un enlace de descarga para el archivo xlsx y lo guarda en sp.link_descarga
            sp.link_descarga = f'media/descargas/{spreadsheets["properties"]["title"]}-{sp.fecha}.xlsx'
            sp.link_descarga_ods = f'media/descargas/{spreadsheets["properties"]["title"]}-{sp.fecha}.ods'
            sp.descargar = True
            sp.save()
        except:
            print("no se encontro {} en Listado_Plantillas".format(spreadsheets["spreadsheetId"]))

    def borrar_por_id(self, id):
        # Elimina el archivo
        self.drive_service.files().delete(fileId=id).execute()
