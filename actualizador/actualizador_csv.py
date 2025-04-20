import os
import csv
import sys
import time
import unicodedata
import logging

from django.conf import settings as const
# Asumiendo que tus modelos están en 'bdd' y 'x_cartel'
# Ajusta las rutas de importación si es necesario
from bdd.models import Item, Sub_Carpeta, Sub_Titulo, ListaProveedores, Proveedor
from x_cartel.models import Carteles, CartelesCajon
from bdd.classes import Patoba # Asumiendo que esta clase existe y se usa

from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User


# Configuración del logger (ya estaba, aseguramos que esté)
logger = logging.getLogger(__name__)

# --- Funciones de Utilidad ---

def limpiar_texto(texto):
    """Limpia un texto convirtiendo caracteres no ASCII a su equivalente ASCII."""
    if not isinstance(texto, str):
        # logger.warning(f"limpiar_texto recibió un tipo no string: {type(texto)}. Convirtiendo a string.")
        texto = str(texto)
    try:
        texto_normalizado = unicodedata.normalize('NFKD', texto)
        texto_ascii = texto_normalizado.encode('ASCII', 'ignore').decode('ASCII')
        return texto_ascii
    except Exception as e:
        logger.error(f"Error al limpiar texto: '{texto}'. Error: {e}")
        return texto # Devuelve el original si falla la limpieza

def validar_digitos_str(cadena):
    """Valida si una cadena contiene solo dígitos, puntos o comas."""
    if not isinstance(cadena, str):
        # logger.debug(f"validar_digitos_str recibió tipo no string: {type(cadena)}")
        return False
    if not cadena: # Cadena vacía no es válida aquí
        return False
    for caracter in cadena:
        if not caracter.isdigit() and caracter not in ['.', ',']:
            return False
    return True

def custom_round(price):
    """Aplica reglas de redondeo customizadas basadas en el número de dígitos."""
    try:
        # Asegurarse que es un número flotante
        price = float(str(price).replace(',', '.')) # Reemplazar coma por punto si existe
    except (ValueError, TypeError):
        logger.warning(f"custom_round recibió un valor no numérico: '{price}'. Devolviendo 0.")
        return 0 # O manejar como prefieras

    price_int = int(price) # Usar la parte entera para determinar dígitos
    digits = len(str(price_int))

    if digits <= 1:
        return 10 if price > 0 else 0
    elif digits == 2:
        # Redondeo al múltiplo de 5 más cercano, mínimo 10
        rounded_price = round(price / 5) * 5
        return max(rounded_price, 10)
    elif digits == 3:
        # Redondeo al múltiplo de 10 más cercano
        return round(price / 10) * 10
    elif 4 <= digits <= 6:
         # Redondeo al múltiplo de 50 más cercano
        return round(price / 50) * 50
    elif digits >= 7:
         # Redondeo al múltiplo de 500 más cercano
        return round(price / 500) * 500
    else: # Caso inesperado (e.g., negativo?), devuelve el precio original o ajustado
        logger.warning(f"custom_round encontró un caso no manejado para precio: {price}")
        return price # O aplica una regla por defecto

# --- Funciones de Procesamiento de Datos ---

