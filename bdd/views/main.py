# tu_app/views/main.py
import os
from django.shortcuts import render
from django.views.generic import TemplateView, FormView, View
from django.http import JsonResponse, FileResponse
from django.db.models import Exists, OuterRef, Q, BooleanField, Value
from django.apps import apps
from django.core.exceptions import FieldDoesNotExist

# Importa la vista base, formularios y modelos necesarios
from .base import MiVista
from .forms import MyForm, BusquedaForm
from ..models import Item, Cajon, Sector, NavBar, Marca, Cajonera
from x_cartel.models import CartelesCajon, Carteles


import logging

logger = logging.getLogger(__name__)

class Inicio(MiVista):
    # Hereda get_context_data, get y post de MiVista
    # Puedes sobreescribirlos si Inicio necesita lógica adicional
    def get_context_data(self, **kwargs):
        logger.info("Accediendo a la vista Inicio (get_context_data).")
        context = super().get_context_data(**kwargs)
        # Añadir contexto específico para Inicio si es necesario
        # context['mensaje_bienvenida'] = "Bienvenido a la página principal"
        logger.debug("Contexto adicional para Inicio preparado (si hubo).")
        return context

    def get(self, request, *args, **kwargs):
        logger.info("Procesando GET request en Inicio.")
        response = super().get(request, *args, **kwargs)
        logger.info("Finalizado GET request en Inicio.")
        return response

    def post(self, request, *args, **kwargs):
        logger.info("Procesando POST request en Inicio.")
        response = super().post(request, *args, **kwargs)
        logger.info("Finalizado POST request en Inicio.")
        return response


class Prueba(MiVista):
    # Similar a Inicio, hereda todo de MiVista.
    # Sobrescribe si necesitas comportamiento específico para /prueba/
    def get_context_data(self, **kwargs):
        logger.info("Accediendo a la vista Prueba (get_context_data).")
        context = super().get_context_data(**kwargs)
        # Contexto específico para Prueba
        context['titulo_prueba'] = "Página de Prueba"
        return context

    def get(self, request, *args, **kwargs):
         logger.info("Procesando GET request en Prueba.")
         # Puedes añadir lógica antes o después de llamar al padre
         return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
         logger.info("Procesando POST request en Prueba.")
         # Puedes añadir lógica antes o después de llamar al padre
         return super().post(request, *args, **kwargs)


# --- Vista de Búsqueda específica ---
class BusquedaView(FormView):
    """
    Vista de formulario que maneja la lógica de búsqueda y muestra los resultados al usuario.
    """
    template_name = 'plantilla_prueba.html' # Asegúrate que esta plantilla exista
    form_class = BusquedaForm
    # success_url = reverse_lazy('nombre_url_resultado') # O manejar en form_valid

    def get_context_data(self, **kwargs):
        """
        Obtiene el contexto para la plantilla. Agrega todos los sectores al contexto.
        """
        logger.info("Preparando contexto para BusquedaView (GET inicial).")
        context = super().get_context_data(**kwargs)
        context['sectores'] = Sector.objects.all()
        logger.debug(f"Sectores añadidos al contexto: {context['sectores'].count()}")
        return context

    def form_valid(self, form):
        """
        Procesa el formulario cuando es válido (enviado por POST o GET si se configura).
        Filtra los elementos en función de los campos del formulario y agrega los elementos filtrados al contexto.
        """
        logger.info("Formulario de búsqueda válido recibido.")
        marca = form.cleaned_data.get('marca')
        cajon = form.cleaned_data.get('cajon')
        cajonera = form.cleaned_data.get('cajonera')
        sector = form.cleaned_data.get('sector')
        logger.debug(f"Criterios de búsqueda: Marca={marca}, Cajon={cajon}, Cajonera={cajonera}, Sector={sector}")

        items = Item.objects.all()
        if marca:
            items = items.filter(marca=marca)
        if cajon:
            items = items.filter(cajon=cajon)
        if cajonera:
            items = items.filter(cajon__cajonera=cajonera)
        if sector:
            items = items.filter(cajon__cajonera__sector=sector)

        logger.info(f"Búsqueda encontró {items.count()} items.")

        context = self.get_context_data(form=form) # Obtiene contexto base (incluye sectores)
        context['items'] = items # Añade los resultados
        context['busqueda_realizada'] = True # Flag para la plantilla
        return self.render_to_response(context)

    def form_invalid(self, form):
         logger.warning(f"Formulario de búsqueda inválido: {form.errors}")
         return super().form_invalid(form)


