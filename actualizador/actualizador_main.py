import os
import io
import json
import csv
import time  # Import time for potential timestamps or delays
import logging

# Third-party imports
import pandas as pd
import openpyxl
from openpyxl.writer.excel import save_virtual_workbook
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from googleapiclient.errors import HttpError # Import HttpError

# Django imports
from django.conf import settings as const # Renamed to avoid conflict with logging.settings
from django.db import transaction # Import transaction for atomic operations
from asgiref.sync import sync_to_async # Assuming this is used elsewhere

# App imports (adjust paths if necessary)
from bdd.models import Listado_Planillas, Item, Sub_Carpeta, Sub_Titulo, ListaProveedores
from bdd.classes import Patoba
from bdd.funtions import get_emails # Assuming this function exists and works
from x_cartel.models import Carteles, CartelesCajon

# --- Logger Setup ---
logger = logging.getLogger(__name__)

# --- Utility Functions ---
# Remove registrar_log function entirely, use logger directly

# --- Database Operations (Refactored) ---

# Refactored version similar to the previous script
def crear_o_actualizar_registro(row_original):
    """Intenta crear o actualizar un registro Item basado en una fila de datos."""
    row = row_original.copy()
    codigo_item = row.get('codigo', 'N/A')
    logger.debug(f"Procesando registro individual para código: {codigo_item}")

    try:
        # 1. Obtener/Crear Sub_Carpeta
        sub_carpeta_nombre = row.pop('sub_carpeta', None)
        sub_carpeta = None
        if sub_carpeta_nombre:
            try:
                sub_carpeta, created_sc = Sub_Carpeta.objects.get_or_create(nombre=sub_carpeta_nombre)
                if created_sc: logger.info(f"Sub_Carpeta creada: '{sub_carpeta_nombre}'")
            except Exception as sc_e:
                logger.error(f"Error al get_or_create Sub_Carpeta '{sub_carpeta_nombre}' para código {codigo_item}: {sc_e}")
                # Decide si continuar sin sub_carpeta o fallar
        #else: logger.warning(f"Falta 'sub_carpeta' en fila para código {codigo_item}.")

        # 2. Obtener/Crear Sub_Titulo
        sub_titulo_nombre = row.pop('sub_titulo', None)
        sub_titulo = None
        if sub_titulo_nombre:
             try:
                sub_titulo, created_st = Sub_Titulo.objects.get_or_create(nombre=sub_titulo_nombre)
                if created_st: logger.info(f"Sub_Titulo creado: '{sub_titulo_nombre}'")
             except Exception as st_e:
                 logger.error(f"Error al get_or_create Sub_Titulo '{sub_titulo_nombre}' para código {codigo_item}: {st_e}")
                # Decide si continuar sin sub_titulo o fallar
        #else: logger.warning(f"Falta 'sub_titulo' en fila para código {codigo_item}.")

        # 3. Preparar datos para Item (eliminar 'codigo' y añadir relaciones)
        defaults = {k: v for k, v in row.items() if k != 'codigo'}
        defaults['sub_carpeta'] = sub_carpeta
        defaults['sub_titulo'] = sub_titulo
        defaults['actualizado'] = True # Marcar como actualizado

        # 4. Usar update_or_create para atomicidad
        item, created = Item.objects.update_or_create(codigo=codigo_item, defaults=defaults)

        if created:
            logger.info(f"Item CREADO con código: {codigo_item}")
        else:
            logger.info(f"Item ACTUALIZADO con código: {codigo_item}")

    except Exception as e:
        logger.error(f"Error CRÍTICO al procesar/guardar registro para código '{codigo_item}'. Fila original: {row_original}")
        logger.exception(e) # Loguea el traceback completo
        # Opcional: Escribir error a un archivo CSV si es necesario (similar a la otra función)


def desactualizar_anteriores(filtro):
    """Marca items como no actualizados basado en un filtro de código."""
    logger.info(f"Marcando como no actualizados items con código terminando en: '{filtro}'")
    try:
        # Usar update para eficiencia
        count = Item.objects.filter(codigo__endswith=filtro).update(actualizado=False)
        logger.info(f"{count} items marcados como no actualizados para filtro '{filtro}'.")
    except Exception as e:
        logger.error(f"Error al desactualizar items para filtro '{filtro}'.")
        logger.exception(e)