def crear_o_actualizar_registro(row_original):
    """Intenta crear o actualizar un registro Item basado en una fila de datos."""
    # Guardamos una copia para logging en caso de error
    row = row_original.copy()
    codigo_item = row.get('codigo', 'N/A')
    logger.debug(f"Procesando registro individual para código: {codigo_item}")

    try:
        # 1. Obtener/Crear Sub_Carpeta
        sub_carpeta_nombre = row.pop('sub_carpeta', None)
        if sub_carpeta_nombre:
            sub_carpeta, created_sc = Sub_Carpeta.objects.get_or_create(nombre=sub_carpeta_nombre)
            if created_sc:
                logger.info(f"Sub_Carpeta creada: '{sub_carpeta_nombre}'")
            row['sub_carpeta'] = sub_carpeta
        else:
            logger.warning(f"Falta 'sub_carpeta' en la fila para código {codigo_item}.")
            row['sub_carpeta'] = None # Asegurar que es None si falta

        # 2. Obtener/Crear Sub_Titulo
        sub_titulo_nombre = row.pop('sub_titulo', None)
        if sub_titulo_nombre:
            sub_titulo, created_st = Sub_Titulo.objects.get_or_create(nombre=sub_titulo_nombre)
            if created_st:
                logger.info(f"Sub_Titulo creado: '{sub_titulo_nombre}'")
            row['sub_titulo'] = sub_titulo
        else:
            logger.warning(f"Falta 'sub_titulo' en la fila para código {codigo_item}.")
            row['sub_titulo'] = None # Asegurar que es None si falta

        # 3. Limpiar descripción
        descripcion_original = row.pop('descripcion', '')
        row['descripcion'] = limpiar_texto(descripcion_original)

        # 4. Ajustar final_efectivo si es necesario
        final_efectivo = row.get('final_efectivo', 0)
        final = row.get('final', 0)
        if not isinstance(final_efectivo, (int, float)) or final_efectivo <= 0:
             if isinstance(final, (int, float)):
                 row['final_efectivo'] = final
                 logger.debug(f"Ajustado final_efectivo para código {codigo_item} al valor de final: {final}")
             else:
                 row['final_efectivo'] = 0 # Valor por defecto si 'final' tampoco es válido
                 logger.warning(f"final_efectivo y final inválidos para código {codigo_item}. Establecido a 0.")


        # 5. Crear o Actualizar Item
        # Preparamos los defaults quitando 'codigo' y asegurando valores correctos
        defaults = {k: v for k, v in row.items() if k != 'codigo'}
        # Asegurarse que los campos ForeignKey son instancias o None
        if 'sub_carpeta' in defaults and not isinstance(defaults['sub_carpeta'], Sub_Carpeta) and defaults['sub_carpeta'] is not None:
            logger.error(f"Valor inválido para sub_carpeta en defaults para código {codigo_item}. Omitiendo.")
            defaults.pop('sub_carpeta') # O manejar de otra forma
        if 'sub_titulo' in defaults and not isinstance(defaults['sub_titulo'], Sub_Titulo) and defaults['sub_titulo'] is not None:
            logger.error(f"Valor inválido para sub_titulo en defaults para código {codigo_item}. Omitiendo.")
            defaults.pop('sub_titulo') # O manejar de otra forma

        # Marcamos como actualizado antes de guardar
        defaults['actualizado'] = True

        item, created = Item.objects.update_or_create(codigo=codigo_item, defaults=defaults)

        if created:
            logger.info(f"Item CREADO con código: {codigo_item}")
        else:
            logger.info(f"Item ACTUALIZADO con código: {codigo_item}")

    except Exception as e:
        logger.error(f"Error al procesar/guardar registro para código '{codigo_item}'. Fila original: {row_original}")
        logger.exception(e) # Loguea el traceback completo

        # Escribir la fila original con error al archivo CSV
        error_file = 'errores_importacion.csv'
        try:
            file_exists = os.path.isfile(error_file)
            with open(error_file, 'a', newline='', encoding='utf8') as file:
                # Usar DictWriter para manejar encabezados automáticamente
                fieldnames = row_original.keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader() # Escribir encabezado si el archivo es nuevo
                writer.writerow(row_original)
            logger.info(f"Fila con error para código '{codigo_item}' guardada en {error_file}")
        except Exception as csv_e:
            logger.error(f"¡FALLO AL ESCRIBIR EN CSV DE ERRORES! Error: {csv_e}. Fila: {row_original}")