# --- Vista para obtener Items de un Cajón (probablemente AJAX) ---
# Podría ir en ajax.py, pero si renderiza algo, puede quedarse aquí.
# Asumiendo que es AJAX basado en el JsonResponse original.
class ItemsView(View):
    def get(self, request, cajon_id):
        logger.info(f"Solicitud GET para ItemsView, cajon_id={cajon_id}")
        try:
            cajon = Cajon.objects.get(id=cajon_id)
            items = Item.objects.filter(cajon=cajon)
            logger.info(f"Encontrados {items.count()} items para el cajón {cajon.codigo}.")

            data = [{
                'id': item.id, # Añadir ID suele ser útil
                'codigo': item.codigo,
                'descripcion': item.descripcion,
                'final': item.final, # Considera el tipo de dato (Decimal -> str)
                 # Añadir otros campos si son necesarios en el frontend
            } for item in items]

            return JsonResponse(data, safe=False)
        except Cajon.DoesNotExist:
             logger.warning(f"Intento de acceder a items de cajón inexistente (ID: {cajon_id}).")
             return JsonResponse({'error': 'Cajón no encontrado'}, status=404)
        except Exception as e:
             logger.error(f"Error en ItemsView para cajon_id={cajon_id}: {e}", exc_info=True)
             return JsonResponse({'error': 'Error interno del servidor'}, status=500)


