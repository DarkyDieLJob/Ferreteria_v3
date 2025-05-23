from googleapiclient.errors import HttpError
import ast
import io
import logging
import os

import pandas as pd
from django.conf import settings
from django.db.models import Max
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from googleapiclient.http import MediaIoBaseDownload

# Configuración del logger
logger = logging.getLogger(__name__)

# viejo archivo vistas (Asumiendo que son necesarios, aunque parezcan redundantes)
# from bdd.views_old import MiVista as MiVistaOld, MyForm as MyFormOld
# from bdd.views.base import MiVista
# from bdd.views.forms import MyForm
# --> Simplificado para el ejemplo, ajusta según tu estructura real
from bdd.views.base import MiVista
from bdd.views.forms import MyForm
from actualizador.task import agregar_tareas_en_cola


from bdd.classes import Patoba
from bdd.models import Listado_Planillas, Proveedor
from .sincronizador import reckup
# from .task import recolectar_procesar, actualizar, ejecutar_cola_tareas # Comentado si no se usa en este fragmento
# from core_config.celery import app # Comentado si no se usa en este fragmento
import time
import datetime

# Create your views here.

class ActualizarAhora(TemplateView):
    template_name = 'actualizador/actualizar_ahora.html' # Ajusta la ruta si es necesario

    def get(self, request, *args, **kwargs):
        logger.info("Iniciando proceso de actualización inmediata.")
        try:
            # Aqui se le pasa la hora actual mas un minuto
            hora_actual = datetime.datetime.now() + datetime.timedelta(minutes=1)
            agregar_tareas_en_cola(hora_actual)
            logger.info("Proceso de actualización inmediata completado.")
            return HttpResponse("La actualización ha sido realizada correctamente.")
        except Exception as e:
            logger.error("Error durante el proceso de actualización inmediata:")
            logger.exception(e)
            return HttpResponse(f"Error al realizar la actualización: {e}", status=500)

