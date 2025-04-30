import os
import logging  # Importar el módulo logging
from django.conf import settings as const
from bdd.classes import Patoba
from x_cartel.models import Carteles, CartelesCajon
from bdd.models import  Item, Sub_Carpeta, Sub_Titulo, ListaProveedores, Proveedor # Añadido Proveedor si no estaba
import csv
import unicodedata
from django.db import transaction
import sys
import time
from django.contrib.auth.models import User
from boletas.models import Boleta
from django.db.models import Q


# Configuración del logger
# Configuración básica de logging (puedes personalizarla más)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    # Asegurarse de que price es un número antes de procesar
    if not isinstance(price, (int, float)):
        try:
            # Intentar convertir a float si es una cadena válida
            price = float(str(price).replace(',', '.'))
        except (ValueError, TypeError):
            # Si no se puede convertir, retornar un valor por defecto o manejar el error
            logger.warning(f"custom_round recibió un valor no numérico inválido: {price}. Retornando 0.")
            return 0  # O podrías retornar price, None, o lanzar una excepción

    # Continuar con la lógica original solo si price es numérico
    price = int(price) # Convertir a entero para obtener longitud precisa sin decimales

    # Obtén el número de dígitos en el precio
    digits = len(str(price))

    # Aplica las reglas de redondeo basadas en el número de dígitos
    if digits == 1:
        if price == 0:
            return 0 # Devolver 0 si el precio es 0
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
        # Esto podría cubrir casos donde digits es 0 (si price fuera 0 como float inicialmente)
        # o si la lógica anterior no capturó algo.
        return price


def crear_o_actualizar_registro(row):
    # Esta función parece escribir todas las filas a items.csv,
    # lo cual podría no ser la intención original si solo se querían errores.
    # Considera mover esto dentro del bloque 'except' si solo quieres loguear errores allí.
    try:
        with open('items.csv', 'a', newline='', encoding='utf8') as file:
            writer = csv.writer(file)
            # Agrega la fila con error al archivo CSV
            writer.writerow(row.values())
    except Exception as e:
        logger.error(f"No se pudo escribir la fila en items.csv: {row}. Error: {e}")

    try:
        # Recuperar o crear una instancia de Sub_Carpeta
        sub_carpeta_nombre = row.pop('sub_carpeta', None) # Usar pop con default
        if sub_carpeta_nombre:
            sub_carpeta, created = Sub_Carpeta.objects.get_or_create(nombre=sub_carpeta_nombre)
            row['sub_carpeta'] = sub_carpeta
        else:
             row['sub_carpeta'] = None # O manejar como error si es requerido

        # Recuperar o crear una instancia de Sub_Titulo
        sub_titulo_nombre = row.pop('sub_titulo', None) # Usar pop con default
        if sub_titulo_nombre:
            sub_titulo, created = Sub_Titulo.objects.get_or_create(nombre=sub_titulo_nombre)
            row['sub_titulo'] = sub_titulo
        else:
            row['sub_titulo'] = None # O manejar como error si es requerido

        # Manejar precios
        final_efectivo_val = row.get('final_efectivo')
        final_val = row.get('final')
        if final_efectivo_val is None or final_efectivo_val <= 0:
             row['final_efectivo'] = final_val # Asegúrate que 'final' existe y es válido

    except Exception as e:
        # Captura excepciones específicas si es posible (e.g., KeyError)
        logger.error(f"Error pre-procesando Sub_Carpeta/Sub_Titulo para la fila: {row}. Error: {e}", exc_info=True)
        # Decide si continuar o retornar aquí si la fila es inválida

    # logger.debug(f"Fila procesada antes de guardar: {row}") # Reemplaza print(row) si era para debug

    codigo_item = row.get('codigo')
    if not codigo_item:
        logger.error(f"Fila sin código no puede ser procesada: {row}")
        return # No intentar guardar sin código

    try:
        # Limpiar descripción antes de get_or_create o actualizar
        descripcion_original = row.pop('descripcion', '') # Default a '' si no existe
        row['descripcion'] = limpiar_texto(descripcion_original)

        item, created = Item.objects.get_or_create(codigo=codigo_item, defaults=row)
        item.marcar_actualizado()
        if not created:
            # Actualizar campos existentes si no fue creado
            for key, value in row.items():
                 # Asegurarse que el campo existe en el modelo Item antes de setattr
                if hasattr(item, key):
                    setattr(item, key, value)
                # else: # Opcional: loguear si hay campos en la fila que no están en el modelo
                #     logger.warning(f"Campo '{key}' de la fila no encontrado en el modelo Item para código {codigo_item}.")
        # Guardar los cambios (ya sea creación o actualización)
        item.save()
        # logger.info(f"{'Creado' if created else 'Actualizado'}: {item.codigo}") # Reemplaza print('creado o guardado: ', item)

    except Exception as e:
        logger.error(f"Error al intentar guardar Item con código: {codigo_item}", exc_info=True)
        # Abre el archivo CSV donde se guardarán las filas con errores
        try:
            with open('errores.csv', 'a', newline='', encoding='utf8') as file:
                writer = csv.writer(file)
                # Reinsertar descripción original si fue popeada y quieres loguearla
                row_values = list(row.values())
                 # Intentar encontrar dónde iba la descripción o añadirla al final
                row_values.insert(1, descripcion_original) # Asumiendo que era el segundo campo, ajustar si no
                writer.writerow(row_values) # Escribir valores
        except Exception as csv_e:
            logger.error(f"No se pudo escribir la fila con error en errores.csv para código {codigo_item}. Error CSV: {csv_e}")