# --- Vista de Impresión ---
# Esta vista parece compleja y mezcla lógica GET/POST con configuración de contexto.
# Hereda de TemplateView directamente, no de MiVista (según el código original).
class Imprimir(TemplateView):
    template_name = 'generic_template.html' # Usa la plantilla genérica
    ruta_actual = '' # Esto se setea en get_context_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barra_de_navegacion'] = NavBar.objects.all() # Necesario si no hereda de MiVista
        self.ruta_actual = self.request.path
        logger.info(f"Preparando contexto para Imprimir en ruta: {self.ruta_actual}")

        # Lógica condicional basada en la ruta exacta
        if self.ruta_actual == '/imprimir/':
            logger.debug("Configurando contexto para /imprimir/ (Formulario inicial).")
            context['muro'] = 'muro_simple.html'
            context['lista_html'] = ['plantilla_formulario.html']
            lista_campos = ['sub_carpeta','sub_titulo']
            context['lista_formulario_campos'] = lista_campos
            # Usar MyForm para el formulario
            context['form'] = MyForm(model_name='Item', fields_to_show=lista_campos) # Asume modelo Item
            context['boton_form'] = 'Imprimir'
            context['action'] = 'tabla/' # Acción relativa a la URL actual
            context['metodo'] = 'POST'

        elif self.ruta_actual == '/imprimir/tabla/':
             logger.debug("Configurando contexto para /imprimir/tabla/ (Mostrar tabla).")
             context['muro'] = 'muro_imprimir.html'
             context['lista_html'] = ['imprimir_carteles_x6.html']
             # Los campos del formulario podrían venir de la request anterior (POST)
             # o necesitar un formulario GET si se accede directamente
             lista_campos = ['sub_carpeta','sub_titulo'] # Mismos campos?
             context['lista_formulario_campos'] = lista_campos
             # Si se accede por GET a esta URL, ¿mostramos un form o esperamos datos?
             # context['form'] = MyForm(model_name='Item', fields_to_show=lista_campos) # Podría necesitarse
             context['action'] = '' # Acción vacía si el POST se maneja aquí mismo
             context['campos_tabla'] = ['descripcion', 'final', 'final_efectivo', 'final_rollo', 'final_rollo_efectivo', 'actualizado']
             context['titulos_tabla'] = ['Descripcion', 'Publico', 'Efectivo', 'X Cantidad', 'X Cant Efectivo', 'Actualizado?'] # Ajusta títulos
             # Los 'datos' se llenarán en el método POST (o GET si se adapta)
             context['datos'] = kwargs.get('datos', []) # Obtener datos pasados desde POST/GET

        else:
             logger.warning(f"Ruta no manejada explícitamente en Imprimir.get_context_data: {self.ruta_actual}")
             # Configurar un estado por defecto o lanzar error

        return context

    def get(self, request, *args, **kwargs):
        # El GET a /imprimir/ simplemente muestra el formulario inicial
        logger.info(f"Procesando GET request en Imprimir para ruta: {request.path}")
        context = self.get_context_data()
        # Si es /imprimir/tabla/ y se accede por GET, ¿qué mostramos?
        # Podríamos requerir parámetros GET o mostrarla vacía.
        if request.path == '/imprimir/tabla/':
             logger.warning("Acceso GET a /imprimir/tabla/, mostrando tabla vacía o según params GET.")
             # Aquí podrías procesar request.GET si quieres permitir búsquedas GET en esta URL
             context['datos'] = [] # Por defecto vacía en GET
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # El POST probablemente va a /imprimir/ y luego muestra /imprimir/tabla/
        logger.info(f"Procesando POST request en Imprimir para ruta: {request.path}")
        # Determinar qué formulario procesar basado en la ruta o un campo oculto
        # Asumiendo que el POST siempre viene de /imprimir/ hacia /imprimir/tabla/
        lista_campos = ['sub_carpeta','sub_titulo'] # Campos esperados
        form = MyForm(request.POST, model_name='Item', fields_to_show=lista_campos)
        datos_filtrados = []

        if form.is_valid():
            logger.info("Formulario POST de Imprimir válido.")
            form_data = form.cleaned_data
            # Filtrar campos vacíos (¿seguro que quieres esto?)
            form_data = {k: v for k, v in form_data.items() if v}
            logger.debug(f"Datos del formulario para filtrar Items: {form_data}")

            try:
                modelo = apps.get_model('bdd', 'Item')
                # Cuidado: **form_data puede fallar si los nombres no coinciden exactamente con los campos del modelo
                # Sería más seguro construir el filtro explícitamente
                # ej: queryset = modelo.objects.filter(campo_modelo1=form_data.get('sub_carpeta'), ...)
                queryset = modelo.objects.filter(**form_data)
                logger.info(f"Consulta de Items para imprimir encontró {queryset.count()} resultados.")

                # Preparar datos para la tabla /imprimir/tabla/
                campos_tabla = ['descripcion', 'final', 'final_efectivo', 'final_rollo', 'final_rollo_efectivo', 'actualizado']
                # Usar .values() para obtener solo los campos necesarios
                datos_filtrados = list(queryset.values(*campos_tabla))

                # Reordenar columnas si es necesario (values ya puede dar el orden)
                # column_order = campos_tabla
                # ordered_data = []
                # for row in datos_values:
                #     ordered_row = {column: row[column] for column in column_order}
                #     ordered_data.append(ordered_row)
                # datos_filtrados = ordered_data
                logger.debug(f"Datos preparados para la plantilla de tabla: {len(datos_filtrados)} filas.")

            except Exception as e:
                 logger.error(f"Error al filtrar Items para imprimir con datos {form_data}: {e}", exc_info=True)
                 # Pasar el error al contexto para mostrarlo?
                 # context = self.get_context_data(datos=[]) # Asegura contexto base
                 # context['form'] = form # Re-mostrar form con datos
                 # context['print_error'] = "Error al buscar los items."
                 # return self.render_to_response(context)
                 datos_filtrados = [] # Mostrar tabla vacía en caso de error

        else:
             logger.warning(f"Formulario POST de Imprimir inválido: {form.errors}")
             # Re-mostrar el formulario inicial con errores? O ir a tabla vacía?
             # Depende de la UX deseada. Mostremos la tabla vacía por ahora.
             datos_filtrados = []


        # Renderizar la plantilla de la tabla (/imprimir/tabla/) con los datos
        # Necesitamos asegurar que el contexto para '/imprimir/tabla/' esté configurado
        context = self.get_context_data(datos=datos_filtrados) # Pasar datos encontrados
        context['form'] = form # Pasar el form (con errores si los hubo) puede ser útil
        self.request.path = '/imprimir/tabla/' # Simular estar en la URL de la tabla para get_context_data
        context = self.get_context_data(datos=datos_filtrados) # Recalcular contexto para la tabla
        logger.info("Renderizando plantilla de tabla de impresión.")
        return self.render_to_response(context)