def buscar_modificar_registros(csv_file, filtro):
    """Procesa un CSV registro por registro."""
    # Nota: Esta función es menos eficiente que el procesamiento por lotes.
    logger.info(f"Iniciando procesamiento INDIVIDUAL desde CSV: '{csv_file}' para filtro: '{filtro}'")
    try:
        desactualizar_anteriores(filtro)
        processed_count = 0
        skipped_count = 0
        with open(csv_file, newline='', encoding='utf-8') as csvfile: # Especificar encoding
            reader = csv.DictReader(csvfile)
            for row in reader:
                logger.debug(f"Procesando fila CSV: {row}")
                # Validar precio_base antes de procesar
                precio_base = row.get('precio_base')
                if precio_base in [None, '', ' ', '-', '.', '#N/A', '#VALUE!']:
                    # logger.debug(f"Fila omitida por precio_base inválido ('{precio_base}') para código {row.get('codigo', 'N/A')}")
                    skipped_count += 1
                    continue

                # Asegurarse que los campos FK esperados existen, aunque sean None/vacíos
                if 'sub_carpeta' not in row: row['sub_carpeta'] = None
                if 'sub_titulo' not in row: row['sub_titulo'] = None

                crear_o_actualizar_registro(row) # Llama a la función refactorizada con logging
                processed_count += 1

        logger.info(f"Carga INDIVIDUAL desde CSV '{csv_file}' completada para filtro '{filtro}'. Procesados: {processed_count}, Omitidos: {skipped_count}")

    except FileNotFoundError:
         logger.error(f"Archivo CSV no encontrado: '{csv_file}'")
    except Exception as e:
        logger.error(f"Error al leer o procesar el archivo CSV '{csv_file}' en buscar_modificar_registros.")
        logger.exception(e)


# --- Google Drive/Sheet Operations ---

# Remover función f() ya que su lógica parece estar (o debería estar) en principal()

def fusionar_hojas(wb): # Modificado para recibir Workbook, no file path/object
    """Fusiona hojas de un Workbook openpyxl, excluyendo 'general'."""
    # Nota: Esta función puede consumir mucha memoria para archivos grandes.
    logger.info("Iniciando fusión de hojas (excluyendo 'general')...")
    all_data = []
    sheet_count = 0
    for ws in wb.worksheets:
        if ws.title.lower() != "general": # Comparación insensible a mayúsculas
            logger.debug(f"Leyendo datos de hoja: '{ws.title}'")
            # Iterar filas para mejor manejo de memoria vs ws.values
            sheet_data = []
            for row in ws.iter_rows(values_only=True):
                sheet_data.append(row)
            if sheet_data: # Solo añadir si la hoja tiene datos
                 all_data.extend(sheet_data)
                 sheet_count += 1
            else:
                 logger.debug(f"Hoja '{ws.title}' está vacía o no se pudieron leer datos.")

    if not all_data:
         logger.warning("No se encontraron datos en las hojas a fusionar.")
         # Considera si crear la hoja "cargar datos" vacía o retornar None/Error
         ws_new = wb.create_sheet(title="cargar datos")
         return wb # Devuelve con la hoja vacía

    logger.info(f"Datos de {sheet_count} hojas recopilados. Creando hoja 'cargar datos'.")
    # Crear DataFrame (puede ser intensivo en memoria)
    df = pd.DataFrame(all_data)

    # Crear nueva hoja
    # Verificar si ya existe para evitar error, o eliminarla primero
    if "cargar datos" in wb.sheetnames:
        logger.warning("La hoja 'cargar datos' ya existe. Será reemplazada.")
        del wb["cargar datos"]
    ws_new = wb.create_sheet(title="cargar datos")

    # Escribir datos a la nueva hoja eficientemente
    try:
        from openpyxl.utils.dataframe import dataframe_to_rows
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=False), 1):
            for c_idx, value in enumerate(row, 1):
                ws_new.cell(row=r_idx, column=c_idx, value=value)
        logger.info("Datos escritos en la hoja 'cargar datos'.")
    except ImportError:
         logger.warning("dataframe_to_rows no disponible. Usando método alternativo (puede ser más lento).")
         data_list = df.values.tolist()
         for row_list in data_list:
             ws_new.append(row_list)


    return wb # Retorna el Workbook modificado

# --- Cartel Operations ---