def crear_o_actualizar_registros_en_lotes(rows, tamaño_lote):
    for i in range(0, len(rows), tamaño_lote):
        lote = rows[i:i+tamaño_lote]
        items_para_crear = []
        items_para_actualizar_map = {} # Usar mapa para buscar actualizaciones por código
        codigos_lote = {row['codigo'] for row in lote if row.get('codigo')} # Obtener códigos del lote actual
        inicio = time.time()  # Inicio del temporizador

        # Pre-cargar subcarpetas y subtítulos para evitar consultas repetidas en el bucle
        subcarpetas_nombres = {row.get('sub_carpeta') for row in lote if row.get('sub_carpeta')}
        subtitulos_nombres = {row.get('sub_titulo') for row in lote if row.get('sub_titulo')}
        subcarpetas_map = {sc.nombre: sc for sc in Sub_Carpeta.objects.filter(nombre__in=subcarpetas_nombres)}
        subtitulos_map = {st.nombre: st for st in Sub_Titulo.objects.filter(nombre__in=subtitulos_nombres)}

        # Consultar items existentes en la BD para este lote
        items_existentes = {item.codigo: item for item in Item.objects.filter(codigo__in=codigos_lote)}

        # Medición de memoria (opcional, puede quitarse si no es necesaria)
        # uso_memoria_inicial = sum(sys.getsizeof(obj) for obj in locals().values()) # Aproximación

        with transaction.atomic():
            for row in lote:
                codigo_item = row.get('codigo')
                # Validaciones básicas de la fila
                if not codigo_item:
                    logger.warning(f"Fila sin código en lote, saltando: {row}")
                    continue
                if any(value is None or str(value).strip() == '' for key, value in row.items() if key not in ['sub_carpeta', 'sub_titulo', 'final_efectivo', 'codigo']): # Ajustar claves opcionales
                     logger.warning(f"Fila con valores vacíos/None en lote (código: {codigo_item}), saltando: {row}")
                     continue

                # Procesar SubCarpeta y SubTitulo usando los mapas pre-cargados
                sub_carpeta_nombre = row.pop('sub_carpeta', None)
                sub_titulo_nombre = row.pop('sub_titulo', None)
                sub_carpeta = None
                sub_titulo = None

                if sub_carpeta_nombre:
                    if sub_carpeta_nombre not in subcarpetas_map:
                        sub_carpeta, _ = Sub_Carpeta.objects.get_or_create(nombre=sub_carpeta_nombre)
                        subcarpetas_map[sub_carpeta_nombre] = sub_carpeta # Añadir al mapa si es nuevo
                    else:
                        sub_carpeta = subcarpetas_map[sub_carpeta_nombre]
                row['sub_carpeta'] = sub_carpeta

                if sub_titulo_nombre:
                    if sub_titulo_nombre not in subtitulos_map:
                        sub_titulo, _ = Sub_Titulo.objects.get_or_create(nombre=sub_titulo_nombre)
                        subtitulos_map[sub_titulo_nombre] = sub_titulo # Añadir al mapa si es nuevo
                    else:
                        sub_titulo = subtitulos_map[sub_titulo_nombre]
                row['sub_titulo'] = sub_titulo

                # Procesar precios y descripción
                try:
                    final_efectivo_val = row.get('final_efectivo')
                    final_val = row.get('final')
                    if final_efectivo_val is None or final_efectivo_val <= 0:
                        row['final_efectivo'] = final_val # Asignar 'final' si efectivo es inválido

                    # Limpiar descripción ANTES de asignarla al objeto Item
                    descripcion_original = row.pop('descripcion', '')
                    row['descripcion'] = limpiar_texto(descripcion_original)

                except Exception as e:
                     logger.error(f"Error procesando precios/descripción para código {codigo_item}: {e}", exc_info=True)
                     continue # Saltar esta fila si hay error aquí


                # Decidir si crear o actualizar
                if codigo_item in items_existentes:
                    # Preparar para actualización
                    item_existente = items_existentes[codigo_item]
                    actualizado = False
                    for key, value in row.items():
                        if hasattr(item_existente, key) and getattr(item_existente, key) != value:
                            setattr(item_existente, key, value)
                            actualizado = True
                    if actualizado or not item_existente.actualizado: # Marcar si hubo cambios o si no estaba actualizado
                        item_existente.marcar_actualizado()
                        items_para_actualizar_map[codigo_item] = item_existente
                else:
                    # Preparar para creación
                    # Necesitamos asegurarnos de que todos los campos requeridos por el modelo Item
                    # están presentes en 'row' o tienen un default en el modelo.
                    # El pop de descripción ya se hizo.
                    try:
                        nuevo_item = Item(**row) # Crear instancia sin guardar aún
                        nuevo_item.marcar_actualizado()
                        items_para_crear.append(nuevo_item)
                    except Exception as e:
                        logger.error(f"Error al instanciar nuevo Item (código: {codigo_item}): {e}. Fila: {row}", exc_info=True)


            # Ejecutar operaciones bulk fuera del bucle de filas, pero dentro de la transacción
            try:
                if items_para_crear:
                    Item.objects.bulk_create(items_para_crear, ignore_conflicts=True) # O manejar conflictos si es necesario
                    logger.info(f"Lote {i//tamaño_lote + 1}: {len(items_para_crear)} items creados.")
            except Exception as e:
                logger.error(f"Error en bulk_create para lote {i//tamaño_lote + 1}: {e}", exc_info=True)

            try:
                items_a_actualizar_lista = list(items_para_actualizar_map.values())
                if items_a_actualizar_lista:
                     # Obtener todos los campos del modelo excepto la clave primaria
                    campos_modelo = [field.name for field in Item._meta.fields if field.name != Item._meta.pk.name]
                    # Asegurar que solo actualizamos campos presentes en el modelo
                    campos_para_actualizar = [campo for campo in campos_modelo if campo != 'codigo'] # Excluir codigo si es PK y no debe cambiar
                    campos_para_actualizar.append('actualizado') # Asegurarse que 'actualizado' se incluye
                    # Quitar duplicados por si acaso
                    campos_para_actualizar = list(set(campos_para_actualizar))

                    Item.objects.bulk_update(items_a_actualizar_lista, campos_para_actualizar)
                    logger.info(f"Lote {i//tamaño_lote + 1}: {len(items_a_actualizar_lista)} items actualizados.")
            except Exception as e:
                logger.error(f"Error en bulk_update para lote {i//tamaño_lote + 1}: {e}", exc_info=True)


        fin = time.time()  # Fin del temporizador
        # uso_memoria_final = sum(sys.getsizeof(obj) for obj in locals().values()) # Aproximación

        logger.info(f"Lote {i//tamaño_lote + 1} procesado en {fin - inicio:.4f} segundos.")
        # logger.info(f"Uso de memoria aproximado del lote: {uso_memoria_final - uso_memoria_inicial} bytes")