# --- Vista ListadoPedidos ---
# Hereda de MiVista, principalmente sobreescribe GET para filtrar
class ListadoPedidos(MiVista):
    def get(self, request, *args, **kwargs):
        logger.info("Procesando GET request en ListadoPedidos.")
        # Llama al get_context_data de MiVista para obtener el contexto base
        # (armador, modelo, etc.)
        context = super().get_context_data(**kwargs)
        model_name = context.get('model_name')
        lista_campos = context.get('lista_formulario_campos', ['None'])
        armador = context.get('armador')
        datos_filtrados = [] # Inicializar

        if model_name and model_name == 'Lista_Pedidos': # Asegurarse que es el modelo correcto
            logger.debug(f"Modelo para ListadoPedidos: {model_name}")
            # Usar request.GET para los filtros
            search_params = request.GET.copy()
            query_params = {k: v for k, v in search_params.items() if v}
            logger.debug(f"Parámetros GET para filtrar Lista_Pedidos: {query_params}")

            filter_kwargs = {}
            model = apps.get_model('bdd', model_name) # Asume app 'bdd'

            campos_contiene = [obj.nombre for obj in armador.formulario_campos_contiene.all()] if armador else []
            campos_empieza = [obj.nombre for obj in armador.formulario_campos_empieza_con.all()] if armador else []

            # Mapeo especial para campos ForeignKey (ej: item -> item__descripcion)
            foreign_keys = {field.name: field.related_model for field in model._meta.get_fields() if isinstance(field, ForeignKey)}

            for k, v in query_params.items():
                field_name = k
                lookup_type = ''

                if field_name in campos_contiene:
                    lookup_type = '__icontains'
                    filter_key = f'{field_name}{lookup_type}'
                    filter_kwargs[filter_key] = v
                elif field_name in campos_empieza:
                    lookup_type = '__istartswith'
                    filter_key = f'{field_name}{lookup_type}'
                    filter_kwargs[filter_key] = v
                # Manejo de FK: si el campo es una FK y el modelo relacionado tiene 'descripcion'
                elif field_name in foreign_keys and hasattr(foreign_keys[field_name], 'descripcion'):
                     # Asume que queremos buscar en la descripción del modelo relacionado
                     filter_key = f'{field_name}__descripcion__icontains' # Busca por descripción relacionada
                     filter_kwargs[filter_key] = v
                     logger.debug(f"Aplicando filtro FK: {filter_key}={v}")
                else:
                    # Coincidencia exacta si es un campo válido del modelo Lista_Pedidos
                    try:
                         model._meta.get_field(field_name)
                         filter_kwargs[field_name] = v
                    except FieldDoesNotExist:
                         logger.warning(f"Parámetro '{field_name}' ignorado en ListadoPedidos (no válido/manejado).")

            logger.debug(f"Filtros finales para Lista_Pedidos: {filter_kwargs}")

            if filter_kwargs:
                try:
                    # Seleccionar campos específicos para la tabla
                    campos_a_mostrar = ['id', 'item__codigo', 'item__descripcion', 'cantidad', 'pedido']
                    queryset = model.objects.filter(**filter_kwargs).select_related('item') # Optimizar FK
                    datos_filtrados = list(queryset.values(*campos_a_mostrar))
                    logger.info(f"Búsqueda en Lista_Pedidos encontró {len(datos_filtrados)} resultados.")
                    # Asegurarse que los títulos coincidan con los campos seleccionados
                    context['titulos'] = campos_a_mostrar # Sobreescribir títulos si es necesario
                except Exception as e:
                     logger.error(f"Error buscando en Lista_Pedidos con filtros {filter_kwargs}: {e}", exc_info=True)
                     context['search_error'] = "Error al realizar la búsqueda de pedidos."
                     datos_filtrados = []
            else:
                 logger.info("No se proporcionaron filtros para ListadoPedidos.")
                 # Podrías mostrar todos los pedidos o ninguno si no hay filtro
                 # queryset = model.objects.all().select_related('item')
                 # datos_filtrados = list(queryset.values(...))
                 datos_filtrados = [] # Mostrar vacío si no hay filtro

        else:
            logger.error(f"ListadoPedidos esperaba modelo 'Lista_Pedidos', pero el Armador indicó '{model_name}'.")
            # Manejar el error apropiadamente

        context['datos'] = datos_filtrados
        # El formulario GET se podría añadir aquí si se quiere mostrar pre-llenado
        # context['form'] = MyForm(request.GET, ...)
        return self.render_to_response(context)

    # El método POST heredado de MiVista podría funcionar si el Armador está configurado
    # para POST en la URL de ListadoPedidos, pero GET es más común para búsquedas.
    # Si POST tiene otra lógica, sobreescríbelo aquí.