def marcar_revisar_carteles(id_proveedor):
    """Marca carteles asociados a un proveedor para revisión."""
    logger.info(f"Marcando carteles para revisar para proveedor ID: {id_proveedor}")
    try:
        count_c = Carteles.objects.filter(proveedor=id_proveedor).update(revisar=True)
        logger.info(f"{count_c} Carteles marcados.")
        count_cc = CartelesCajon.objects.filter(proveedor=id_proveedor).update(revisar=True)
        logger.info(f"{count_cc} CartelesCajon marcados.")
    except Exception as e:
        logger.error(f"Error al marcar carteles para revisar para proveedor ID {id_proveedor}.")
        logger.exception(e)


# --- Main Processing Function ---

def principal():
    """Función principal que orquesta la actualización de planillas y datos."""
    logger.info("--- INICIO FUNCIÓN PRINCIPAL ---")
    patoba = None
    try:
        patoba = Patoba(None) # Asumiendo que Patoba se inicializa sin request aquí
        gmail_service = patoba.gmail_service
        drive_service = patoba.drive_service
        if not drive_service:
             logger.critical("Servicio de Google Drive no inicializado. Abortando.")
             return
        if not gmail_service:
             logger.warning("Servicio de Gmail no inicializado. get_emails no funcionará.")

    except Exception as e:
        logger.critical(f"Error al inicializar Patoba o servicios de Google: {e}")
        logger.exception(e)
        return # Salir si no se puede inicializar

    # --- 1. Procesar Emails (si aplica) ---
    try:
        if gmail_service and drive_service:
             logger.info("Procesando emails...")
             get_emails(gmail_service, drive_service) # Asume que esta función tiene su propio logging interno
             logger.info("Procesamiento de emails finalizado.")
        else:
             logger.info("Saltando procesamiento de emails por falta de servicios.")
    except Exception as e:
         logger.error("Error durante la llamada a get_emails.")
         logger.exception(e)

    # --- 2. Listar Archivos de Drive y Actualizar Listado_Planillas ---
    logger.info("Listando archivos de Drive Inbox y actualizando Listado_Planillas...")
    try:
        items_drive = patoba.listar(100, const.INBOX) # Usar const en lugar de cosnt
        created_count = 0
        checked_count = 0
        skipped_count = 0
        for item_info in items_drive:
            checked_count += 1
            item_name = item_info.get('name')
            item_id = item_info.get('id')
            if not item_name or not item_id:
                 logger.warning(f"Item de Drive omitido por falta de 'name' o 'id': {item_info}")
                 skipped_count += 1
                 continue
            try:
                # Usar update_or_create para evitar duplicados si ya existe por ID pero cambió nombre
                obj, created = Listado_Planillas.objects.update_or_create(
                    identificador=item_id,
                    defaults={'descripcion': item_name}
                )
                if created:
                    logger.info(f"Listado_Planillas CREADO: ID={item_id}, Desc={item_name}")
                    created_count += 1
                # else: logger.debug(f"Listado_Planillas ya existe/actualizado: ID={item_id}, Desc={item_name}")

            except Exception as db_e:
                 logger.error(f"Error en update_or_create Listado_Planillas para ID='{item_id}', Nombre='{item_name}': {db_e}")
                 skipped_count += 1
        logger.info(f"Listado de Drive procesado. Verificados: {checked_count}, Creados: {created_count}, Omitidos/Errores: {skipped_count}")

    except HttpError as http_e:
         logger.error(f"Error HTTP al listar archivos de Drive Inbox (ID: {const.INBOX}): {http_e}")
    except Exception as e:
        logger.error("Error inesperado al listar archivos de Drive o actualizar Listado_Planillas.")
        logger.exception(e)

    # --- 3. Procesar Planilla "Caramia" (Fusionar Hojas) ---
    # Esta lógica parece específica y podría moverse a una función separada
    logger.info("Procesando planilla específica 'Caramia' para fusionar hojas...")
    try:
        # Buscar por el nombre del proveedor en lugar de string fijo si es posible
        # Asumiendo que ListaProveedores relaciona nombre "Caramia" con el objeto Proveedor
        lp_caramia = ListaProveedores.objects.filter(nombre="Caramia").first()
        if lp_caramia and lp_caramia.proveedor_obj: # Asume que hay campo 'proveedor_obj'
             planilla_caramia = Listado_Planillas.objects.filter(proveedor=lp_caramia.proveedor_obj).first()
        else:
             # Fallback a buscar por descripción si no hay relación directa
             planilla_caramia = Listado_Planillas.objects.filter(descripcion__icontains="Caramia").first() # Búsqueda flexible

        if not planilla_caramia:
            logger.warning("No se encontró registro de Listado_Planillas para 'Caramia'. Saltando fusión.")
        else:
            file_id_caramia = planilla_caramia.identificador
            logger.info(f"Descargando archivo 'Caramia' (ID: {file_id_caramia}) para fusión.")
            request_caramia = drive_service.files().get_media(fileId=file_id_caramia)
            file_caramia = io.BytesIO()
            downloader_caramia = MediaIoBaseDownload(file_caramia, request_caramia)
            done_caramia = False
            while not done_caramia:
                status, done_caramia = downloader_caramia.next_chunk()
                # logger.debug(f"Progreso descarga Caramia: {int(status.progress() * 100)}%")

            file_caramia.seek(0)
            wb_caramia = openpyxl.load_workbook(file_caramia)
            logger.info("Archivo 'Caramia' descargado. Fusionando hojas...")

            wb_fusionado = fusionar_hojas(wb_caramia) # Llama a la función de fusión

            logger.info("Hojas fusionadas. Subiendo archivo modificado a Drive...")
            # Guardar cambios en Google Drive
            output_stream = io.BytesIO(save_virtual_workbook(wb_fusionado))
            media_caramia = MediaIoBaseUpload(output_stream, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', resumable=True)
            drive_service.files().update(fileId=file_id_caramia, media_body=media_caramia).execute()
            logger.info(f"Archivo 'Caramia' (ID: {file_id_caramia}) actualizado en Drive con hoja 'cargar datos'.")

            # Actualizar hoja en DB (opcional, si es necesario)
            # planilla_caramia.hoja = "cargar datos"
            # planilla_caramia.save()

    except HttpError as http_e:
         if http_e.resp.status == 404:
              logger.warning(f"Archivo 'Caramia' no encontrado en Drive (404) con ID: {planilla_caramia.identificador if 'planilla_caramia' in locals() and planilla_caramia else 'N/A'}")
              # Considerar eliminar el registro de planilla_caramia si es 404
         else:
              logger.error(f"Error HTTP ({http_e.resp.status}) al procesar planilla 'Caramia': {http_e}")
    except Exception as e:
        logger.error("Error inesperado al procesar planilla 'Caramia'.")
        logger.exception(e)

    # --- 4. Obtener Nombres de Hojas para Planillas Pendientes ---
    logger.info("Obteniendo nombres de hojas para planillas pendientes (listo=False, descargar=False)...")
    datos_pendientes = Listado_Planillas.objects.filter(listo=False, descargar=False)
    processed_sheets = 0
    errors_sheets = 0
    deleted_404_sheets = 0
    for dato in datos_pendientes:
        logger.debug(f"Procesando hojas para planilla ID={dato.identificador}, Desc='{dato.descripcion}'")
        try:
            request_sheets = drive_service.files().get_media(fileId=dato.identificador)
            file_sheets = io.BytesIO()
            downloader_sheets = MediaIoBaseDownload(file_sheets, request_sheets)
            done_sheets = False
            while not done_sheets:
                status, done_sheets = downloader_sheets.next_chunk()

            file_sheets.seek(0)
            xls = pd.read_excel(file_sheets, sheet_name=None) # Lee todas las hojas

            sheet_names = [""] # Empezar con vacío como en el original?
            sheet_names.extend(list(xls.keys()))
            dato.hojas = ';'.join(sheet_names) # Guarda nombres separados por ;
            dato.save()
            logger.debug(f"Hojas guardadas para {dato.identificador}: {dato.hojas}")
            processed_sheets += 1

        except HttpError as http_e:
            if http_e.resp.status == 404:
                logger.warning(f"Archivo no encontrado (404) al obtener hojas para ID={dato.identificador}. Eliminando registro.")
                try:
                    dato.delete()
                    deleted_404_sheets += 1
                except Exception as del_e:
                    logger.error(f"Error al eliminar registro ID={dato.identificador} después de 404: {del_e}")
                    errors_sheets += 1
            else:
                logger.error(f"Error HTTP ({http_e.resp.status}) al obtener hojas para ID={dato.identificador}: {http_e}")
                errors_sheets += 1
        except Exception as e:
            logger.error(f"Error (no HTTP) al leer hojas (pandas?) para ID={dato.identificador}")
            logger.exception(e)
            errors_sheets += 1
    logger.info(f"Obtención de nombres de hojas completada. Procesados: {processed_sheets}, Errores: {errors_sheets}, Eliminados (404): {deleted_404_sheets}")

    # --- 5. Procesar Planillas Marcadas como 'listo=True' ---
    logger.info("Procesando planillas marcadas como 'listo=True'...")
    lista_procesar = Listado_Planillas.objects.filter(listo=True)
    if not lista_procesar.exists():
        logger.info("No hay planillas marcadas como 'listo=True' para procesar.")
    else:
        logger.info(f"Planillas a procesar: {lista_procesar.count()}")

    mi_diccionario = {} # Para mapeo de descarga

    for sp in lista_procesar:
        nombre_proveedor_desc = sp.descripcion # Nombre original del archivo en Drive
        proveedor_obj = sp.proveedor # Objeto Proveedor asociado
        # Intentar obtener el nombre de la plantilla desde el proveedor
        nombre_plantilla = None
        if proveedor_obj:
             lp_obj = getattr(proveedor_obj, 'identificador', None) # Asume relación inversa a ListaProveedores
             if lp_obj:
                  nombre_plantilla = lp_obj.nombre # Nombre de ListaProveedores es el nombre de la plantilla
        # else: logger.warning(f"Planilla ID {sp.id} no tiene Proveedor asociado.")

        if not nombre_plantilla or nombre_plantilla.lower() == 'otros':
            logger.warning(f"Saltando planilla ID {sp.id} (Desc: '{sp.descripcion}') porque no tiene proveedor válido o es 'Otros'.")
            continue

        logger.info(f"--- Procesando planilla lista: '{nombre_plantilla}' (ID DB: {sp.id}, ID Drive: {sp.identificador}) ---")
        fecha_str = sp.fecha.strftime('%Y-%m-%d') if sp.fecha else "sin_fecha"
        nombre_descargable = f"{nombre_plantilla}-{fecha_str}"
        hoja_seleccionada = sp.hoja

        logger.debug(f"Datos: nombre_prov='{nombre_proveedor_desc}', nombre_plantilla='{nombre_plantilla}', hoja='{hoja_seleccionada}'")

        id_archivo_proveedor = sp.identificador # ID del archivo original descargado
        id_archivo_plantilla = None
        id_hoja_reemplazable = None

        try:
            # Obtener ID de la plantilla y hoja reemplazable
            id_archivo_plantilla = patoba.obtener_id_por_nombre(nombre_plantilla, const.PLANTILLAS)
            if not id_archivo_plantilla:
                 logger.error(f"No se encontró ID de plantilla en Drive para '{nombre_plantilla}'. Saltando.")
                 continue
            sp.id_sp = id_archivo_plantilla # Guardar ID plantilla en BD

            id_hoja_reemplazable = patoba.obtener_id_hoja_por_nombre("Reemplazable", id_archivo_plantilla)
            if not id_hoja_reemplazable:
                 logger.error(f"No se encontró hoja 'Reemplazable' en plantilla ID '{id_archivo_plantilla}'. Saltando.")
                 continue

            # --- Descargar datos 'BDD' de la plantilla y procesar CSV ---
            logger.info(f"Descargando datos 'BDD' de plantilla '{nombre_plantilla}' (ID: {id_archivo_plantilla})...")
            result_bdd = patoba.sheet_service.spreadsheets().values().get(
                spreadsheetId=id_archivo_plantilla, range='BDD').execute()
            values_bdd = result_bdd.get('values', [])

            if not values_bdd:
                logger.warning(f"No se encontraron datos en la hoja 'BDD' de la plantilla '{nombre_plantilla}'. No se procesará CSV.")
            else:
                csv_file_path = f'{nombre_plantilla}.csv'
                try:
                    with open(csv_file_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(values_bdd)
                    logger.info(f"Datos 'BDD' guardados en '{csv_file_path}'.")

                    # --- Procesar el CSV ---
                    # Obtener la abreviatura del proveedor (asumiendo está en ListaProveedores)
                    abreviatura_filtro = None
                    if proveedor_obj and hasattr(proveedor_obj, 'identificador') and proveedor_obj.identificador:
                         abreviatura_filtro = proveedor_obj.identificador.abreviatura
                    
                    if abreviatura_filtro:
                         logger.info(f"Procesando archivo CSV '{csv_file_path}' con filtro '{abreviatura_filtro}'...")
                         # DESCOMENTAR LA LÍNEA QUE CORRESPONDA:
                         # buscar_modificar_registros(csv_file_path, abreviatura_filtro) # Procesamiento individual (lento)
                         # ó si tienes la función de lotes disponible:
                         # buscar_modificar_registros_lotes(csv_file_path, abreviatura_filtro) # Procesamiento por lotes (rápido)
                         logger.warning(f"PROCESAMIENTO CSV PARA '{nombre_plantilla}' COMENTADO EN EL CÓDIGO.") # Recordatorio

                         marcar_revisar_carteles(proveedor_obj.id) # Marcar carteles después de procesar datos
                    else:
                         logger.warning(f"No se pudo obtener abreviatura para proveedor '{nombre_plantilla}'. No se puede procesar CSV.")

                except IOError as ioe:
                     logger.error(f"Error de I/O al escribir/leer CSV '{csv_file_path}': {ioe}")
                except Exception as csv_e:
                     logger.error(f"Error al procesar CSV para '{nombre_plantilla}'.")
                     logger.exception(csv_e)

            # --- Copiar hoja 'Reemplazable' ---
            # La lógica original de copiar la hoja 'Reemplazable' usando datos del archivo del proveedor
            # parece compleja y potencialmente incorrecta si la meta es solo usar la plantilla.
            # Se necesita clarificar qué se quiere copiar y a dónde.
            # El código original parece intentar leer el archivo del proveedor (ya procesado?)
            # y luego llamar a copiar_reemplazable con argumentos confusos.
            # VOY A OMITIR ESTA PARTE POR AHORA HASTA CLARIFICAR EL OBJETIVO.
            logger.warning("La lógica de 'copiar_reemplazable' se ha omitido por falta de claridad en el objetivo.")
            # --- Fin Omisión ---


            # --- Actualizar Plantilla en Drive (Ejemplo: ¿Añadir timestamp?) ---
            # Esto parece llamar a una función para actualizar la propia plantilla en Drive.
            # El código original llama a obtener_g_sheet_por_id con 'identificador', que parece ser el ID
            # del *archivo original del proveedor*, no de la plantilla. Usaremos id_archivo_plantilla.
            try:
                spreadsheet_obj = patoba.obtener_g_sheet_por_id(id_archivo_plantilla)
                if spreadsheet_obj:
                     logger.info(f"Actualizando plantilla '{nombre_plantilla}' en Drive (ID: {id_archivo_plantilla})...")
                     # patoba.actualizar_plantilla(spreadsheet_obj, sp) # Asume que esta función existe y hace algo útil
                     logger.warning("Llamada a patoba.actualizar_plantilla comentada.") # Comentado si no es clara su función
                else:
                     logger.error(f"No se pudo obtener objeto Spreadsheet para ID {id_archivo_plantilla} para actualizar.")
            except Exception as upd_e:
                 logger.error(f"Error al intentar actualizar plantilla '{nombre_plantilla}' en Drive.")
                 logger.exception(upd_e)


            # --- Marcar planilla como procesada y limpiar ---
            sp.listo = False # Marcar como ya no lista para procesar de nuevo
            sp.save()
            logger.info(f"Planilla '{nombre_plantilla}' (ID DB: {sp.id}) marcada como lista=False.")

            # ¿Borrar archivo original de Inbox? ¡CUIDADO! Esto es destructivo.
            # patoba.borrar_por_id(sp.identificador) # ID del archivo original
            logger.warning(f"Borrado del archivo original de Drive (ID: {sp.identificador}) COMENTADO por seguridad.")

            # Marcar ListaProveedor para que se vuelva a generar CSV la próxima vez?
            if proveedor_obj and hasattr(proveedor_obj, 'identificador') and proveedor_obj.identificador:
                 try:
                    lp_instance = proveedor_obj.identificador # Obtener ListaProveedores
                    lp_instance.hay_csv_pendiente = True
                    lp_instance.save()
                    logger.info(f"ListaProveedores '{nombre_plantilla}' marcada con hay_csv_pendiente=True.")
                 except Exception as lp_e:
                      logger.error(f"Error al marcar hay_csv_pendiente=True para ListaProveedores '{nombre_plantilla}': {lp_e}")


        except HttpError as http_e:
             logger.error(f"Error HTTP procesando planilla '{nombre_plantilla}': Status {http_e.resp.status}, {http_e}")
        except Exception as e:
            logger.error(f"Error inesperado procesando planilla '{nombre_plantilla}'.")
            logger.exception(e)

        logger.info(f"--- Fin procesamiento planilla lista: '{nombre_plantilla}' ---")


    logger.info("--- FIN FUNCIÓN PRINCIPAL ---")


# --- Script Execution ---
if __name__ == '__main__':
    # Configurar logging básico si se ejecuta directamente
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    principal()