def desactualizar_anteriores(filtro):
    """Marca como no actualizados los items cuyo código termina con el filtro dado."""
    logger.info(f"Marcando como no actualizados items terminados en: {filtro}")
    try:
        # Asegurarse que el filtro no sea vacío o None si eso puede causar problemas
        if filtro:
            count = Item.objects.filter(codigo__endswith=filtro).update(actualizado=False)
            logger.info(f"{count} items marcados como no actualizados para el filtro: {filtro}")
        else:
            logger.warning("Se intentó desactualizar con un filtro vacío.")
    except Exception as e:
        logger.error(f"Error al desactualizar items con filtro {filtro}: {e}", exc_info=True)


def buscar_modificar_registros(csv_file, filtro):
    """Procesa un archivo CSV para crear o actualizar registros uno por uno."""
    logger.info(f"Iniciando procesamiento individual para archivo: {csv_file}, filtro: {filtro}")
    desactualizar_anteriores(filtro)
    try:
        with open(csv_file, newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            processed_count = 0
            error_count = 0
            for row in reader:
                # Limpiar espacios en blanco de las claves y valores si es necesario
                row = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}

                precio_base = row.get('precio_base')
                # Filtrar filas con precio_base inválido o ausente
                invalid_price_values = [None, '', ' ', '-', '.', '#N/A', '#VALUE!']
                if precio_base in invalid_price_values:
                    # logger.debug(f"Saltando fila por precio_base inválido ('{precio_base}'): {row.get('codigo')}")
                    continue

                try:
                    # Intentar procesar y guardar la fila
                    crear_o_actualizar_registro(row)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Error procesando fila (individual) con código {row.get('codigo')}: {e}", exc_info=True)
                    error_count += 1
            logger.info(f"Procesamiento individual completado para {filtro}. Filas procesadas: {processed_count}, Errores: {error_count}")

    except FileNotFoundError:
        logger.error(f"Archivo CSV no encontrado: {csv_file}")
    except Exception as e:
        logger.error(f"Error general al leer o procesar el archivo CSV {csv_file}: {e}", exc_info=True)
    logger.info(f'Procesamiento individual finalizado para: {filtro}')