# --- Vista ListarCarteles ---
class ListarCarteles(TemplateView):
    template_name = 'generic_template.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Configuración específica de esta vista (difiere de MiVista)
        context['barra_de_navegacion'] = NavBar.objects.all()
        self.ruta_actual = self.request.path
        logger.info(f"Preparando contexto para ListarCarteles en ruta: {self.ruta_actual}")

        # Siempre la misma configuración de muro/html/form?
        context['muro'] = 'muro_doble.html'
        context['lista_html'] = ['plantilla_formulario.html','tabla_listado_carteles_prueva.html']
        lista_formulario_campos = ['proveedor', 'revisar'] # Campos específicos
        # Asegúrate que el modelo 'Carteles' tiene 'proveedor' y 'revisar' como campos válidos
        # o ajusta MyForm para manejar estos campos aunque no estén en el modelo.
        # Si 'Carteles' no es el modelo del form, especifica uno que sí los tenga o usa un form diferente.
        # Asumiendo que 'Carteles' *sí* tiene esos campos o MyForm los ignora si no.
        formulario = MyForm(model_name='Carteles', fields_to_show=lista_formulario_campos) # OJO: Modelo correcto?
        context['form'] = formulario
        context['boton_form'] = 'Buscar'
        context['action'] = '/listar_carteles/' # Acción para el formulario GET
        context['metodo'] = 'GET'
        context['campos_tabla'] = ['descripcion'] # Campos a mostrar en tabla? Solo descripción?
        context['titulos_tabla'] = ['Descripcion']

        # Crear CartelesCajon si no existen (esto debería ir en migrations o un comando)
        try:
            cajones = Cajon.objects.all()
            for cajon in cajones:
                 _, created = CartelesCajon.objects.get_or_create(id=cajon.id)
                 if created:
                      logger.info(f"Creado CartelesCajon para Cajon ID: {cajon.id}")
        except Exception as e:
             logger.error(f"Error asegurando CartelesCajon: {e}", exc_info=True)

        # Añadir datos calculados en GET
        context.update(kwargs.get('extra_context', {})) # Añadir datos pasados desde GET

        return context

    def get(self, request, *args, **kwargs):
        logger.info("Procesando GET request en ListarCarteles.")
        proveedor_id = request.GET.get('proveedor')
        revisar_param = request.GET.get('revisar', 'false').lower() # Default a 'false'
        # Convertir 'revisar' a booleano de forma segura
        filtro_revisar = revisar_param == 'true'
        logger.debug(f"Filtros GET: proveedor_id={proveedor_id}, revisar={filtro_revisar} (param: {revisar_param})")

        # Anotar cajones que tienen items para revisar
        cajones_qs = Cajon.objects.annotate(
            tiene_item_para_revisar=Exists(
                Item.objects.filter(cajon=OuterRef('id'), carteles__revisar=True)
            )
        ).prefetch_related( # Prefetch para optimizar acceso posterior
             'item_set', # Items asociados al cajón
             'item_set__carteles_set' # Carteles asociados a esos items
             )

        # Filtrar cajones
        # Solo mostrar cajones que SÍ tienen items para revisar si filtro_revisar es True
        if filtro_revisar:
             cajones_qs = cajones_qs.filter(tiene_item_para_revisar=True)
             logger.debug("Filtrando cajones: Solo aquellos con items a revisar.")

        if proveedor_id:
            # Filtrar por proveedor, asegurando que el item pertenezca al cajón Y al proveedor
            # Y si filtro_revisar es True, que también necesite revisión.
            proveedor_filter = Q(item__proveedor_id=proveedor_id)
            if filtro_revisar:
                 # Si filtramos por revisar, ya filtramos cajones con items a revisar.
                 # Ahora nos aseguramos que *al menos uno* de esos items sea del proveedor.
                 cajones_qs = cajones_qs.filter(Exists(Item.objects.filter(cajon=OuterRef('id'), proveedor_id=proveedor_id, carteles__revisar=True)))
                 logger.debug(f"Filtrando cajones por proveedor_id={proveedor_id} Y que tengan items de ese proveedor a revisar.")
            else:
                 # Si no filtramos por revisar, mostramos cajones si tienen *cualquier* item de ese proveedor.
                 cajones_qs = cajones_qs.filter(Exists(Item.objects.filter(cajon=OuterRef('id'), proveedor_id=proveedor_id)))
                 logger.debug(f"Filtrando cajones por proveedor_id={proveedor_id} (sin filtro 'revisar' obligatorio).")


        # Procesar items dentro de los cajones filtrados
        # Y filtrar los items *dentro* de cada cajón según 'revisar'
        cajones_list = []
        for cajon in cajones_qs:
            # Filtrar los items del cajón según el parámetro 'revisar'
            items_del_cajon = [
                 item for item in cajon.item_set.all() # Usar prefetch
                 if item.tiene_cartel and (not filtro_revisar or item.carteles_set.filter(revisar=True).exists())
            ]
            if items_del_cajon: # Solo añadir cajón si tiene items relevantes después de filtrar
                 for item in items_del_cajon:
                      item.url = f"/x_cartel/imprimir/{item.id}/" # URL para imprimir
                      item.needs_review = item.carteles_set.filter(revisar=True).exists() # Flag para la plantilla
                 cajon.items_filtrados = items_del_cajon # Guardar items filtrados
                 cajones_list.append(cajon)
                 logger.debug(f"Cajon '{cajon.codigo}' añadido con {len(items_del_cajon)} items filtrados.")

        # Items sin cajón
        items_sin_cajon_qs = Item.objects.filter(tiene_cartel=True, cajon__isnull=True)
        if proveedor_id:
             items_sin_cajon_qs = items_sin_cajon_qs.filter(proveedor_id=proveedor_id)
        if filtro_revisar:
             items_sin_cajon_qs = items_sin_cajon_qs.filter(carteles__revisar=True)

        items_sin_cajon_list = list(items_sin_cajon_qs.prefetch_related('carteles_set'))
        for item in items_sin_cajon_list:
            item.url = f"/x_cartel/imprimir/{item.id}/"
            item.needs_review = item.carteles_set.filter(revisar=True).exists()
        logger.info(f"Encontrados {len(items_sin_cajon_list)} items sin cajón que cumplen criterios.")


        # Preparar contexto extra para pasarlo a get_context_data
        extra_context = {
            'cajones': cajones_list,
            'items_sin_cajon': items_sin_cajon_list,
            'busqueda_realizada': bool(proveedor_id or revisar_param != 'false') # Indica si se aplicó filtro
        }
        context = self.get_context_data(extra_context=extra_context)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        # El POST no parece usarse según el GET, pero si se necesitara:
        logger.warning("Recibida solicitud POST en ListarCarteles, pero no implementada. Redirigiendo a GET?")
        # Podrías procesar el POST si tuviera sentido, o simplemente redirigir a la vista GET.
        # Por ejemplo, procesar la búsqueda POST y luego renderizar como si fuera GET.
        # O simplemente: return redirect('nombre_url_listar_carteles')
        context = self.get_context_data() # Contexto base
        context['post_error'] = "Método POST no soportado actualmente aquí."
        return self.render_to_response(context)