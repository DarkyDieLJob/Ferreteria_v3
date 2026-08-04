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
    
    # Extraer solo el email si viene con formato "Name <email@domain>"
    import re
    email_match = re.search(r'<([^>]+)>', email)
    if email_match:
        email = email_match.group(1)
    
    # Extraer parte antes del @
    local_part = email.split("@")[0]
    
    # Eliminar números y caracteres especiales comunes
    name = re.sub(r'[0-9_\-\.]', ' ', local_part)
    
    # Capitalizar palabras
    name = ' '.join(word.capitalize() for word in name.split())
    
    return name if name else "default_name"

def extract_email_address(from_header):
    """Extrae solo la dirección de email de un header 'From'.
    Ej: 'Carlos Vimercati <carlosvimercati2@gmail.com>' -> 'carlosvimercati2@gmail.com'
    """
    if not from_header:
        return ""
    import re
    email_match = re.search(r'<([^>]+)>', from_header)
    if email_match:
        return email_match.group(1).lower().strip()
    # Si no tiene formato Name <email>, devolver tal cual
    return from_header.lower().strip()

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


def _extraer_attachments(parts, msg_id, gmail_service):
    """Recorre recursivamente las partes del email buscando attachments Excel.
    Retorna lista de (filename, file_data) para cada attachment valido.
    """
    attachments = []
    if not parts:
        return attachments
    for part in parts:
        filename = part.get("filename")
        # Skip partes sin filename o con filename vacio
        if not filename:
            # Si la parte tiene sub-partes (nested multipart), recorrerlas
            sub_parts = part.get("parts")
            if sub_parts:
                attachments.extend(
                    _extraer_attachments(sub_parts, msg_id, gmail_service)
                )
            continue
        # Verificar extension de forma segura (case-insensitive)
        if not filename.lower().endswith((".xls", ".xlsx")):
            continue
        try:
            if "data" in part["body"]:
                data = part["body"]["data"]
            else:
                att_id = part["body"]["attachmentId"]
                att = (
                    gmail_service.users()
                    .messages()
                    .attachments()
                    .get(userId="me", messageId=msg_id, id=att_id)
                    .execute()
                )
                data = att["data"]
            file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))
            attachments.append((filename, file_data))
        except Exception as e:
            logger.error("Error al descargar attachment '%s' del msg %s: %s", filename, msg_id, e)
    return attachments


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
        return

    logger.info("Se encontraron %d mensajes para procesar.", len(messages))
    for msg in messages:
        try:
            txt = (
                gmail_service.users()
                .messages()
                .get(userId="me", id=msg["id"])
                .execute()
            )
            payload = txt["payload"]
            headers = payload.get("headers", [])
            subject = next(
                (i["value"] for i in headers if i["name"] == "Subject"),
                "default_subject",
            )
            sender = next(
                (i["value"] for i in headers if i["name"] == "From"), "default_sender"
            )
            parts = payload.get("parts")
            if not parts:
                logger.debug("Mensaje %s sin partes, saltando.", msg["id"])
                continue

            # Extraer attachments recursivamente (manja nested multipart)
            attachments = _extraer_attachments(parts, msg["id"], gmail_service)
            if not attachments:
                logger.debug("Mensaje %s sin attachments Excel, saltando.", msg["id"])
                continue

            for filename, file_data in attachments:
                # Determinar el nombre del archivo según el remitente
                sender_email = extract_email_address(sender)

                # Buscar coincidencia exacta en el mapeo
                if sender_email in EMAIL_NAME_MAPPING:
                    rule = EMAIL_NAME_MAPPING[sender_email]
                    if rule == "subject":
                        file_name = clean_subject(subject)
                    elif rule == "email_name":
                        file_name = extract_name_from_email(sender)
                    else:
                        file_name = rule  # Nombre fijo
                else:
                    # Fallback: intentar extraer nombre del email
                    file_name = extract_name_from_email(sender)

                logger.info("Email de %s -> archivo: %s (attachment original: %s)", sender, file_name, filename)

                file_metadata = {"name": file_name, "parents": [folder_id]}
                media = MediaIoBaseUpload(
                    io.BytesIO(file_data), mimetype="application/vnd.ms-excel"
                )

                try:
                    # Buscar archivos con el mismo nombre en la carpeta especificada
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
                    items = []

                if items:
                    # Eliminar archivos duplicados y subir el nuevo
                    for item in items:
                        logger.info("Archivo duplicado detectado id=%s name=%s, eliminando para reemplazar.", item.get('id'), item.get('name'))
                        try:
                            drive_service.files().delete(fileId=item['id']).execute()
                        except Exception as del_e:
                            logger.error("Error al eliminar archivo duplicado id=%s: %s", item.get('id'), del_e)
                    # Subir el nuevo archivo
                    try:
                        _ = (
                            drive_service.files()
                            .create(
                                body=file_metadata, media_body=media, fields="id"
                            )
                            .execute()
                        )
                        logger.info("Archivo '%s' subido a Drive (reemplazo de duplicado).", file_name)
                    except Exception as up_e:
                        logger.error("Error al subir archivo '%s' despues de eliminar duplicado: %s", file_name, up_e)
                else:
                    try:
                        _ = (
                            drive_service.files()
                            .create(
                                body=file_metadata, media_body=media, fields="id"
                            )
                            .execute()
                        )
                        logger.info("Archivo '%s' subido a Drive (nuevo).", file_name)
                    except Exception as up_e:
                        logger.error("Error al subir archivo '%s' a Drive: %s", file_name, up_e)
        except Exception as e:
            logger.error("Error al procesar mensaje id=%s: %s", msg.get("id", "?"), e)
            logger.exception(e)
            continue