def buscar_modificar_registros_lotes(csv_file, filtro, tamaño_lote=10000):
    """Procesa un archivo CSV para crear o actualizar registros en lotes."""
    logger.info(f"Iniciando procesamiento por lotes para archivo: {csv_file}, filtro: {filtro}, tamaño lote: {tamaño_lote}")
    desactualizar_anteriores(filtro)
    rows = []
    try:
        with open(csv_file, newline='', encoding='utf8') as csvfile:
            reader = csv.DictReader(csvfile)
            skipped_count = 0
            valid_count = 0
            for row in reader:
                # Limpiar espacios en claves y valores
                row = {k.strip() if k else k: v.strip() if isinstance(v, str) else v for k, v in row.items() if k} # Ignorar claves vacías

                # logger.debug(f"Leyendo fila: {row}") # Loguear fila leída si es necesario para debug

                precio_base = str(row.get('precio_base', '')).strip() # Convertir a str y limpiar
                codigo = row.get('codigo')

                # Filtrar filas con valores inválidos o vacíos cruciales
                invalid_price_values = ['', ' ', '-', '.', '#N/A', '#VALUE!']
                if precio_base in invalid_price_values or not codigo:
                     # logger.debug(f"Saltando fila por precio_base ('{precio_base}') o código ('{codigo}') inválido/faltante.")
                     skipped_count += 1
                     continue

                # Validar y redondear precios si son válidos
                try:
                    # Validar precio_base antes de intentar convertir/redondear otros
                    if validar_digitos_str(precio_base):
                        final_val_str = str(row.get('final', '0')).replace(',', '.').strip()
                        if validar_digitos_str(final_val_str):
                             row['final'] = custom_round(float(final_val_str))
                        # else: # Opcional: loguear o poner default si 'final' no es válido
                        #     logger.warning(f"Valor 'final' no válido ('{row.get('final')}') para código {codigo}. Usando 0 o valor original.")
                        #     row['final'] = 0 # o mantener valor original si se prefiere

                        final_efectivo_str = str(row.get('final_efectivo', '0')).replace(',', '.').strip()
                        if validar_digitos_str(final_efectivo_str):
                             row['final_efectivo'] = custom_round(float(final_efectivo_str))
                        # else: # Opcional: loguear o poner default
                        #      logger.warning(f"Valor 'final_efectivo' no válido ('{row.get('final_efectivo')}') para código {codigo}. Usando 0 o valor original.")
                        #      row['final_efectivo'] = 0 # o mantener valor original

                        rows.append(row)
                        valid_count +=1
                    else:
                        # logger.debug(f"Saltando fila porque precio_base ('{precio_base}') no pasó la validación de dígitos para código {codigo}.")
                        skipped_count += 1
                        continue
                except Exception as e:
                    logger.error(f"Error validando/redondeando precios para código {codigo}. Fila: {row}. Error: {e}", exc_info=True)
                    skipped_count += 1


            logger.info(f"Lectura de {csv_file} completa. Filas válidas: {valid_count}, Filas saltadas: {skipped_count}.")
            # Procesar las filas acumuladas en lotes
            if rows:
                crear_o_actualizar_registros_en_lotes(rows, tamaño_lote)
            else:
                logger.info("No se encontraron filas válidas para procesar en lotes.")

    except FileNotFoundError:
        logger.error(f"Archivo CSV no encontrado: {csv_file}")
    except Exception as e:
        logger.error(f"Error general al leer o procesar el archivo CSV {csv_file} en modo lotes: {e}", exc_info=True)

    logger.info(f'Procesamiento por lotes finalizado para: {filtro}')


