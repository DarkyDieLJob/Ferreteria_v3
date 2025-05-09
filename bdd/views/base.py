# tu_app/views/base.py
import os
import json
import requests
import mercadopago
from datetime import datetime, timedelta

from django.views.generic import TemplateView
from django.template.loader import select_template
from django.shortcuts import redirect
from django.conf import settings
from django.apps import apps
from django.db.models import Exists, OuterRef, QuerySet, ForeignKey

# Importa modelos y formularios necesarios (ajusta según sea necesario)
from ..models import NavBar, Armador, Listado_Planillas, Lista_Pedidos # Importa desde el models.py de la app padre
# Importa el formulario desde el archivo forms.py dentro de este módulo views
from .forms import MyForm
from django.core.exceptions import FieldDoesNotExist

import logging

logger = logging.getLogger(__name__)

class MiVista(TemplateView):
    template_name = 'generic_template.html'
    ruta_actual = ''

    def get_context_data(self, **kwargs):
        logger.info(f"[{self.__class__.__name__}] Iniciando get_context_data para ruta: {self.request.path}")
        context = super().get_context_data(**kwargs)

        # Versión desde package.json
        try:
            dir_file = os.path.join(settings.BASE_DIR, 'package.json')
            with open(dir_file, 'r') as f:
                data = json.load(f)
                context['version'] = data.get('version', 'N/A')
            logger.debug(f"Versión obtenida de package.json: {context['version']}")
        except FileNotFoundError:
            logger.warning("package.json no encontrado.")
            context['version'] = 'N/A'
        except json.JSONDecodeError:
            logger.error("Error al decodificar package.json.")
            context['version'] = 'Error'
        except Exception as e:
             logger.error(f"Error inesperado leyendo package.json: {e}", exc_info=True)
             context['version'] = 'Error'


        # Navegación y Armador
        context['barra_de_navegacion'] = NavBar.objects.all()
        self.ruta_actual = self.request.path
        context['ruta_actual'] = self.ruta_actual
        logger.debug(f"Ruta actual: {self.ruta_actual}")

        try:
            armador = Armador.objects.filter(url=self.ruta_actual).first()
            context['armador'] = armador
            if armador:
                 logger.info(f"Armador encontrado para la ruta: {armador.url}")
                 context['metodo'] = 'GET' if armador.busqueda else 'POST'
                 context['muro'] = armador.muro.muro_html + '.html'
                 contenedor = armador.contenedor
                 model_name = armador.modelo
                 context['model_name'] = model_name
                 logger.debug(f"Armador settings: metodo={context['metodo']}, muro={context['muro']}, modelo={model_name}")

                 # Modelo asociado al armador
                 model = None
                 try:
                     model = apps.get_model('bdd', model_name)
                 except LookupError:
                     logger.warning(f"Modelo '{model_name}' no encontrado en 'bdd', intentando 'x_cartel'.")
                     try:
                         model = apps.get_model('x_cartel', model_name)
                     except LookupError:
                          logger.error(f"Modelo '{model_name}' especificado en Armador no encontrado.")
                 context['model'] = model # Pasar el modelo al contexto puede ser útil

                 # Campos y Títulos del Formulario
                 formulario_campos = armador.formulario_campos.values_list('nombre', flat=True)
                 lista_formulario_campos = list(formulario_campos)
                 context['lista_formulario_campos'] = lista_formulario_campos
                 logger.debug(f"Campos del formulario Armador: {lista_formulario_campos}")
                 formulario = MyForm(model_name=model_name, fields_to_show=lista_formulario_campos)
                 context['form'] = formulario
                 context['boton_form'] = armador.formulario_boton

                 # Títulos de la tabla/listado
                 if model:
                     modelo_campos = list(armador.modelo_campos.values_list('nombre', flat=True))
                     if modelo_campos and modelo_campos[0] == '__all__':
                         titulos = [field.name for field in model._meta.get_fields() if field.name in [f.name for f in model._meta.fields] and not (isinstance(field, ForeignKey) and field.related_model != model)]
                     elif modelo_campos:
                         titulos = [field.name for field in model._meta.get_fields() if field.name in modelo_campos and field.name in [f.name for f in model._meta.fields] and not (isinstance(field, ForeignKey) and field.related_model != model)]
                     else:
                          titulos = [] # Si no hay campos definidos
                          logger.warning(f"Armador {armador.nombre} no tiene modelo_campos definidos.")
                     context['titulos'] = titulos
                     logger.debug(f"Títulos para tabla: {titulos}")
                 else:
                      context['titulos'] = []

                 # Lista de HTMLs del Contenedor
                 lista_html = []
                 campos_contenedor = ['a', 'b', 'c'] # Asumiendo que estos son los campos relevantes en Contenedor
                 for campo in campos_contenedor:
                     try:
                         valor = getattr(contenedor, campo)
                         if valor is None:
                             # logger.debug(f"Campo contenedor '{campo}' es None, deteniendo búsqueda de templates.")
                             break
                         template_name = f'{valor}.html'
                         # Verificar si la plantilla existe
                         try:
                              select_template([template_name])
                              lista_html.append(template_name)
                              logger.debug(f"Template '{template_name}' añadido desde contenedor.")
                         except Exception: # TemplateDoesNotExist más específico sería mejor
                              logger.warning(f"Template '{template_name}' definido en Contenedor no encontrado.")
                     except AttributeError:
                          logger.warning(f"Contenedor asociado al Armador no tiene el campo '{campo}'.")
                     except Exception as e:
                          logger.error(f"Error procesando campo '{campo}' del contenedor: {e}", exc_info=True)

                 context['lista_html'] = lista_html

            else:
                 logger.warning(f"No se encontró Armador para la ruta: {self.ruta_actual}. Algunas partes del contexto pueden faltar.")
                 context['metodo'] = 'GET' # Default
                 context['muro'] = 'muro_default.html' # Un muro por defecto
                 context['model_name'] = None
                 context['form'] = None
                 context['titulos'] = []
                 context['lista_html'] = []
                 # Considera mostrar un mensaje de error o redirigir si el armador es esencial

        except Exception as e:
            logger.error(f"Error crítico obteniendo datos del Armador para ruta {self.ruta_actual}: {e}", exc_info=True)
            # Setear valores por defecto o manejar el error para que la página no falle completamente
            context['armador'] = None
            context['metodo'] = 'GET'
            context['muro'] = 'muro_error.html' # Plantilla de error
            # ... otros defaults


        # Planillas de Descarga
        try:
            context['seleccion_descargar'] = Listado_Planillas.objects.filter(descargar=True).order_by('-id') # Reemplaza [::-1]
            context['nuevas_planillas'] = Listado_Planillas.objects.filter(listo=False, descargar=False).count()
            context['nuevas_planillas_descarga'] = Listado_Planillas.objects.filter(fecha=datetime.now().date(), descargar=True).count()
            logger.debug(f"Planillas para descargar: {context['seleccion_descargar'].count()}, Nuevas: {context['nuevas_planillas']}, Nuevas para hoy: {context['nuevas_planillas_descarga']}")
        except Exception as e:
            logger.error(f"Error al obtener datos de Listado_Planillas: {e}", exc_info=True)
            context['seleccion_descargar'] = []
            context['nuevas_planillas'] = 0
            context['nuevas_planillas_descarga'] = 0


        # Mercado Pago (Últimos 30 min y último día)
        if getattr(settings, 'INTEGRATE_MERCADOPAGO', False) and getattr(settings, 'INTERNET', False): # Usa settings
            try:
                mp_token_file = getattr(settings, 'MP_TOKEN_FILE', './mp_access_token.txt')
                with open(mp_token_file, 'r') as f:
                     mp_token = f.read().strip()
                sdk = mercadopago.SDK(mp_token)
                logger.info("SDK de MercadoPago inicializado.")

                # Función auxiliar para buscar pagos
                def buscar_pagos_mp(begin_date, end_date):
                    filters = {
                        "range": "date_created",
                        "begin_date": begin_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "end_date": end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                        "sort": "date_created", # Ordenar por fecha
                        "criteria": "desc"      # Más recientes primero
                    }
                    logger.debug(f"Buscando pagos MP con filtros: {filters}")
                    result = sdk.payment().search(filters=filters)
                    # MP a veces retorna 200 OK incluso con errores internos
                    if result["status"] != 200 or "results" not in result["response"]:
                         logger.error(f"Error en la respuesta de búsqueda de pagos MP: Status={result['status']}, Response={result['response']}")
                         return []

                    payments = result["response"]["results"]
                    payment_data = []
                    for py in payments:
                        try:
                            date_string = py.get('date_created', '')
                            identificador = py.get('payer', {}).get('id') or py.get('payer_id') # Prioriza payer.id
                            date = datetime.strptime(date_string.split('.')[0], "%Y-%m-%dT%H:%M:%S") # Ignora microsegundos y TZ para simplificar
                            hour = date.strftime("%H:%M:%S")
                            total_paid_amount = py.get('transaction_details', {}).get('total_paid_amount', 0)
                            status = py.get('status', 'N/A')
                            payment_data.append({
                                'hora': hour,
                                'total_pagado': total_paid_amount,
                                'estado': status,
                                'id': identificador,
                            })
                        except (ValueError, KeyError, TypeError) as e:
                             logger.warning(f"Error procesando pago individual de MP (ID: {py.get('id')}): {e}. Pago: {py}")
                             continue # Saltar este pago si hay error
                    return payment_data

                # Pagos últimos 30 mins
                end_date_30m = datetime.now()
                begin_date_30m = end_date_30m - timedelta(minutes=30)
                context['payments'] = buscar_pagos_mp(begin_date_30m, end_date_30m)
                logger.info(f"Se encontraron {len(context['payments'])} pagos en los últimos 30 min.")


                # Pagos último día
                end_date_1d = datetime.now()
                begin_date_1d = end_date_1d - timedelta(days=1)
                context['tabla_mp'] = buscar_pagos_mp(begin_date_1d, end_date_1d)
                logger.info(f"Se encontraron {len(context['tabla_mp'])} pagos en las últimas 24 horas.")
                context['today'] = datetime.now().strftime('%Y-%m-%d')

            except FileNotFoundError:
                logger.error(f"Archivo de token de MercadoPago no encontrado en: {mp_token_file}")
                context['payments'] = []
                context['tabla_mp'] = []
            except Exception as e:
                 logger.error(f"Error inesperado con la integración de MercadoPago: {e}", exc_info=True)
                 context['payments'] = []
                 context['tabla_mp'] = []
        else:
             logger.info("La integración con MercadoPago está desactivada o no hay conexión a internet (según settings).")
             context['payments'] = []
             context['tabla_mp'] = []


        # Links de Pedidos (Hardcodeado) - Mejor mover a BBDD o settings
        context['tabla_link_pedidos'] = getattr(settings, 'TABLA_LINK_PEDIDOS', [])
        logger.debug(f"Links de pedidos cargados: {len(context['tabla_link_pedidos'])}")

        logger.info(f"[{self.__class__.__name__}] Finalizando get_context_data.")
        return context

    def post(self, request, *args, **kwargs):
        logger.info(f"[{self.__class__.__name__}] Recibida solicitud POST en ruta: {request.path}")
        context = self.get_context_data()
        model_name = context.get('model_name')
        lista_campos = context.get('lista_formulario_campos', ['None']) # Default seguro

        if not model_name:
             logger.error("Intento de POST sin model_name definido en el contexto (probablemente Armador no encontrado).")
             # Decide cómo manejar esto: mostrar error, redirigir, etc.
             context['form_errors'] = "Error de configuración: No se pudo determinar el modelo para guardar."
             return self.render_to_response(context)


        form = MyForm(request.POST, model_name=model_name, fields_to_show=lista_campos)

        if form.is_valid():
            logger.info(f"Formulario POST válido para modelo '{model_name}'. Datos: {form.cleaned_data}")
            saved_object = form.save(model_name=model_name)
            if saved_object:
                 logger.info(f"Objeto {model_name} (ID: {saved_object.pk}) guardado/actualizado exitosamente. Redirigiendo.")
                 return redirect(self.request.path) # Redirige a la misma página (patrón PRG)
            else:
                 # El método save de MyForm (modificado) debería haber logueado el error
                 logger.error(f"El método form.save() para {model_name} falló.")
                 context['form_errors'] = "Ocurrió un error al guardar los datos." # Mensaje genérico para el usuario
                 context['form'] = form # Mantener el formulario con los datos ingresados
        else:
            logger.warning(f"Formulario POST inválido para modelo '{model_name}'. Errores: {form.errors}")
            context['form'] = form # Devuelve el formulario con errores

        # Siempre renderiza la respuesta si no hubo redirección
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        logger.info(f"[{self.__class__.__name__}] Recibida solicitud GET en ruta: {request.path}")
        context = self.get_context_data()
        model_name = context.get('model_name')
        lista_campos = context.get('lista_formulario_campos', ['None'])
        titulos = context.get('titulos', []) # Obtener los títulos definidos en get_context_data

        if not model_name:
             logger.warning("Intento de GET (búsqueda) sin model_name definido (Armador no encontrado?).")
             # Renderiza la plantilla base sin datos de búsqueda
             return self.render_to_response(context)

        # Nota: GET request no debería usar MyForm si es solo para búsqueda (a menos que MyForm maneje GET)
        # Vamos a asumir que el Armador indica si es una búsqueda (GET) y los campos a usar
        armador = context.get('armador')
        if armador and armador.busqueda:
             logger.info("Procesando solicitud GET como búsqueda.")
             # Usar request.GET directamente para filtrar
             search_params = request.GET.copy()
             logger.debug(f"Parámetros GET recibidos: {search_params}")

             # Filtrar parámetros vacíos y específicos de paginación/control si los hubiera
             query_params = {k: v for k, v in search_params.items() if v and k not in ['page', 'csrfmiddlewaretoken']} # Ejemplo de exclusión

             # Aplicar lógica __contains o __istartswith basada en Armador
             filter_kwargs = {}
             model = context.get('model')
             if model:
                 campos_contiene = [obj.nombre for obj in armador.formulario_campos_contiene.all()] if armador else []
                 campos_empieza = [obj.nombre for obj in armador.formulario_campos_empieza_con.all()] if armador else []

                 for k, v in query_params.items():
                      field_name = k # Nombre original del campo
                      lookup_type = ''
                      if field_name in campos_contiene:
                           lookup_type = '__icontains' # Usar icontains para case-insensitive
                           filter_key = f'{field_name}{lookup_type}'
                           filter_kwargs[filter_key] = v
                      elif field_name in campos_empieza:
                           lookup_type = '__istartswith' # Usar istartswith
                           filter_key = f'{field_name}{lookup_type}'
                           filter_kwargs[filter_key] = v
                      else:
                           # Si no es un campo especial, intentar coincidencia exacta
                           # Validar que 'k' sea un campo real del modelo antes de añadirlo
                           try:
                                model._meta.get_field(k)
                                filter_kwargs[k] = v
                           except FieldDoesNotExist:
                                logger.warning(f"Parámetro de búsqueda '{k}' ignorado porque no es un campo válido del modelo '{model_name}' ni un campo especial.")


                 logger.debug(f"Filtros aplicados a la query: {filter_kwargs}")

                 if filter_kwargs:
                     try:
                         queryset = model.objects.filter(**filter_kwargs)
                         logger.info(f"Búsqueda en modelo '{model_name}' con filtros {filter_kwargs} encontró {queryset.count()} resultados.")

                         # Anotación para Lista_Pedidos si el modelo es Item
                         if model_name == "Item":
                              logger.debug("Anotando queryset de Item con 'tiene_pedido'.")
                              queryset = queryset.annotate(
                                   tiene_pedido=Exists(
                                       Lista_Pedidos.objects.filter(
                                           item=OuterRef('pk'), pedido=True
                                       )
                                   )
                              )
                              # Asegurarse de que 'tiene_pedido' esté en los títulos si no lo estaba ya
                              if 'tiene_pedido' not in titulos:
                                   titulos.append('tiene_pedido')


                         # Obtener los datos como diccionarios, seleccionando solo los títulos definidos
                         # Usar .values() con los títulos asegura que solo obtenemos lo necesario
                         context['datos'] = list(queryset.values(*titulos))


                     except Exception as e:
                          logger.error(f"Error al ejecutar la búsqueda en modelo '{model_name}' con filtros {filter_kwargs}: {e}", exc_info=True)
                          context['datos'] = []
                          context['search_error'] = "Error al realizar la búsqueda."
                 else:
                     logger.info("No se proporcionaron filtros válidos para la búsqueda GET.")
                     context['datos'] = []
             else:
                  logger.error("No se pudo obtener el modelo para realizar la búsqueda GET.")
                  context['datos'] = []
        else:
             # Si no es una búsqueda (armador.busqueda es False o no hay armador)
             # o si se quiere mostrar un formulario GET vacío
             logger.debug("Procesando solicitud GET estándar (no búsqueda o formulario inicial).")
             # Podrías inicializar un formulario GET aquí si fuera necesario
             # context['form'] = MyForm(request.GET, ...)
             context['datos'] = []


        # Asegurarse de que 'datos' exista en el contexto, aunque esté vacío
        if 'datos' not in context:
             context['datos'] = []

        # No es necesario filtrar aquí si .values(*titulos) ya se usó
        # filtered_data = [{k: v for k, v in d.items() if k in titulos} for d in context['datos']]
        # context['datos'] = filtered_data

        return self.render_to_response(context)