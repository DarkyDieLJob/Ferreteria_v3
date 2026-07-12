from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload

# import pandas as pd
from googleapiclient.http import MediaIoBaseUpload
from datetime import datetime, timedelta
from django.conf import settings as const
import base64
import logging

logger = logging.getLogger(__name__)


def armar_tabla(id_carpeta_inbox, id_carpeta_plantillas, credentials):

    # Crear un objeto drive_service para interactuar con la API de Google Drive
    drive_service = build("drive", "v3", credentials=credentials)

    # Obtener los archivos en la carpeta "Inbox"
    query = f"'{id_carpeta_inbox}' in parents and trashed = false"
    results = (
        drive_service.files()
        .list(q=query, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items_inbox = results.get("files", [])

    # Obtener los archivos en la carpeta "Plantillas"
    query = f"'{id_carpeta_plantillas}' in parents and trashed = false"
    results = (
        drive_service.files()
        .list(q=query, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items_plantillas = results.get("files", [])

    # Armar la tabla
    tabla = []
    lista_exclusion = [
        "Procesado de datos.ipynb",
        "plantilla - Auxiliar",
        "Plantilla",
        "planti-lla - Auxiliar",
        "Planti-lla",
    ]
    for item_inbox in items_inbox:
        # Mostrar las opciones de plantillas disponibles
        logger.info(
            "Selecciona la plantilla que deseas usar para el archivo %s:", item_inbox["name"]
        )
        for i, item_plantilla in enumerate(items_plantillas):
            if item_plantilla["name"] in lista_exclusion:
                continue
            logger.debug("%s. %s", i + 1, item_plantilla["name"]) 

        # Obtener la selección del usuario
        seleccion = int(input("Ingresa el número de la plantilla: "))
        plantilla_seleccionada = items_plantillas[seleccion - 1]["name"]

        # Leer el archivo en "Inbox"
        file_id = item_inbox["id"]
        request = drive_service.files().get_media(fileId=file_id)
        archivo_inbox = io.BytesIO()
        downloader = MediaIoBaseDownload(archivo_inbox, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        archivo_inbox.seek(0)
        archivo_proveedor = pd.read_excel(archivo_inbox, sheet_name=None)

        # Mostrar las opciones de hojas disponibles
        logger.info(
            "Selecciona la hoja que deseas procesar para el archivo %s:", item_inbox["name"]
        )
        for i, hoja in enumerate(archivo_proveedor.keys()):
            logger.debug("%s. %s", i + 1, hoja)

        # Obtener la selección del usuario
        seleccion = int(input("Ingresa el número de la hoja: "))
        hoja_seleccionada = list(archivo_proveedor.keys())[seleccion - 1]

        tabla.append(
            {
                "archivo_en_inbox": item_inbox["name"],
                "plantilla": plantilla_seleccionada,
                "hoja_seleccionada": hoja_seleccionada,
            }
        )

    return tabla


# ID de la carpeta en Google Drive donde se guardarán los archivos
folder_id = const.INBOX

# Configuración de mapeo de remitentes a nombres de archivo
# Formato: {patrón_email: regla_nombre}
# regla puede ser: "subject" (usar asunto), "email_name" (extraer de email), o un string fijo
EMAIL_NAME_MAPPING = {
    # Emails que usan el subject del email
    "carlosvimercati2@gmail.com": "subject",
    "pyfpaoli@yahoo.com.ar": "subject",
    "laferreteatrobarcultural@gmail.com": "subject",
    
    # Mapeo directo de email a nombre
    "magliasrl1@gmail.com": "Maglia",
    
    # Puedes agregar más mapeos aquí
}

def extract_name_from_email(email):
    """Extrae el nombre base de una dirección de email."""
    if not email:
        return "default_name"
    
    # Extraer parte antes del @
    local_part = email.split("@")[0]
    
    # Eliminar números y caracteres especiales comunes
    import re
    name = re.sub(r'[0-9_\-\.]', ' ', local_part)
    
    # Capitalizar palabras
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name if name else "default_name"

def clean_subject(subject):
    """Limpia el subject del email para usar como nombre de archivo."""
    if not subject:
        return "default_name"
    
    # Eliminar caracteres inválidos para nombres de archivo
    import re
    cleaned = re.sub(r'[<>:"/\\|?*]', '', subject)
    
    # Limitar longitud (máximo 100 caracteres)
    cleaned = cleaned[:100].strip()
    
    return cleaned if cleaned else "default_name"


def get_emails(gmail_service, drive_service):
    # Obtener la fecha de ayer en formato RFC 3339
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y/%m/%d")
    result = (
        gmail_service.users()
        .messages()
        .list(userId="me", labelIds=["INBOX"], q=f"after:{yesterday}")
        .execute()
    )

    messages = result.get("messages")
    if messages is None:
        logger.info("No se encontraron mensajes")
    else:
        for msg in messages:
            txt = (
                gmail_service.users()
                .messages()
                .get(userId="me", id=msg["id"])
                .execute()
            )
            payload = txt["payload"]
            headers = payload["headers"]
            subject = next(
                (i["value"] for i in headers if i["name"] == "Subject"),
                "default_subject",
            )
            sender = next(
                (i["value"] for i in headers if i["name"] == "From"), "default_sender"
            )
            parts = payload.get("parts")
            if parts:
                for part in parts:
                    filename = part.get("filename")
                    if (
                        filename.endswith(".xls")
                        or filename.endswith(".xlsx")
                        or filename.endswith(".XLS")
                    ):
                        if "data" in part["body"]:
                            data = part["body"]["data"]
                        else:
                            att_id = part["body"]["attachmentId"]
                            att = (
                                gmail_service.users()
                                .messages()
                                .attachments()
                                .get(userId="me", messageId=msg["id"], id=att_id)
                                .execute()
                            )
                            data = att["data"]
                        file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
                        
                        # Determinar el nombre del archivo según el remitente
                        file_name = None
                        sender_lower = sender.lower()
                        
                        # Buscar coincidencia exacta en el mapeo
                        if sender_lower in EMAIL_NAME_MAPPING:
                            rule = EMAIL_NAME_MAPPING[sender_lower]
                            if rule == "subject":
                                file_name = clean_subject(subject)
                            elif rule == "email_name":
                                file_name = extract_name_from_email(sender)
                            else:
                                file_name = rule  # Nombre fijo
                        else:
                            # Fallback: intentar extraer nombre del email
                            file_name = extract_name_from_email(sender)
                        
                        logger.info(f"Email de {sender} -> archivo: {file_name}")

                        file_metadata = {"name": file_name, "parents": [folder_id]}
                        media = MediaIoBaseUpload(
                            io.BytesIO(file_data), mimetype="application/vnd.ms-excel"
                        )

                        try:
                            # Buscar archivos con el mismo nombre en la carpeta especificada
                            logger.debug("Verificando existencia previa: nombre=%s, folder_id=%s", file_name, folder_id)
                            results = (
                                drive_service.files()
                                .list(
                                    q=f"name='{file_name}' and trashed = false and parents in '{folder_id}'"
                                )
                                .execute()
                            )
                            items = results.get("files", [])
                        except Exception as e:
                            logger.warning(
                                "No se encontro el archivo en Inbox de Drive: nombre=%s, error=%s",
                                file_name,
                                e,
                            )
                            items = False

                        # Si se encuentra un archivo con el mismo nombre, eliminarlo
                        if items:
                            for item in items:
                                logger.info("Archivo duplicado detectado id=%s name=%s (no eliminado)", item.get('id'), item.get('name'))
                                # drive_service.files().delete(fileId=item['id']).execute()
                                # plantilla = Listado_Planillas.objects.filter(identificador=item['id']).delete()
                        else:
                            _ = (
                                drive_service.files()
                                .create(
                                    body=file_metadata, media_body=media, fields="id"
                                )
                                .execute()
                            )
                        # Comentado: Eliminación de emails deshabilitada por falta de scopes
                        # try:
                        #     gmail_service.users().messages().delete(
                        #         userId="me", id=msg["id"]
                        #     ).execute()
                        # except Exception as e:
                        #     logger.error("Error al querer borrar el email: %s", e)