def principal_csv():
    """Función principal que procesa archivos CSV pendientes para cada proveedor."""
    patoba = Patoba(None) # Asumiendo que Patoba se inicializa correctamente así
    logger.info("Chequeando proveedores con CSV pendientes...")
    try:
        # Obtener proveedores con CSV pendiente o todos si es necesario testear
        proveedores = ListaProveedores.objects.filter(hay_csv_pendiente=True)
        # proveedores = ListaProveedores.objects.all() # Descomentar para probar con todos

        if not proveedores.exists():
            logger.info("No hay proveedores con CSV pendientes para procesar.")
            return

        for proveedor in proveedores:
            logger.info(f"Procesando proveedor: {proveedor.nombre} (Abreviatura: {proveedor.abreviatura})")
            ruta_csv = os.path.join(const.BASE_DIR, f'{proveedor.nombre}.csv')
            abreviatura = proveedor.abreviatura
            id_archivo_plantilla = None # Inicializar

            # Intentar obtener ID de plantilla
            try:
                id_archivo_plantilla = patoba.obtener_id_por_nombre(proveedor.nombre, const.PLANTILLAS)
                if not id_archivo_plantilla:
                    logger.warning(f"No se encontró ID de plantilla para el proveedor: {proveedor.nombre}. Saltando descarga.")
                    continue # Saltar al siguiente proveedor si no hay plantilla
            except Exception as e:
                 logger.error(f"Error al obtener ID de plantilla para {proveedor.nombre}: {e}", exc_info=True)
                 continue # Saltar al siguiente proveedor

            # Descargar datos de Google Sheet si hay ID
            try:
                logger.info(f"Descargando datos de Google Sheet (ID: {id_archivo_plantilla}) para {proveedor.nombre}...")
                # Obtener los datos de la hoja de cálculo
                result = patoba.sheet_service.spreadsheets().values().get(
                    spreadsheetId=id_archivo_plantilla, range='BDD' # Asumiendo que el rango siempre es 'BDD'
                ).execute()
                values = result.get('values', [])

                if not values:
                    logger.warning(f"No se encontraron datos en la hoja 'BDD' para {proveedor.nombre}.")
                    # Decide si continuar con un archivo vacío o marcar como error/saltar
                    # Por ahora, crearemos un archivo vacío si no hay datos.
                else:
                    logger.info(f"Datos descargados ({len(values)} filas). Guardando en {ruta_csv}...")

                # Guardar los datos en un archivo CSV
                with open(ruta_csv, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(values)
                logger.info(f"Archivo CSV guardado: {ruta_csv}")

            except Exception as e:
                logger.error(f"Error al descargar o guardar datos de Google Sheet para {proveedor.nombre} (ID: {id_archivo_plantilla}): {e}", exc_info=True)
                # Decide si continuar sin el archivo CSV o detenerse/marcar error
                continue # Saltar procesamiento de este proveedor si falla la descarga

            # Procesar el archivo CSV descargado
            try:
                logger.info(f"Iniciando procesamiento del archivo CSV {ruta_csv} para {proveedor.nombre}...")
                buscar_modificar_registros_lotes(ruta_csv, abreviatura) # Usar procesamiento por lotes
                logger.info(f"Procesamiento CSV completado para {proveedor.nombre}.")

                # Marcar el proveedor como procesado SOLO si el procesamiento fue exitoso
                try:
                    lista_proveedor = ListaProveedores.objects.get(id=proveedor.id) # Recargar por si acaso
                    lista_proveedor.hay_csv_pendiente = False
                    lista_proveedor.save()
                    logger.info(f"Proveedor {proveedor.nombre} marcado como NO pendiente.")
                except ListaProveedores.DoesNotExist:
                    logger.error(f"No se encontró el proveedor {proveedor.nombre} en la BD para desmarcarlo.")
                except Exception as e_save:
                    logger.error(f"Error al desmarcar proveedor {proveedor.nombre}: {e_save}", exc_info=True)

                # Marcar carteles para revisión
                try:
                    carteles_count = Carteles.objects.filter(proveedor=proveedor.id).update(revisar=True)
                    carteles_cajon_count = CartelesCajon.objects.filter(proveedor=proveedor.id).update(revisar=True)
                    logger.info(f"Marcados para revisión: {carteles_count} carteles y {carteles_cajon_count} carteles de cajón para {proveedor.nombre}.")
                except Exception as e_cartel:
                     logger.error(f"Error al marcar carteles para revisión para {proveedor.nombre}: {e_cartel}", exc_info=True)

            except Exception as e:
                logger.error(f"Error durante el procesamiento del CSV o pasos posteriores para {proveedor.nombre}: {e}", exc_info=True)
                # NO desmarcar 'hay_csv_pendiente' si hubo un error aquí

    except Exception as e:
        logger.error(f"Error general en la función principal_csv: {e}", exc_info=True)

    logger.info("Función principal_csv finalizada.")

def apply_custom_round(batch_size=10000):
    """Aplica redondeo personalizado a varios campos de precio en todos los Items, por lotes."""
    logger.info(f"Iniciando redondeo personalizado por lotes de tamaño: {batch_size}")
    try:
        items_qs = Item.objects.all()
        total_items = items_qs.count()
        logger.info(f"Total items a redondear: {total_items}")
        offset = 0

        while offset < total_items:
            logger.info(f"Procesando lote de redondeo desde offset: {offset}")
            # Obtener el lote usando slicing sobre el queryset
            batch_qs = items_qs[offset : offset + batch_size]
            # Convertir a lista para poder modificar los objetos
            batch_list = list(batch_qs)

            items_to_update = []
            for item in batch_list:
                updated = False
                # Lista de campos a redondear
                campos_a_redondear = [
                    'final', 'final_efectivo', 'final_rollo', 'final_rollo_efectivo'
                ]
                for campo in campos_a_redondear:
                    valor_actual = getattr(item, campo, None)
                    # Solo redondear si el valor no es None
                    if valor_actual is not None:
                        valor_redondeado = custom_round(valor_actual)
                        # Actualizar solo si el valor redondeado es diferente
                        if valor_redondeado != valor_actual:
                            setattr(item, campo, valor_redondeado)
                            updated = True

                if updated:
                    items_to_update.append(item)

            if items_to_update:
                # Campos que potencialmente fueron modificados
                campos_modificados = ['final', 'final_efectivo', 'final_rollo', 'final_rollo_efectivo']
                Item.objects.bulk_update(items_to_update, campos_modificados)
                logger.info(f"Lote desde {offset}: {len(items_to_update)} items actualizados con redondeo.")
            else:
                 logger.info(f"Lote desde {offset}: No se necesitaron actualizaciones de redondeo.")


            offset += len(batch_list) # Incrementar offset por el tamaño real del lote procesado

        logger.info("Redondeo personalizado por lotes finalizado.")

    except Exception as e:
        logger.error(f"Error durante apply_custom_round: {e}", exc_info=True)


def mostrara_boletas(bool):
    """Actualiza el estado 'impreso' de todas las boletas."""
    nuevo_estado = bool
    logger.info(f"Estableciendo estado 'impreso' a {nuevo_estado} para todas las boletas.")
    try:
        count = Boleta.objects.all().update(impreso=nuevo_estado)
        logger.info(f"{count} boletas actualizadas al estado impreso={nuevo_estado}.")
    except Exception as e:
        logger.error(f"Error al actualizar estado de boletas a {nuevo_estado}: {e}", exc_info=True)

def reset(username, contraseña):
    """Resetea la contraseña de un usuario."""
    logger.info(f"Intentando resetear contraseña para usuario: {username}")
    try:
        u = User.objects.get(username=username)
        u.set_password(contraseña)
        u.save()
        logger.info(f"Contraseña reseteada exitosamente para el usuario: {username}")
    except User.DoesNotExist:
        logger.error(f"Usuario no encontrado: {username}")
    except Exception as e:
        logger.error(f"Error al resetear contraseña para {username}: {e}", exc_info=True)


def filtrar_trabajados():
    """Filtra items marcados como 'trabajado' por proveedor y los guarda en archivos CSV."""
    logger.info("Iniciando filtrado de items trabajados por proveedor...")
    try:
        # Obtener todos los proveedores que tienen items asociados
        proveedores_con_items = Proveedor.objects.filter(item__isnull=False).distinct()

        if not proveedores_con_items.exists():
            logger.info("No se encontraron proveedores con items asociados.")
            return

        for proveedor in proveedores_con_items:
            logger.info(f"Filtrando items trabajados para: {proveedor.identificador.nombre}") # Asumiendo que 'identificador' es la relación a ListaProveedores
            # Filtrar items por proveedor y si están trabajados
            # Ajusta el campo 'trabajado' si se llama diferente en tu modelo Item
            filtrados = Item.objects.filter(proveedor=proveedor, trabajado=True)

            if filtrados.exists():
                # Crear un nombre de archivo único para cada proveedor
                # Usar un nombre seguro para el archivo, ej. reemplazando espacios
                nombre_archivo_seguro = proveedor.identificador.nombre.replace(' ', '_').replace('/', '_')
                filename = f'{nombre_archivo_seguro}_trabajado.csv'
                logger.info(f"Encontrados {filtrados.count()} items trabajados. Guardando en: {filename}")

                try:
                    # Abrir (o crear) el archivo CSV
                    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                        # Crear un escritor CSV
                        writer = csv.writer(csvfile)
                        # Escribir encabezado (Ajusta los nombres a tus campos reales)
                        writer.writerow(['Codigo', 'Descripción', 'Stock', 'Carga Stock'])

                        # Escribir los datos de los items
                        for item in filtrados:
                            # Asegúrate de que los atributos coincidan con tu modelo Item
                            writer.writerow([item.codigo, item.descripcion, item.stock, '']) # 'Carga Stock' se deja vacío
                    logger.info(f"Archivo {filename} guardado exitosamente.")
                except IOError as e:
                    logger.error(f"Error de E/S al escribir el archivo {filename}: {e}", exc_info=True)
                except Exception as e:
                     logger.error(f"Error inesperado al escribir el archivo {filename}: {e}", exc_info=True)
            else:
                logger.info(f"No se encontraron items trabajados para {proveedor.identificador.nombre}.")

        logger.info("Filtrado de items trabajados completado.")

    except Exception as e:
        logger.error(f"Error general en la función filtrar_trabajados: {e}", exc_info=True)

def asociar_proveedores():
    """Asocia Items con Proveedores basándose en la abreviatura del código."""
    logger.info("Iniciando asociación de Items con Proveedores...")
    try:
        # Obtener todos los items que aún no tienen un proveedor asociado
        items_sin_proveedor = Item.objects.filter(proveedor__isnull=True)
        count_items_inicial = items_sin_proveedor.count()
        logger.info(f"Se encontraron {count_items_inicial} items sin proveedor asociado.")

        if count_items_inicial == 0:
            logger.info("No hay items que necesiten asociación de proveedor.")
            return

        # Obtener todos los ListaProveedores y crear un mapa de abreviatura a objeto ListaProveedores
        lista_proveedores = ListaProveedores.objects.all()
        abreviatura_a_lista_proveedores = {lp.abreviatura: lp for lp in lista_proveedores if lp.abreviatura}

        # Crear un mapa de objeto ListaProveedores a objeto Proveedor para eficiencia
        # Asume que existe una relación uno a uno o clave externa desde Proveedor a ListaProveedores llamada 'identificador'
        proveedores_map = {prov.identificador_id: prov for prov in Proveedor.objects.filter(identificador__in=lista_proveedores)}


        items_para_actualizar = []
        items_no_asociados_count = 0

        # Iterar solo sobre los items sin proveedor
        for item in items_sin_proveedor:
            # Extraer la parte después de la última '/' como abreviatura potencial
            # y añadir '/' al principio como en el diccionario
            partes_codigo = item.codigo.split('/')
            if len(partes_codigo) > 1:
                abreviatura_detectada = '/' + partes_codigo[-1]
            else:
                abreviatura_detectada = None # No se encontró '/'

            if abreviatura_detectada and abreviatura_detectada in abreviatura_a_lista_proveedores:
                lista_prov = abreviatura_a_lista_proveedores[abreviatura_detectada]

                # Buscar el Proveedor correspondiente usando el mapa
                proveedor = proveedores_map.get(lista_prov.id)

                if proveedor:
                    # Asociar el item con el proveedor
                    item.proveedor = proveedor
                    items_para_actualizar.append(item)
                else:
                     logger.warning(f"Se encontró ListaProveedores para abreviatura '{abreviatura_detectada}' (Item {item.codigo}), pero no el objeto Proveedor correspondiente.")
                     items_no_asociados_count += 1
            else:
                # logger.debug(f"No se encontró ListaProveedores para la abreviatura '{abreviatura_detectada}' del item {item.codigo}.")
                items_no_asociados_count += 1


        # Actualizar los items en la base de datos si hay algo que actualizar
        if items_para_actualizar:
            logger.info(f"Intentando actualizar {len(items_para_actualizar)} items con su proveedor asociado...")
            try:
                # Especificar explícitamente que solo el campo 'proveedor' debe actualizarse
                Item.objects.bulk_update(items_para_actualizar, ['proveedor'])
                logger.info(f"Asociación completada. {len(items_para_actualizar)} items actualizados.")
                if items_no_asociados_count > 0:
                    logger.warning(f"{items_no_asociados_count} items no pudieron ser asociados (falta abreviatura/proveedor).")
            except Exception as e:
                 logger.error("Error durante el bulk_update de asociación de proveedores:", exc_info=True)
        else:
            logger.info("No se realizaron asociaciones (ningún item pudo ser mapeado o ya estaban asociados).")
            if items_no_asociados_count > 0:
                 logger.warning(f"{items_no_asociados_count} items no pudieron ser asociados (falta abreviatura/proveedor).")


    except Exception as e:
        logger.error(f"Error general en la función asociar_proveedores: {e}", exc_info=True)


# --- Bloque Principal ---
if __name__ == "__main__":
    # Configura Django si este script se ejecuta fuera de un manage.py runscript
    # import django
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings') # Reemplaza 'tu_proyecto.settings'
    # django.setup()

    logger.info("Inicio del proceso principal del script.")

    # --- Comandos Comentados (Opcional, ejecutar si es necesario) ---
    # logger.info("Ejecutando reset de contraseña (si está descomentado)...")
    # reset(input("usuario: "), input("contraseña: ")) # Cuidado con el input en scripts automáticos

    # logger.info("Ejecutando filtrado de trabajados (si está descomentado)...")
    # # patoba = Patoba(None) # Ya no parece necesario aquí si filtrar_trabajados no lo usa directamente
    # filtrar_trabajados() # Llama a la función local

    # logger.info("Ejecutando asociación de proveedores (si está descomentado)...")
    # asociar_proveedores()


    # --- Procesos Principales ---
    logger.info("Ejecutando procesamiento principal de CSVs...")
    principal_csv()

    logger.info("Ejecutando redondeo personalizado de precios...")
    apply_custom_round()

    logger.info("Proceso principal del script finalizado.")


# --- Sugerencias Finales ---
# 1.  **Configuración de Logging Avanzada:** Para producción, considera configurar el logging usando un diccionario o archivo de configuración. Esto permite definir diferentes manejadores (handlers) como `FileHandler` (para escribir logs a archivos), `RotatingFileHandler` (para rotar archivos de log), y `StreamHandler` (para la consola), con diferentes niveles y formatos para cada uno.
# 2.  **Niveles de Logging:** Usa los niveles de logging apropiadamente:
#     * `logger.debug()`: Información detallada, útil solo para diagnóstico.
#     * `logger.info()`: Mensajes informativos sobre el progreso normal de la aplicación.
#     * `logger.warning()`: Indica que algo inesperado ocurrió, o un problema potencial, pero la aplicación sigue funcionando.
#     * `logger.error()`: Error grave, la aplicación no pudo realizar alguna función.
#     * `logger.critical()`: Error crítico que puede llevar a la detención de la aplicación.
# 3.  **Formato de Logs:** Personaliza el formato de los logs para incluir información útil como timestamp, nivel de log, nombre del módulo, número de línea (`%(asctime)s - %(levelname)s - %(name)s:%(lineno)d - %(message)s`).
# 4.  **Manejo de Excepciones:**
#     * Sé específico en los `except`: En lugar de `except Exception:`, atrapa excepciones más específicas (`except FileNotFoundError:`, `except KeyError:`, `except ValueError:`, `except IntegrityError:`, etc.) cuando sea posible. Esto evita ocultar errores inesperados.
#     * Usa `exc_info=True` en `logger.error()` o `logger.exception()` para incluir automáticamente el traceback de la excepción en el log, lo cual es crucial para depurar. `logger.exception()` es un atajo para `logger.error(..., exc_info=True)`.
# 5.  **Optimización de Consultas:**
#     * En `crear_o_actualizar_registros_en_lotes`, ya se pre-cargan `Sub_Carpeta` y `Sub_Titulo`. Similarmente, se pre-cargan los `Item` existentes. ¡Esto es bueno!
#     * Asegúrate de que los campos usados en `filter()` y `get_or_create()` (como `codigo`, `nombre`) estén indexados en la base de datos para mejorar el rendimiento.
# 6.  **Transacciones:** El uso de `transaction.atomic()` en el procesamiento por lotes es correcto para asegurar la atomicidad de las operaciones dentro de un lote.
# 7.  **Limpieza de Código:** Elimina código comentado (`#print(...)`) si ya no es necesario. Revisa la lógica de escritura en `items.csv` y `errores.csv` para asegurarte de que cumple el propósito deseado.
# 8.  **Validación de Datos:** Añade más validaciones a los datos leídos del CSV antes de intentar crear/actualizar objetos Django para prevenir errores (`IntegrityError`, `ValidationError`). Por ejemplo, validar tipos de datos, longitudes máximas, etc. La función `validar_digitos_str` y el redondeo en `buscar_modificar_registros_lotes` son buenos ejemplos de esto.
# 9.  **Dependencias Externas:** Asegúrate de que las llamadas a servicios externos (como Google Sheets con `Patoba`) tengan manejo de errores robusto (timeouts, errores de API, etc.).
# 10. **Contexto en Logs:** Añade contexto relevante a los mensajes de log, como el nombre del proveedor, el archivo CSV que se está procesando, o el código del item afectado. Esto facilita el seguimiento de problemas. (Ya se hizo en parte al convertir los prints a f-strings con variables).