def crear_o_actualizar_registros_en_lotes(rows, tamaño_lote=1000):
    """Procesa y guarda registros de Item en lotes usando bulk_update."""
    logger.info(f"Iniciando procesamiento por lotes. Tamaño del lote: {tamaño_lote}. Filas totales: {len(rows)}")
    items_para_crear = []
    mapa_items_para_actualizar = {} # codigo -> item_preparado
    codigos_con_error = set()

    # Fase 1: Preparar datos y separar creaciones de actualizaciones
    logger.info("Fase 1: Preparando datos y clasificando items...")
    inicio_prep = time.time()
    codigos_existentes = set(Item.objects.filter(codigo__in=[row['codigo'] for row in rows]).values_list('codigo', flat=True))
    subcarpetas_cache = {sc.nombre: sc for sc in Sub_Carpeta.objects.all()}
    subtitulos_cache = {st.nombre: st for st in Sub_Titulo.objects.all()}
    
    for row_original in rows:
        row = row_original.copy()
        codigo_item = row.get('codigo')

        if not codigo_item:
            logger.warning(f"Fila omitida por falta de código: {row_original}")
            codigos_con_error.add(str(row_original)) # Guardar representación de la fila
            continue

        # Validar campos clave antes de procesar (opcional pero recomendado)
        if any(value in [None, '', '           '] for key, value in row.items() if key not in ['sub_carpeta', 'sub_titulo', 'codigo']):
             logger.warning(f"Fila omitida para código '{codigo_item}' por contener valores vacíos/nulos: {row_original}")
             codigos_con_error.add(codigo_item)
             continue

        try:
            # Obtener/Crear Sub_Carpeta (usando cache)
            sub_carpeta_nombre = row.pop('sub_carpeta', None)
            sub_carpeta = None
            if sub_carpeta_nombre:
                if sub_carpeta_nombre in subcarpetas_cache:
                     sub_carpeta = subcarpetas_cache[sub_carpeta_nombre]
                else:
                     sub_carpeta, created = Sub_Carpeta.objects.get_or_create(nombre=sub_carpeta_nombre)
                     if created: logger.info(f"Sub_Carpeta creada: '{sub_carpeta_nombre}'")
                     subcarpetas_cache[sub_carpeta_nombre] = sub_carpeta # Actualizar cache
            #else: logger.warning(f"Falta 'sub_carpeta' en fila para código {codigo_item}.")

            # Obtener/Crear Sub_Titulo (usando cache)
            sub_titulo_nombre = row.pop('sub_titulo', None)
            sub_titulo = None
            if sub_titulo_nombre:
                if sub_titulo_nombre in subtitulos_cache:
                    sub_titulo = subtitulos_cache[sub_titulo_nombre]
                else:
                    sub_titulo, created = Sub_Titulo.objects.get_or_create(nombre=sub_titulo_nombre)
                    if created: logger.info(f"Sub_Titulo creado: '{sub_titulo_nombre}'")
                    subtitulos_cache[sub_titulo_nombre] = sub_titulo # Actualizar cache
            #else: logger.warning(f"Falta 'sub_titulo' en fila para código {codigo_item}.")

            # Limpiar descripción
            descripcion_limpia = limpiar_texto(row.get('descripcion', ''))

            # Ajustar final_efectivo
            final_efectivo = row.get('final_efectivo', 0)
            final = row.get('final', 0)
            try: # Convertir a float antes de comparar
                 final_efectivo_f = float(str(final_efectivo).replace(',', '.')) if final_efectivo else 0
                 final_f = float(str(final).replace(',', '.')) if final else 0
                 if final_efectivo_f <= 0:
                     final_efectivo_f = final_f
            except ValueError:
                 logger.warning(f"Valor no numérico en final/final_efectivo para código {codigo_item}. Usando 0.")
                 final_efectivo_f = 0

            # Preparar datos para el modelo Item
            item_data = {
                'codigo': codigo_item,
                'sub_carpeta': sub_carpeta,
                'sub_titulo': sub_titulo,
                'descripcion': descripcion_limpia,
                'actualizado': True,
                # Añadir el resto de campos desde 'row', convirtiendo tipos si es necesario
                'precio_base': row.get('precio_base', 0), # Asume conversión necesaria
                'final': final_f if 'final' in row else 0,
                'final_efectivo': final_efectivo_f,
                # ... añadir otros campos de tu modelo Item ...
            }
            # Eliminar claves None que no deben ir al modelo
            item_data = {k: v for k, v in item_data.items() if v is not None or k in ['sub_carpeta', 'sub_titulo']} # Mantener FKs aunque sean None


            if codigo_item in codigos_existentes:
                 # Para actualizar: crear instancia temporal o preparar para bulk_update
                 item_obj = Item(**item_data) # Creamos obj temporal para bulk_update
                 mapa_items_para_actualizar[codigo_item] = item_obj
            else:
                 # Para crear: añadir a lista para bulk_create
                 items_para_crear.append(Item(**item_data))

        except Exception as e:
            logger.error(f"Error al preparar datos para código '{codigo_item}'. Fila original: {row_original}")
            logger.exception(e)
            codigos_con_error.add(codigo_item if codigo_item else str(row_original))
            # Opcional: Escribir error a CSV aquí también

    fin_prep = time.time()
    logger.info(f"Fase 1 completada en {fin_prep - inicio_prep:.2f} seg. Items a crear: {len(items_para_crear)}, a actualizar: {len(mapa_items_para_actualizar)}, con error: {len(codigos_con_error)}")

    # Fase 2: Ejecutar operaciones en BD por lotes
    logger.info("Fase 2: Ejecutando operaciones en Base de Datos...")
    inicio_db = time.time()

    # Bulk Create
    if items_para_crear:
        try:
            with transaction.atomic():
                Item.objects.bulk_create(items_para_crear, batch_size=tamaño_lote)
            logger.info(f"Bulk Create completado para {len(items_para_crear)} items.")
        except Exception as e:
            logger.error(f"Error durante Bulk Create.")
            logger.exception(e)
            # Aquí podrías intentar guardar individualmente o loguear más detalle

    # Bulk Update
    if mapa_items_para_actualizar:
        items_actualizar_lista = list(mapa_items_para_actualizar.values())
        # Obtener todos los campos excepto la PK para actualizar
        campos_actualizar = [field.name for field in Item._meta.fields if not field.primary_key]
        try:
            with transaction.atomic():
                 Item.objects.bulk_update(items_actualizar_lista, campos_actualizar, batch_size=tamaño_lote)
            logger.info(f"Bulk Update completado para {len(items_actualizar_lista)} items.")
        except Exception as e:
            logger.error(f"Error durante Bulk Update.")
            logger.exception(e)
            # Aquí podrías intentar guardar individualmente o loguear más detalle


    fin_db = time.time()
    logger.info(f"Fase 2 completada en {fin_db - inicio_db:.2f} seg.")

    # Opcional: Loguear items con error que no se procesaron
    if codigos_con_error:
        logger.warning(f"Se encontraron errores al preparar/procesar {len(codigos_con_error)} filas/códigos.")
        # Podrías escribir estos códigos/filas a un archivo si es necesario


