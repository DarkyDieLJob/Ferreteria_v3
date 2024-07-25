from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload
#import pandas as pd
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime, timedelta
from django.conf import settings as const
import base64

def armar_tabla(id_carpeta_inbox, id_carpeta_plantillas, credentials):

    # Crear un objeto drive_service para interactuar con la API de Google Drive
    drive_service = build('drive', 'v3', credentials=credentials)

    # Obtener los archivos en la carpeta "Inbox"
    query = f"'{id_carpeta_inbox}' in parents and trashed = false"
    results = drive_service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute()
    items_inbox = results.get('files', [])

    # Obtener los archivos en la carpeta "Plantillas"
    query = f"'{id_carpeta_plantillas}' in parents and trashed = false"
    results = drive_service.files().list(
        q=query, fields="nextPageToken, files(id, name)").execute()
    items_plantillas = results.get('files', [])

    # Armar la tabla
    tabla = []
    lista_exclusion = ['Procesado de datos.ipynb',
                       'plantilla - Auxiliar', 'Plantilla',
                       'planti-lla - Auxiliar', 'Planti-lla']
    for item_inbox in items_inbox:
        # Mostrar las opciones de plantillas disponibles
        print(
            f'Selecciona la plantilla que deseas usar para el archivo {item_inbox["name"]}:')
        for i, item_plantilla in enumerate(items_plantillas):
            if item_plantilla["name"] in lista_exclusion:
                continue
            print(f'{i+1}. {item_plantilla["name"]}')

        # Obtener la selección del usuario
        seleccion = int(input('Ingresa el número de la plantilla: '))
        plantilla_seleccionada = items_plantillas[seleccion-1]['name']

        # Leer el archivo en "Inbox"
        file_id = item_inbox['id']
        request = drive_service.files().get_media(fileId=file_id)
        archivo_inbox = io.BytesIO()
        downloader = MediaIoBaseDownload(archivo_inbox, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        archivo_inbox.seek(0)
        archivo_proveedor = pd.read_excel(archivo_inbox, sheet_name=None)

        # Mostrar las opciones de hojas disponibles
        print(
            f'Selecciona la hoja que deseas procesar para el archivo {item_inbox["name"]}:')
        for i, hoja in enumerate(archivo_proveedor.keys()):
            print(f'{i+1}. {hoja}')

        # Obtener la selección del usuario
        seleccion = int(input('Ingresa el número de la hoja: '))
        hoja_seleccionada = list(archivo_proveedor.keys())[seleccion-1]

        tabla.append({
            'archivo_en_inbox': item_inbox['name'],
            'plantilla': plantilla_seleccionada,
            'hoja_seleccionada': hoja_seleccionada
        })

    return tabla



# ID de la carpeta en Google Drive donde se guardarán los archivos
folder_id = const.INBOX

# Diccionario con los nombres de archivo para cada remitente
file_names = {}


def get_emails(gmail_service, drive_service):
    # Obtener la fecha de ayer en formato RFC 3339
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y/%m/%d')
    result = gmail_service.users().messages().list(userId='me', labelIds=[
        'INBOX'], q=f'after:{yesterday}').execute()

    messages = result.get('messages')
    if messages is None:
        print('No se encontraron mensajes')
    else:
        for msg in messages:
            txt = gmail_service.users().messages().get(
                userId='me', id=msg['id']).execute()
            payload = txt['payload']
            headers = payload['headers']
            subject = next(
                (i['value'] for i in headers if i['name'] == 'Subject'), 'default_subject')
            sender = next((i['value'] for i in headers if i['name']
                           == 'From'), 'default_sender')
            parts = payload.get('parts')
            if parts:
                for part in parts:
                    filename = part.get('filename')
                    if filename.endswith('.xls') or filename.endswith('.xlsx') or filename.endswith('.XLS'):
                        if 'data' in part['body']:
                            data = part['body']['data']
                        else:
                            att_id = part['body']['attachmentId']
                            att = gmail_service.users().messages().attachments().get(
                                userId='me', messageId=msg['id'], id=att_id).execute()
                            data = att['data']
                        file_data = base64.urlsafe_b64decode(
                            data.encode('UTF-8'))
                        if 'carlosvimercati2@gmail.com' in sender or 'pyfpaoli@yahoo.com.ar' in sender or 'laferreteatrobarcultural@gmail.com' in sender:
                            file_name = subject
                        else:
                            file_name = file_names.get(sender, 'default_name')

                        file_metadata = {'name': file_name,
                                         'parents': [folder_id]}
                        media = MediaIoBaseUpload(io.BytesIO(
                            file_data), mimetype='application/vnd.ms-excel')

                        try:
                            # Buscar archivos con el mismo nombre en la carpeta especificada
                            print(f"Nombre: {file_name} e ID de carpeta: {folder_id}")
                            results = drive_service.files().list(q=f"name='{file_name}' and trashed = false and parents in '{folder_id}'").execute()
                            items = results.get('files', [])
                        except Exception as e:
                            print(f"No se encontro el archivo: {file_name}, en la carpeta Inbox de Google Drive")
                            print(e)
                            items = False

                        # Si se encuentra un archivo con el mismo nombre, eliminarlo
                        if items:
                            for item in items:
                                print(item)
                                print(f"Eliminando archivo con ID: {item['id']}")
                                #drive_service.files().delete(fileId=item['id']).execute()
                                #plantilla = Listado_Planillas.objects.filter(identificador=item['id']).delete()
                        else:
                            _ = drive_service.files().create(
                                body=file_metadata, media_body=media, fields='id').execute()
                        try:
                            gmail_service.users().messages().delete(userId='me', id=msg['id']).execute()
                        except Exception as e:
                            print("error al querer borar el email")
                            print(e)