class Actualizar(MiVista):
    def get_context_data(self, **kwargs):
        self.context = super().get_context_data(**kwargs)
        self.context['lista_html'] = ['actualizar.html',]

        patoba = Patoba(request=self.request)
        self.drive_service = patoba.drive_service
        logger.debug(f"Detectando path: {self.request.path}")

        datos = Listado_Planillas.objects.filter(listo=False, descargar=False)
        hojas_por_item = []
        ids_a_borrar_por_404 = [] # Opcional: para borrar en bloque después

        # Es buena idea iterar sobre una lista fija si vas a modificar la tabla
        # durante la iteración, aunque .delete() dentro del bucle suele funcionar.
        # datos_list = list(datos) # Descomenta si prefieres iterar sobre una lista

        for dato in datos: # o 'datos_list'
            sheet_names = ["",]
            try:
                # Descargar el archivo de Excel desde Google Drive
                logger.debug(f"Intentando descargar archivo de Drive: ID={dato.identificador}, Nombre='{dato.descripcion}'")
                request_drive = self.drive_service.files().get_media(fileId=dato.identificador)
                file = io.BytesIO()
                downloader = MediaIoBaseDownload(file, request_drive)
                done = False
                while not done:
                    # Esta línea puede lanzar HttpError 404
                    status, done = downloader.next_chunk()
                    if status: # status puede ser None si la descarga es muy pequeña
                        logger.debug(f"Progreso descarga {dato.identificador}: {int(status.progress() * 100)}%")

                # Leer el contenido del archivo de Excel
                file.seek(0)
                xls = pd.read_excel(file, sheet_name=None)

                # Obtener los nombres de las hojas
                sheet_names.extend(xls.keys())
                hojas_por_item.append(sheet_names)
                logger.debug(f"Archivo {dato.identificador} leído, hojas: {sheet_names}")

            except HttpError as http_error:
                # ¡Captura específica para errores HTTP de la API!
                if http_error.resp.status == 404:
                    # El archivo no existe en Google Drive
                    logger.warning(f"Archivo no encontrado en Drive (404): ID={dato.identificador}, Nombre='{dato.descripcion}'. Eliminando registro ID={dato.id}.")
                    try:
                        dato_id_para_borrar = dato.id # Guarda el ID por si acaso
                        dato.delete() # Elimina el registro inconsistente de la BD
                        logger.info(f"Registro Listado_Planillas con ID={dato_id_para_borrar} eliminado.")
                        # NO AÑADAS NADA a hojas_por_item para este registro eliminado
                        # Simplemente continuamos al siguiente 'dato' en el bucle
                        continue # Importante: salta el resto del bloque try y el except genérico
                    except Exception as delete_error:
                        # Loggear si incluso la eliminación falla
                        logger.error(f"¡FALLO AL ELIMINAR! Error al intentar eliminar el registro ID={dato_id_para_borrar} después de un 404: {delete_error}")
                        # Decide qué hacer aquí. ¿Añadir lista vacía igualmente?
                        hojas_por_item.append([]) # Mantiene la correspondencia si la eliminación falla
                else:
                    # Otro error HTTP (ej. 403 Forbidden, 500 Server Error)
                    logger.error(f"Error HTTP ({http_error.resp.status}) al descargar archivo ID={dato.identificador}, Nombre='{dato.descripcion}': {http_error}")
                    hojas_por_item.append([]) # Añade lista vacía porque no se pudo procesar

            except Exception as e:
                # Captura cualquier otro error (ej. error de Pandas, problema de red antes de respuesta HTTP)
                logger.error(f"Error genérico al procesar archivo ID={dato.identificador}, Nombre='{dato.descripcion}'")
                logger.exception(e) # Loggea el traceback completo
                hojas_por_item.append([]) # Añade lista vacía para mantener correspondencia

        # IMPORTANTE: Si eliminaste registros DENTRO del bucle, la variable 'datos' original
        # (si era un QuerySet que no convertiste a lista) podría comportarse de forma
        # inesperada si la reutilizas. Además, self.context['datos'] debe reflejar
        # el estado ACTUAL de la base de datos para que coincida con 'hojas_por_item'.
        # Es más seguro volver a consultar los datos que SÍ existen.

        self.context['datos'] = Listado_Planillas.objects.filter(listo=False, descargar=False)
        self.context['hojas_por_item'] = hojas_por_item
        seleccion_planillas = Listado_Planillas.objects.filter(listo=True)
        self.context['seleccion_planillas'] = seleccion_planillas

        # Asegúrate que MyForm y los campos se inicializan correctamente
        # Puede que necesites ajustar esto si 'model_name' o 'lista_formulario_campos' no están
        if 'model_name' in self.context and 'lista_formulario_campos' in self.context:
             formulario = MyForm(model_name=self.context['model_name'],fields_to_show=self.context['lista_formulario_campos'])
             self.context['form'] = formulario
        else:
             logger.warning("Contexto no contiene 'model_name' o 'lista_formulario_campos' para inicializar MyForm")
             self.context['form'] = None # O alguna inicialización por defecto

        self.context['seleccion_planillas'] = Listado_Planillas.objects.filter(listo=True, descargar=False)
        self.context['seleccion_descargar'] = Listado_Planillas.objects.filter(descargar=True).reverse() # Usar reverse() en lugar de [::-1]

        # --- Lógica de limpieza de archivos viejos ---
        logger.info("Iniciando limpieza de archivos y registros antiguos de planillas.")
        # Obtén el archivo más reciente de cada proveedor
        latest_files = Listado_Planillas.objects.values('proveedor').annotate(latest_date=Max('fecha'))

        # Optimización: Obtener todos los IDs a borrar en una sola consulta por proveedor
        ids_to_delete = []
        files_to_delete = []

        for latest_file in latest_files:
            proveedor_id = latest_file['proveedor']
            latest_date = latest_file['latest_date']
            if proveedor_id is None: # Saltar si no hay proveedor asociado
                continue

            # Obtén todos los archivos de este proveedor que no sean el más reciente
            old_files_qs = Listado_Planillas.objects.filter(proveedor_id=proveedor_id).exclude(fecha=latest_date)

            for old_file in old_files_qs:
                ids_to_delete.append(old_file.id)
                # Construye las rutas a los archivos físicos
                file_path_xlsx = os.path.join(settings.MEDIA_ROOT, 'descargas', f'{old_file.proveedor}-{old_file.fecha}.xlsx')
                file_path_ods = os.path.join(settings.MEDIA_ROOT, 'descargas', f'{old_file.proveedor}-{old_file.fecha}.ods')
                files_to_delete.append(file_path_xlsx)
                files_to_delete.append(file_path_ods)

        # Elimina los archivos físicos
        for file_path in files_to_delete:
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Archivo físico eliminado: {file_path}")
                except OSError as e:
                    logger.error(f"No se pudo eliminar el archivo físico {file_path}: {e}")

        # Elimina los registros de la base de datos en bloque
        if ids_to_delete:
            deleted_count, _ = Listado_Planillas.objects.filter(id__in=ids_to_delete).delete()
            logger.info(f"Se eliminaron {deleted_count} registros antiguos de Listado_Planillas.")
        else:
             logger.info("No se encontraron registros antiguos de planillas para eliminar.")
        # --- Fin Lógica de limpieza ---

        return self.context

    def get(self, request, *args, **kwargs):
        logger.debug("Procesando solicitud GET")
        self.context = self.get_context_data()
        logger.debug(f"Datos GET recibidos: {self.request.GET}")
        logger.debug(f"Contexto 'datos' en GET: {self.context.get('datos', 'No disponible')}") # Usar .get para evitar KeyError
        return self.render_to_response(self.context)

    def post(self, request, *args, **kwargs):
        logger.debug("Procesando solicitud POST")
        # Es más eficiente obtener el contexto una vez si no cambia mucho entre ramas
        # Si cambia significativamente, muévelo dentro de las ramas if/else
        # self.context = self.get_context_data() # Llamar get_context_data puede ser costoso, considera si es necesario aquí

        logger.debug(f"Datos POST recibidos: {self.request.POST}")
        # logger.debug(f"Contexto 'seleccion_planillas' antes de procesar POST: {self.context.get('seleccion_planillas', 'No disponible')}")

        logger.debug("Verificando datos del formulario POST...")
        lista_debug = ["tipo-boton", "actualizar_planillas", "descargar"] # Campos clave a verificar
        for name in lista_debug:
            logger.debug(f"POST parameter '{name}': {self.request.POST.get(name)}")

        # Manejo de la lógica de 'actualizar_planillas'
        if self.request.POST.get('actualizar_planillas') != 'True':
            logger.info("Procesando selección/actualización de estado 'listo' de planillas.")
            elementos_seleccionados = self.request.POST.getlist('elemento_seleccionado')
            proveedores_post = self.request.POST.getlist('proveedor') # Renombrado para evitar confusión

            # Reiniciar 'listo' podría hacerse más eficientemente si es necesario
            # Listado_Planillas.objects.update(listo=False) # CUIDADO: Esto afecta a TODAS las planillas

            elementos_a_actualizar = []
            ids_procesados = set()

            for i, elemento in enumerate(elementos_seleccionados):
                try:
                    id_str, _ = elemento.split(':') # El índice 'i' de POST no se usa aquí
                    planilla_id = int(id_str)
                    ids_procesados.add(planilla_id)

                    planilla = Listado_Planillas.objects.get(id=planilla_id)

                    # Determinar si la planilla debe marcarse como lista
                    # Asumiendo que 'elemento_seleccionado' viene como 'id:indice' o 'id:' si no se selecciona hoja
                    _, hoja_indice_str = elemento.split(':')
                    if hoja_indice_str == "":
                        planilla.listo = False
                        logger.debug(f"Planilla ID {planilla_id} marcada como NO lista.")
                    else:
                        planilla.listo = True
                        # Asignar proveedor si se proporcionó uno válido en la misma posición
                        if i < len(proveedores_post) and proveedores_post[i]:
                            try:
                                proveedor_obj = Proveedor.objects.get(id=proveedores_post[i])
                                planilla.proveedor = proveedor_obj
                                logger.debug(f"Planilla ID {planilla_id}: Proveedor asignado ID {proveedores_post[i]}.")
                            except Proveedor.DoesNotExist:
                                logger.warning(f"Proveedor ID {proveedores_post[i]} no encontrado para planilla ID {planilla_id}.")
                        else:
                            logger.warning(f"Proveedor vacío o índice fuera de rango para planilla ID {planilla_id} en la posición {i}.")

                        # Asignar hoja si se proporcionó
                        hoja_nombre = self.request.POST.get(f'hoja_{planilla_id}')
                        if hoja_nombre: # No comparar con "" explícitamente, None o '' son falsy
                            planilla.hoja = hoja_nombre
                            logger.debug(f"Planilla ID {planilla_id}: Hoja asignada '{hoja_nombre}'.")
                        else:
                             planilla.hoja = None # O el valor por defecto que uses

                        logger.debug(f"Planilla ID {planilla_id} marcada como lista.")

                    elementos_a_actualizar.append(planilla)

                except (ValueError, Listado_Planillas.DoesNotExist) as e:
                    logger.error(f"Error procesando elemento seleccionado '{elemento}': {e}")

            # Actualizar en bloque si es posible (Django >= 2.2)
            if hasattr(Listado_Planillas.objects, 'bulk_update') and elementos_a_actualizar:
                campos_a_actualizar = ['listo', 'proveedor', 'hoja']
                Listado_Planillas.objects.bulk_update(elementos_a_actualizar, campos_a_actualizar)
                logger.info(f"Actualizadas {len(elementos_a_actualizar)} planillas en bloque.")
            else: # Fallback para versiones antiguas o si prefieres guardar individualmente
                for planilla in elementos_a_actualizar:
                    planilla.save()
                logger.info(f"Actualizadas {len(elementos_a_actualizar)} planillas individualmente.")

            # Desmarcar las que no vinieron en la selección (si esa es la lógica deseada)
            # planillas_no_seleccionadas = Listado_Planillas.objects.exclude(id__in=ids_procesados)
            # count_desmarcadas = planillas_no_seleccionadas.update(listo=False)
            # if count_desmarcadas > 0:
            #    logger.info(f"{count_desmarcadas} planillas desmarcadas como no listas.")

            # Actualizar contexto después de los cambios
            self.context = self.get_context_data() # Recalcular contexto completo
            logger.debug(f"Contexto 'seleccion_planillas' después de actualizar: {self.context.get('seleccion_planillas', 'No disponible')}")

        else: # actualizar_planillas == 'True'
            logger.info("Iniciando proceso de actualización/descarga de planillas seleccionadas.")
            id_carpeta_inbox = settings.INBOX
            id_carpeta_plantillas = settings.PLANTILLAS
            id_carpeta_descargar = settings.DESCARGAR
            patoba = Patoba(request=self.request)

            ids_post = self.request.POST.getlist('seleccionados') # Debería ser solo uno con la lista como string
            ids_enviar = []
            mi_diccionario = {} # Para el ZIP

            if ids_post:
                try:
                    # Asumiendo que 'seleccionados' contiene algo como "['1', '2', '3']"
                    ids_list_str = ids_post[0]
                    ids_list = ast.literal_eval(ids_list_str)
                    ids_enviar = [int(id_val) for id_val in ids_list]
                    logger.debug(f"IDs de planillas para actualizar/descargar recibidos: {ids_enviar}")
                except (IndexError, ValueError, SyntaxError) as e:
                    logger.error(f"Error al parsear 'seleccionados' POST data ('{ids_post}'): {e}")
                    ids_enviar = [] # Asegurar que la lista esté vacía si hay error
            else:
                logger.warning("No se recibieron IDs en 'seleccionados' para actualizar.")


            if ids_enviar:
                seleccion_planillas_proc = Listado_Planillas.objects.filter(id__in=ids_enviar)
                for sp in seleccion_planillas_proc:
                    nombre_proveedor_desc = sp.descripcion # El nombre original del archivo
                    nombre_plantilla_gdrive = str(sp.proveedor) # Asumiendo que el __str__ del modelo Proveedor es el nombre en Drive
                    nombre_descargable = f"{sp.proveedor}-{sp.fecha}" # Nombre final
                    hoja_seleccionada = sp.hoja

                    logger.info(f"Procesando planilla ID {sp.id}: proveedor_desc='{nombre_proveedor_desc}', plantilla_gdrive='{nombre_plantilla_gdrive}', nombre_final='{nombre_descargable}', hoja='{hoja_seleccionada}'")

                    # Validar que la hoja seleccionada existe
                    if not hoja_seleccionada:
                        logger.warning(f"Planilla ID {sp.id} no tiene hoja seleccionada. Saltando procesamiento Drive.")
                        sp.listo = False # Marcar como no lista si falta la hoja? O manejar diferente?
                        sp.save()
                        continue # Saltar al siguiente

                    try:
                        id_archivo_proveedor = patoba.obtener_id_por_nombre(
                            nombre_proveedor_desc, id_carpeta_inbox)

                        id_archivo_plantilla = patoba.obtener_id_por_nombre(
                            nombre_plantilla_gdrive, id_carpeta_plantillas)

                        if not id_archivo_plantilla:
                             logger.error(f"No se encontró la plantilla '{nombre_plantilla_gdrive}' en Drive (Carpeta ID: {id_carpeta_plantillas}). Saltando planilla ID {sp.id}.")
                             continue

                        id_hoja_reemplazable = patoba.obtener_id_hoja_por_nombre(
                            "Reemplazable", id_archivo_plantilla)

                        if not id_hoja_reemplazable:
                             logger.error(f"No se encontró la hoja 'Reemplazable' en la plantilla '{nombre_plantilla_gdrive}' (ID: {id_archivo_plantilla}). Saltando planilla ID {sp.id}.")
                             continue

                        if id_archivo_proveedor:
                            # La descarga y lectura de la hoja del proveedor ya no parece necesaria aquí
                            # si solo vas a copiar la hoja 'Reemplazable'
                            logger.debug(f"Encontrado archivo proveedor '{nombre_proveedor_desc}' (ID: {id_archivo_proveedor}) y plantilla '{nombre_plantilla_gdrive}' (ID: {id_archivo_plantilla})")

                            # Copiar la hoja 'Reemplazable' de la plantilla al archivo descargable
                            patoba.copiar_reemplazable(
                                id_archivo_proveedor, # Este argumento parece incorrecto si copias desde plantilla
                                hoja_seleccionada,    # Este argumento parece incorrecto si copias desde plantilla
                                id_hoja_reemplazable, # ID de la hoja a copiar (de la plantilla)
                                id_archivo_plantilla) # ID del archivo plantilla (fuente)
                            # REVISAR LA LÓGICA DE patoba.copiar_reemplazable, los argumentos parecen confusos.
                            # ¿Quizás debería ser algo como patoba.copiar_hoja(id_plantilla, id_hoja_reemplazable, id_nuevo_archivo, "NuevoNombreHoja")?

                            # Crear/Buscar copia en Descargas y obtener su ID
                            identificador_descarga = patoba.crear_buscar_copia_descarga(id_archivo_plantilla, id_carpeta_descargar, nombre_descargable) # Pasar nombre deseado
                            # La función anterior debería devolver el ID del archivo creado/encontrado en descargas

                            if identificador_descarga:
                                logger.info(f"Archivo creado/encontrado en Descargas: nombre='{nombre_descargable}', identificador='{identificador_descarga}'")
                                mi_diccionario[str(nombre_descargable)] = str(identificador_descarga)
                                sp.descargar = True # Marcar para posible descarga ZIP
                                sp.identificador_descarga = identificador_descarga # Guardar ID de descarga si es necesario
                            else:
                                logger.error(f"No se pudo crear o encontrar la copia en la carpeta de descargas para '{nombre_descargable}'.")
                                sp.listo = False # Falló el proceso

                        else:
                            logger.warning(f"No se encontró el archivo proveedor '{nombre_proveedor_desc}' en la carpeta Inbox (ID: {id_carpeta_inbox}) para planilla ID {sp.id}.")
                            sp.listo = False # Marcar como no lista si falta el archivo fuente

                        sp.save()

                    except Exception as drive_error:
                        logger.error(f"Error durante el procesamiento con Google Drive para planilla ID {sp.id}:")
                        logger.exception(drive_error)
                        sp.listo = False
                        sp.save()

                logger.debug(f"Diccionario para posible descarga zip: {mi_diccionario}")

            # Actualizar contexto al final de esta rama también
            self.context = self.get_context_data()

            # Lógica de descarga ZIP
            if self.request.POST.get('descargar') == 'True':
                if mi_diccionario:
                    logger.info("Iniciando descarga de archivos procesados como ZIP.")
                    try:
                        zip_content = patoba.download_and_zip_files(mi_diccionario)
                        response = HttpResponse(zip_content, content_type='application/zip')
                        response['Content-Disposition'] = 'attachment; filename=planillas_procesadas.zip' # Nombre más descriptivo
                        logger.info("Archivo ZIP generado y enviado como respuesta.")
                        return response
                    except Exception as zip_error:
                         logger.error("Error al generar o descargar el archivo ZIP:")
                         logger.exception(zip_error)
                         # Podrías renderizar una página de error aquí o redirigir
                else:
                    logger.warning("Se solicitó descargar ZIP, pero no hay archivos procesados exitosamente en el diccionario.")


        # Lógica de borrado al final (se ejecuta independientemente de las ramas anteriores)
        ids_borrar = self.request.POST.getlist('seleccionado_borrar')
        if ids_borrar:
             # Convertir a enteros para la consulta
             try:
                 ids_borrar_int = [int(id_val) for id_val in ids_borrar]
                 logger.info(f"Solicitud para borrar planillas con IDs: {ids_borrar_int}")
                 deleted_count, _ = Listado_Planillas.objects.filter(id__in=ids_borrar_int).delete()
                 logger.info(f"Se eliminaron {deleted_count} planillas.")
                 # Actualizar contexto después de borrar
                 self.context = self.get_context_data()
             except ValueError:
                 logger.error(f"Error al convertir IDs a borrar a enteros: {ids_borrar}")


        # Renderizar la respuesta HTML final (si no se retornó el ZIP)
        # Asegúrate que el contexto esté actualizado si hubo cambios
        # self.context['datos'] = Listado_Planillas.objects.filter(listo=False, descargar=False).reverse() # Esto ya debería estar en get_context_data
        logger.debug("Renderizando respuesta HTML final.")
        return self.render_to_response(self.context)


class Reckup(TemplateView):
    template_name = 'actualizador/reckup.html' # Ajusta la ruta si es necesario

    def get(self, request, *args, **kwargs):
        logger.info("Iniciando proceso de Reckup (descarga de base de datos).")
        try:
            reckup() # Asumiendo que esta función maneja sus propios logs internos si es necesario
            logger.info("Proceso Reckup completado exitosamente.")
            return HttpResponse("La base de datos ha sido descargada correctamente.")
        except Exception as e:
            logger.error("Error durante el proceso de Reckup:")
            logger.exception(e)
            # Considera devolver una respuesta de error más informativa
            return HttpResponse(f"Error al descargar la base de datos: {e}", status=500)