def desactualizar_anteriores(filtro):
    """Marca items como no actualizados basado en un filtro de código."""
    logger.info(f"Marcando como no actualizados items con código terminando en: '{filtro}'")
    try:
        count = Item.objects.filter(codigo__endswith=filtro).update(actualizado=False)
        logger.info(f"{count} items marcados como no actualizados para filtro '{filtro}'.")
    except Exception as e:
        logger.error(f"Error al desactualizar items para filtro '{filtro}'.")
        logger.exception(e)

def buscar_modificar_registros(csv_file, filtro):
    """Procesa un CSV registro por registro (menos eficiente)."""
    logger.info(f"Iniciando procesamiento individual desde CSV: '{csv_file}' para filtro: '{filtro}'")
    desactualizar_anteriores(filtro)
    processed_count = 0
    error_count = 0
    try:
        with open(csv_file, newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Validar precio_base antes de procesar
                precio_base = row.get('precio_base')
                if precio_base in [None, '', ' ', '-', '.', '#N/A', '#VALUE!'] or not validar_digitos_str(str(precio_base)):
                    logger.debug(f"Fila omitida por precio_base inválido ('{precio_base}') para código {row.get('codigo', 'N/A')}")
                    continue

                # Aplicar redondeo customizado si los precios son válidos
                try:
                    if 'final' in row and validar_digitos_str(str(row['final'])):
                        row['final'] = custom_round(row['final'])
                    if 'final_efectivo' in row and validar_digitos_str(str(row['final_efectivo'])):
                        row['final_efectivo'] = custom_round(row['final_efectivo'])
                except Exception as round_e:
                     logger.warning(f"Error aplicando redondeo custom a fila {row.get('codigo', 'N/A')}: {round_e}")

                crear_o_actualizar_registro(row) # Llama a la función que ya tiene logging
                processed_count += 1

    except FileNotFoundError:
        logger.error(f"Archivo CSV no encontrado: '{csv_file}'")
        error_count += 1
    except Exception as e:
        logger.error(f"Error al leer o procesar el archivo CSV '{csv_file}'.")
        logger.exception(e)
        error_count += 1

    if error_count == 0:
        logger.info(f"Procesamiento individual de '{csv_file}' (filtro '{filtro}') completado. {processed_count} filas procesadas.")
    else:
        logger.error(f"Procesamiento individual de '{csv_file}' (filtro '{filtro}') finalizado con errores.")


def buscar_modificar_registros_lotes(csv_file, filtro):
    """Carga un CSV y procesa los registros en lotes (más eficiente)."""
    logger.info(f"Iniciando procesamiento por lotes desde CSV: '{csv_file}' para filtro: '{filtro}'")
    desactualizar_anteriores(filtro)
    rows = []
    read_count = 0
    skipped_count = 0
    try:
        with open(csv_file, newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                read_count += 1
                # Validar precio_base antes de añadir a la lista de procesamiento
                precio_base = row.get('precio_base')
                if precio_base in [None, '', ' ', '-', '.', '#N/A', '#VALUE!'] or not validar_digitos_str(str(precio_base)):
                    # logger.debug(f"Fila omitida por precio_base inválido ('{precio_base}') para código {row.get('codigo', 'N/A')}")
                    skipped_count += 1
                    continue

                 # Aplicar redondeo customizado si los precios son válidos
                try:
                    if 'final' in row and validar_digitos_str(str(row['final'])):
                        row['final'] = custom_round(row['final'])
                    if 'final_efectivo' in row and validar_digitos_str(str(row['final_efectivo'])):
                        row['final_efectivo'] = custom_round(row['final_efectivo'])
                except Exception as round_e:
                     logger.warning(f"Error aplicando redondeo custom a fila {row.get('codigo', 'N/A')} durante carga de lotes: {round_e}")
                     # Decidir si omitir la fila o continuar con precios originales

                rows.append(row)

        logger.info(f"Archivo CSV '{csv_file}' leído. Filas leídas: {read_count}, omitidas por precio_base inválido: {skipped_count}. Filas a procesar: {len(rows)}")
        if rows:
            crear_o_actualizar_registros_en_lotes(rows) # Llama a la función de lotes
        else:
            logger.info(f"No hay filas válidas para procesar en lotes desde '{csv_file}'.")

    except FileNotFoundError:
        logger.error(f"Archivo CSV no encontrado: '{csv_file}'")
    except Exception as e:
        logger.error(f"Error al leer o preparar lotes del archivo CSV '{csv_file}'.")
        logger.exception(e)

    logger.info(f"Procesamiento por lotes de '{csv_file}' (filtro '{filtro}') completado.")

def principal_csv():
    """Función principal que procesa CSVs pendientes para cada proveedor."""
    patoba = Patoba(None) # Asumiendo que Patoba no necesita request aquí
    logger.info("--- Iniciando Proceso Principal de Actualización desde CSVs ---")
    try:
        proveedores = ListaProveedores.objects.filter(hay_csv_pendiente=True)
        if not proveedores:
            logger.info("No hay proveedores marcados con CSV pendiente.")
            return

        logger.info(f"Proveedores encontrados con CSV pendiente: {[p.nombre for p in proveedores]}")

        for proveedor in proveedores:
            logger.info(f"--- Procesando proveedor: '{proveedor.nombre}' ---")
            ruta_csv = os.path.join(const.BASE_DIR, f'{proveedor.nombre}.csv')
            abreviatura = proveedor.abreviatura
            id_archivo_plantilla = None # Inicializar

            try:
                id_archivo_plantilla = patoba.obtener_id_por_nombre(proveedor.nombre, const.PLANTILLAS)
                if not id_archivo_plantilla:
                    logger.error(f"No se encontró ID de plantilla en Drive para '{proveedor.nombre}' en carpeta PLANTILLAS (ID: {const.PLANTILLAS}). Saltando descarga.")
                    continue # Saltar al siguiente proveedor

                logger.info(f"Obteniendo datos de Google Sheet '{proveedor.nombre}' (ID: {id_archivo_plantilla}), Rango: 'BDD'")
                result = patoba.sheet_service.spreadsheets().values().get(
                    spreadsheetId=id_archivo_plantilla, range='BDD').execute()
                values = result.get('values', [])

                if not values:
                    logger.warning(f"No se encontraron datos en la hoja 'BDD' de la plantilla '{proveedor.nombre}'. Creando CSV vacío.")
                    # Crear archivo vacío para evitar FileNotFoundError después
                    open(ruta_csv, 'w').close()
                else:
                    with open(ruta_csv, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerows(values)
                    logger.info(f"Datos guardados en '{ruta_csv}' ({len(values)} filas).")

            except Exception as e:
                logger.error(f"Error al descargar/guardar datos de Google Sheet para '{proveedor.nombre}' (ID: {id_archivo_plantilla}).")
                logger.exception(e)
                continue # Saltar procesamiento de este proveedor

            # Procesar el CSV descargado (o vacío)
            try:
                buscar_modificar_registros_lotes(ruta_csv, abreviatura)
            except Exception as e:
                 # La función llamada ya loguea sus errores internos
                 logger.error(f"Fallo general al llamar a buscar_modificar_registros_lotes para '{ruta_csv}'.")
                 # logger.exception(e) # Descomentar si se necesita traceback aquí también

            # Marcar proveedor como procesado y actualizar carteles/cajones
            try:
                # Refrescar instancia por si acaso
                prov_instance = ListaProveedores.objects.get(id=proveedor.id)
                prov_instance.hay_csv_pendiente = False
                prov_instance.save()
                logger.info(f"Proveedor '{proveedor.nombre}' marcado como procesado (hay_csv_pendiente=False).")

                carteles_updated = Carteles.objects.filter(proveedor=proveedor.id).update(revisar=True)
                logger.info(f"{carteles_updated} Carteles marcados para revisar para proveedor '{proveedor.nombre}'.")
                carteles_cajon_updated = CartelesCajon.objects.filter(proveedor=proveedor.id).update(revisar=True)
                logger.info(f"{carteles_cajon_updated} CartelesCajon marcados para revisar para proveedor '{proveedor.nombre}'.")

            except ListaProveedores.DoesNotExist:
                 logger.error(f"No se encontró el proveedor '{proveedor.nombre}' al intentar marcarlo como procesado.")
            except Exception as e:
                 logger.error(f"Error al actualizar estado o carteles para proveedor '{proveedor.nombre}'.")
                 logger.exception(e)

            logger.info(f"--- Fin del procesamiento para proveedor: '{proveedor.nombre}' ---")

    except Exception as e:
        logger.critical("Error CRÍTICO en la función principal_csv.")
        logger.exception(e)
    finally:
        logger.info("--- Fin del Proceso Principal de Actualización desde CSVs ---")


def apply_custom_round(batch_size=1000):
    """Aplica la función custom_round a los campos de precio de todos los Items."""
    logger.info(f"--- Iniciando Redondeo Custom por Lotes (Tamaño: {batch_size}) ---")
    try:
        items_qs = Item.objects.all()
        total_items = items_qs.count()
        logger.info(f"Total items a redondear: {total_items}")
        offset = 0
        updated_count = 0

        while offset < total_items:
            logger.debug(f"Procesando lote de redondeo: offset={offset}, batch_size={batch_size}")
            # Usar iterator para optimizar memoria en querysets grandes
            batch_items = list(items_qs[offset:offset + batch_size])
            items_to_update = []
            for item in batch_items:
                # Aplicar redondeo y verificar si hubo cambios
                original_final = item.final
                original_final_efectivo = item.final_efectivo
                original_final_rollo = item.final_rollo
                original_final_rollo_efectivo = item.final_rollo_efectivo

                item.final = custom_round(item.final)
                item.final_efectivo = custom_round(item.final_efectivo)
                item.final_rollo = custom_round(item.final_rollo)
                item.final_rollo_efectivo = custom_round(item.final_rollo_efectivo)

                # Añadir a la lista de actualización solo si algo cambió
                if (item.final != original_final or
                    item.final_efectivo != original_final_efectivo or
                    item.final_rollo != original_final_rollo or
                    item.final_rollo_efectivo != original_final_rollo_efectivo):
                    items_to_update.append(item)

            if items_to_update:
                 campos_a_actualizar = ['final', 'final_efectivo', 'final_rollo', 'final_rollo_efectivo']
                 Item.objects.bulk_update(items_to_update, campos_a_actualizar, batch_size=batch_size)
                 logger.debug(f"Lote de {len(items_to_update)} items redondeados y actualizados.")
                 updated_count += len(items_to_update)
            else:
                 logger.debug("Lote procesado, sin cambios detectados en redondeo.")

            offset += len(batch_items) # Avanzar por el tamaño real del lote procesado

        logger.info(f"Redondeo Custom completado. {updated_count} items tuvieron precios actualizados.")

    except Exception as e:
        logger.error("Error durante el proceso de redondeo custom.")
        logger.exception(e)
    finally:
        logger.info("--- Fin del Redondeo Custom por Lotes ---")


# --- Otras Funciones ---

def mostrara_boletas(bool_value):
    """Actualiza el campo 'impreso' en todas las boletas."""
    # Import local para evitar dependencia circular si 'boletas' importa algo de aquí
    from boletas.models import Boleta
    logger.info(f"Estableciendo campo 'impreso' a {bool_value} para todas las Boletas.")
    try:
        count = Boleta.objects.all().update(impreso=bool_value)
        logger.info(f"Campo 'impreso' actualizado a {bool_value} para {count} boletas.")
    except Exception as e:
        logger.error("Error al actualizar el estado 'impreso' de las boletas.")
        logger.exception(e)

def reset_user_password(username, password):
    """Resetea la contraseña de un usuario."""
    logger.warning(f"Intentando resetear contraseña para usuario: '{username}'")
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        logger.info(f"Contraseña reseteada exitosamente para el usuario '{username}'.")
    except User.DoesNotExist:
        logger.error(f"Usuario '{username}' no encontrado para resetear contraseña.")
    except Exception as e:
        logger.error(f"Error al resetear contraseña para usuario '{username}'.")
        logger.exception(e)


def filtrar_trabajados():
    """Exporta items trabajados a archivos CSV, uno por proveedor."""
    logger.info("Iniciando exportación de items trabajados por proveedor a CSV.")
    try:
        proveedores = Proveedor.objects.all()
        logger.info(f"Proveedores encontrados para exportar: {[p.text_display for p in proveedores]}") # Asume que text_display existe

        for proveedor in proveedores:
            logger.debug(f"Filtrando items trabajados para proveedor: '{proveedor.text_display}'")
            # Asumiendo que 'trabajado' es un BooleanField y 'proveedor' es ForeignKey a Proveedor
            filtrados = Item.objects.filter(trabajado=True, proveedor=proveedor)

            if not filtrados.exists():
                 logger.info(f"No se encontraron items trabajados para '{proveedor.text_display}'.")
                 continue

            # Crear un nombre de archivo único y seguro
            filename_base = limpiar_texto(proveedor.text_display).replace(' ', '_')
            filename = f'{filename_base}_trabajado.csv'
            logger.info(f"Exportando {filtrados.count()} items trabajados de '{proveedor.text_display}' a '{filename}'")

            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # Escribir encabezado (ajusta los nombres a tus campos exactos)
                    writer.writerow(['Codigo', 'Descripción', 'Stock', 'Carga Stock'])

                    # Escribir los datos de los items
                    for item in filtrados:
                        # Asegúrate que item.stock existe o maneja AttributeError
                        stock_val = getattr(item, 'stock', 'N/A')
                        writer.writerow([item.codigo, item.descripcion, stock_val, ''])
                logger.debug(f"Archivo '{filename}' creado exitosamente.")
            except IOError as e:
                 logger.error(f"Error de I/O al escribir el archivo CSV '{filename}' para proveedor '{proveedor.text_display}'.")
                 logger.exception(e)
            except Exception as e:
                 logger.error(f"Error inesperado al escribir el archivo CSV '{filename}' para proveedor '{proveedor.text_display}'.")
                 logger.exception(e)

        logger.info("Exportación de items trabajados completada.")

    except Exception as e:
        logger.error("Error general durante la exportación de items trabajados.")
        logger.exception(e)


def asociar_proveedores():
    """Intenta asociar Items a Proveedores basado en la abreviatura en el código."""
    logger.info("--- Iniciando Asociación de Items a Proveedores por Abreviatura ---")
    try:
        items_sin_proveedor = Item.objects.filter(proveedor__isnull=True)
        total_items = items_sin_proveedor.count()
        if total_items == 0:
            logger.info("No hay items sin proveedor asociado.")
            return

        logger.info(f"Items sin proveedor encontrados: {total_items}. Intentando asociar...")
        lista_proveedores_all = ListaProveedores.objects.all() # Asumiendo que ListaProveedores tiene 'abreviatura' y relaciona a 'Proveedor'

        # Crear un diccionario para mapear abreviaturas a IDs de Proveedor reales
        abreviatura_a_proveedor_id = {}
        for lp in lista_proveedores_all:
             # Asumiendo que ListaProveedores tiene un campo ForeignKey 'proveedor_obj' al modelo Proveedor
             # y un campo 'abreviatura' como '/ABR'
             if hasattr(lp, 'proveedor_obj') and lp.proveedor_obj is not None:
                 abreviatura_a_proveedor_id[lp.abreviatura] = lp.proveedor_obj.id
             else:
                 logger.warning(f"ListaProveedores ID {lp.id} (Abrev: {lp.abreviatura}) no tiene un proveedor_obj asociado.")


        logger.debug(f"Mapa de abreviaturas a IDs de Proveedor creado: {abreviatura_a_proveedor_id}")

        items_para_actualizar = []
        asociados_count = 0
        no_encontrados_count = 0

        # Iterar por lotes para manejar muchos items
        batch_size = 5000
        for i in range(0, total_items, batch_size):
             batch_items = list(items_sin_proveedor[i:i + batch_size])
             logger.debug(f"Procesando lote de asociación: {i} a {i + len(batch_items)}")
             for item in batch_items:
                 try:
                     # Obtener la abreviatura del código del item
                     partes_codigo = item.codigo.split('/')
                     if len(partes_codigo) > 1:
                         abreviatura = '/' + partes_codigo[-1]
                         proveedor_id_encontrado = abreviatura_a_proveedor_id.get(abreviatura)

                         if proveedor_id_encontrado:
                             # Asociar el item con el proveedor ID
                             item.proveedor_id = proveedor_id_encontrado # Asignar directamente el ID
                             items_para_actualizar.append(item)
                             asociados_count += 1
                         else:
                             # logger.debug(f"No se encontró proveedor para abreviatura '{abreviatura}' (Código: {item.codigo})")
                             no_encontrados_count +=1
                     else:
                          # logger.debug(f"Código '{item.codigo}' no contiene '/' para extraer abreviatura.")
                          no_encontrados_count +=1
                 except Exception as e:
                      logger.error(f"Error procesando asociación para item código '{item.codigo}'.")
                      logger.exception(e)
                      no_encontrados_count +=1


        # Actualizar los items en la base de datos en lotes
        if items_para_actualizar:
            logger.info(f"Realizando Bulk Update para asociar {len(items_para_actualizar)} items...")
            try:
                Item.objects.bulk_update(items_para_actualizar, ['proveedor'], batch_size=batch_size)
                logger.info(f"Bulk Update de asociación completado.")
            except Exception as e:
                 logger.error("Error durante el Bulk Update de asociación de proveedores.")
                 logger.exception(e)
        else:
             logger.info("No se realizaron asociaciones nuevas.")

        logger.info(f"Asociación finalizada. Items asociados: {asociados_count}. Items no asociados/con error: {no_encontrados_count}")

    except Exception as e:
        logger.error("Error CRÍTICO durante la asociación de proveedores.")
        logger.exception(e)
    finally:
        logger.info("--- Fin de Asociación de Items a Proveedores ---")


# --- Punto de Entrada Principal ---

if __name__ == "__main__":
    # Configurar el logging básico si se ejecuta como script principal
    # Esto es útil para ver logs en consola si no tienes una config de Django
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.info("=============================================")
    logger.info("      INICIO DEL SCRIPT DE ACTUALIZACIÓN     ")
    logger.info("=============================================")

    start_time = time.time()

    # --- Descomenta las funciones que quieras ejecutar ---
    # logger.info(">>> Ejecutando reset_user_password (COMENTADO POR SEGURIDAD)")
    # reset_user_password(input("Usuario a resetear: "), input("Nueva contraseña: "))

    # logger.info(">>> Ejecutando filtrar_trabajados (COMENTADO)")
    # filtrar_trabajados()

    # logger.info(">>> Ejecutando asociar_proveedores (COMENTADO)")
    # asociar_proveedores()

    logger.info(">>> Ejecutando principal_csv...")
    principal_csv()

    logger.info(">>> Ejecutando apply_custom_round...")
    apply_custom_round()

    end_time = time.time()
    logger.info("=============================================")
    logger.info(f"     SCRIPT FINALIZADO en {end_time - start_time:.2f} segundos")
    logger.info("=============================================")