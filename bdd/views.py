from re import L
from django.apps import apps
from django.template.loader import render_to_string, select_template
from django.views.generic import TemplateView
from .models import Armador, NavBar, Item, Listado_Planillas, Proveedor
from django.shortcuts import redirect
from django.db.models import ForeignKey
from django import forms
from django.apps import apps
import os
import io
from googleapiclient.http import MediaIoBaseDownload
import pandas as pd
import mercadopago
from datetime import datetime, timedelta
from .classes import Patoba
from django.http import HttpResponse
from .funtions import get_emails
import ast
from django.conf import settings as cosnt
import requests
from django.db.models import ForeignKey
from .models import Articulo
from django.views.generic.edit import FormView
from django import forms
from .models import Marca, Cajon, Cajonera, Sector, Item ,ArticuloSinRegistro
from django.views.generic import View
from django.http import JsonResponse
from .models import Cajon
from django.http import JsonResponse
from .models import Lista_Pedidos, ListaProveedores
import json
from django.shortcuts import render
from django.http import JsonResponse    
from .models import Carrito
from django.core import serializers
from django.db.models import F
from django.contrib.auth.models import User
from x_cartel.models import Carteles, CartelesCajon
import os
from django.conf import settings
from django.http import FileResponse
from django.db.models import Exists, OuterRef


class DateInput(forms.DateInput):
    """
    Widget personalizado para campos de fecha.
    Establece el tipo de entrada a 'date'.
    """
    input_type = 'date'

class TimeInput(forms.TimeInput):
    """
    Widget personalizado para campos de tiempo.
    Establece el tipo de entrada a 'time'.
    """
    input_type = 'time'

class DateTimeInput(forms.DateTimeInput):
    """
    Widget personalizado para campos de fecha y hora.
    Establece el tipo de entrada a 'datetime-local'.
    """
    input_type = 'datetime-local'

class EmailInput(forms.EmailInput):
    """
    Widget personalizado para campos de correo electrónico.
    Establece el tipo de entrada a 'email'.
    """
    input_type = 'email'

class MyForm(forms.Form):
    """
    Formulario personalizado que construye dinámicamente un conjunto de campos de formulario
    basados en un modelo y una lista de campos especificados.

    Parámetros:
        model_name (str): El nombre del modelo en el que se basará el formulario.
        fields_to_show (list): Una lista de nombres de campo para mostrar en el formulario. 
                                Si es ['__all__'], se mostrarán todos los campos del modelo. 
                                Si es ['None'], no se mostrará ningún campo.

    Métodos:
        save(self, model_name): Crea una nueva instancia del modelo con los datos del formulario,
                                    la valida y luego la guarda en la base de datos.
                                    
        Parámetros:
            model_name (str): El nombre del modelo en el que se basará la nueva instancia.
            
        Devuelve:
            None
    """
    def __init__(self, *args, **kwargs):
        model_name = kwargs.pop('model_name')
        fields_to_show = kwargs.pop('fields_to_show')
        try:
            model = apps.get_model(app_label='bdd', model_name=model_name)
        except:
            pass
        try:
            model = apps.get_model(app_label='x_cartel', model_name=model_name)
        except:
            pass
        super(MyForm, self).__init__(*args, **kwargs)
        if fields_to_show == ['__all__']:
            fields = model._meta.fields
        elif fields_to_show == ['None']:
            fields = []
        else:
            fields = [model._meta.get_field(field_name) for field_name in fields_to_show]
        for field in fields:
            if field.name == 'id':
                continue
            formfield = field.formfield()
            if formfield is None:
                print(f"El campo {field.name} no tiene un campo de formulario válido")
            else:
                self.fields[field.name] = formfield
        for field_name in self.fields:
            if isinstance(self.fields[field_name], forms.DateField):
                self.fields[field_name].widget = DateInput()
            elif isinstance(self.fields[field_name], forms.TimeField):
                self.fields[field_name].widget = TimeInput()
            elif isinstance(self.fields[field_name], forms.DateTimeField):
                self.fields[field_name].widget = DateTimeInput()
            elif isinstance(self.fields[field_name], forms.EmailField):
                self.fields[field_name].widget = EmailInput()

    def save(self, model_name):
        form_data = self.cleaned_data
        model = apps.get_model('bdd', model_name)
        obj = model(**form_data)
        obj.full_clean()
        obj.save()
        #print(form_data)


class MiVista(TemplateView):
    template_name = 'generic_template.html'
    ruta_actual = ''
    def get_context_data(self, **kwargs):
        '''Se genera el contexto principal de una vista primaria (padre) de el resto
        de las vistas.'''
        
        
        #---------------------------------------------------
        # Seteo basico desde el armador, futuro andamio
        
        context = super().get_context_data(**kwargs)
        dir_file = os.path.join(settings.BASE_DIR, 'package.json')
        with open(dir_file, 'r') as f:
            data = json.load(f)
            context['version'] = data['version']


        context['barra_de_navegacion'] = NavBar.objects.all()
        self.ruta_actual = self.request.path
        context['ruta_actual'] = self.ruta_actual
        ruta_actual = self.ruta_actual
        ruta_completa = self.request.get_full_path()
        arm = Armador.objects.all()
        armador = Armador.objects.filter(url=ruta_actual).first()
        print(ruta_actual)
        print(armador)
        context['armador'] = armador
        try:
            if armador.busqueda:
                context['metodo'] = 'GET'
            else:
                context['metodo'] = 'POST'
        except:
            pass
        lista_html = []
        context['muro'] = armador.muro.muro_html+'.html'
        contenedor = armador.contenedor
        model_name = armador.modelo
        context['model_name'] = model_name
        try:
            model = apps.get_model('bdd', model_name)
        except:
            pass
        try:
            model = apps.get_model('x_cartel', model_name)
        except:
            pass
        
        # ---------------------------------------------------------------------------
        # Formularios desde armador, futuro andamios
        
        formulario_campos = armador.formulario_campos.values_list('nombre', flat=True)
        lista_formulario_campos = list(formulario_campos)
        print('lista: ',lista_formulario_campos)
        context['lista_formulario_campos'] = lista_formulario_campos
        formulario = MyForm(model_name=model_name, fields_to_show=lista_formulario_campos)
        context['form'] = formulario
        modelo_campos = list(armador.modelo_campos.values_list('nombre', flat=True))
        if modelo_campos[0] == '__all__':
            titulos = [field.name for field in model._meta.get_fields() if field.name in [f.name for f in model._meta.fields] and not (isinstance(field, ForeignKey) and field.related_model != model)]
        else:
            titulos = [field.name for field in model._meta.get_fields() if field.name in modelo_campos and field.name in [f.name for f in model._meta.fields] and not (isinstance(field, ForeignKey) and field.related_model != model)]
        context['titulos'] = titulos
        context['boton_form'] = armador.formulario_boton
        campos = [field.name for field in contenedor._meta.get_fields() if field.name in ['a', 'b', 'c']]
        for campo in campos:
            valor = getattr(contenedor, campo)
            if valor == None:
                break
            template_name = f'{valor}.html'
            print("valor: ",template_name)
            try:
                template = select_template([template_name])
            except Exception as e:
                template = None
                print(e)
            if template:
                lista_html.append(template_name)
                print("lista_html: ",lista_html)
        context['lista_html'] = lista_html

        #--------------------------------------------------------------------------------------
        # Planillas de descargas para etiquetar Actualizador
        
        context['seleccion_descargar'] = Listado_Planillas.objects.filter(descargar=True)[::-1]
        
        lista = Listado_Planillas.objects.filter(listo=False, descargar=False)
        context['nuevas_planillas'] = lista.count()

        lista = Listado_Planillas.objects.filter(fecha=datetime.now(), descargar=True)
        context['nuevas_planillas_descarga'] = lista.count()
        
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        try: # Extraer precio del dolar de la casa de cambio:
            url = 'https://api.estadisticasbcra.com/var_usd_vs_usd_of'
            headers = {'Authorization': '{BEARER eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MjQyNzUyODMsInR5cGUiOiJleHRlcm5hbCIsInVzZXIiOiJkYXJreWRpZWxAZ21hbC5jb20ifQ.GgcNKy1yXah2ASGm3f0-VgLuR33-TlkWnjSMde_mkUmKtsdfKcw4eeOb8j-wKYA7Q10NO_OYo29MFW9nz_6GIw}'}
            requests.url = url
            requests.headers = headers
            requests.send()
            response = requests.get(url, headers=headers)
            data = response.json()
            context['response'] = data
            for item in data:
                if item["casa"]["nombre"] == "Dolar Blue":
                    context['compra'] = item["casa"]["compra"]
                    context['venta'] = item["casa"]["venta"]
        except Exception as e:
            context['Error'] = str(e)
        #---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        try:
            if settings.INTERNET:
                with open('./mp_access_token.txt', 'r') as f:
                    sdk = mercadopago.SDK(f.read().strip())
                # Establece el rango de tiempo para los últimos 30 minutos
                end_date = datetime.now()
                begin_date = end_date - timedelta(minutes=30)

                filters = {
                    "range": "date_created",
                    "begin_date": begin_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "end_date": end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                }

                result = sdk.payment().search(filters=filters)

                if "results" in result["response"]:
                    payments = result["response"]["results"]
                    payment_data = []
                    for py in payments:
                        for charge in py['charges_details']:
                            date_string = charge['date_created']
                        try:
                            identificador = py["payer_id"]
                        except:
                            pass
                        try:
                            identificador = py["payer"]["id"]
                        except:
                            pass
                        date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z")
                        hour = date.strftime("%H:%M:%S")
                        total_paid_amount = py['transaction_details']['total_paid_amount']
                        status = py['status']
                        payment_data.append({
                            'hora': hour,
                            'total_pagado': total_paid_amount,
                            'estado': status,
                            'id': identificador,
                        })
                    payment_data.reverse()
                else:
                    print("Error al buscar pagos:", result["response"])

                context['payments'] = payment_data

                # Establece el rango de tiempo para el último día
                end_date = datetime.now()
                begin_date = end_date - timedelta(days=1)

                filters = {
                    "range": "date_created",
                    "begin_date": begin_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "end_date": end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                }

                result = sdk.payment().search(filters=filters)

                if "results" in result["response"]:
                    payments = result["response"]["results"]
                    payment_data = []
                    date_string = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                    for py in payments:
                        for charge in py['charges_details']:
                            date_string = charge['date_created']
                        try:
                            identificador = py["payer_id"]
                        except:
                            pass
                        try:
                            identificador = py["payer"]["id"]
                        except:
                            pass
                        try:
                            date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%f%z")
                        except ValueError:
                            try:
                                date = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
                            except ValueError:
                                print("Formato de fecha desconocido: ", date_string)
                        hour = date.strftime("%H:%M:%S")
                        total_paid_amount = py['transaction_details']['total_paid_amount']
                        status = py['status']
                        payment_data.append({
                            'hora': hour,
                            'total_pagado': total_paid_amount,
                            'estado': status,
                            'id': identificador,
                        })
                    payment_data.reverse()
                else:
                    print("Error al buscar pagos:", result["response"])

                context['tabla_mp'] = payment_data
                context['today'] = datetime.now().strftime('%Y-%m-%d')
            else:
                context['payments'] = []
                
        except Exception as e:
            print(e)
            
        context['tabla_link_pedidos'] = [{
            'url':'https://docs.google.com/spreadsheets/d/1HWnI40MJxOVhU7PNW2mDYQUG14CH3we7gV9xXjJnbEc/edit?usp=drive_link',
            'nombre':'Poxipol'},
            ]
        
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = MyForm(request.POST,model_name=context['model_name'],fields_to_show=context['lista_formulario_campos'])
        context['ruta_actual'] = self.request.path
        
        if form.is_valid():
            model_name = context['model_name']
            form.save(model_name=model_name)
            return redirect(self.ruta_actual)
        else:
            context['form'] = form
            return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = MyForm(request.GET, model_name=context['model_name'], fields_to_show=context['lista_formulario_campos'])
        context['datos'] = []
        if form.is_valid():
            form_data = form.cleaned_data
            # Eliminamos los campos vacíos del formulario
            form_data = {k: v for k, v in form_data.items() if v}
            print(form_data)
            try:
                model = apps.get_model('bdd', context['model_name'])
            except:
                pass
            try:
                model = apps.get_model('x_cartel', context['model_name'])
            except:
                pass
            armador = context['armador']
            #armador.formulario_campos_contiene
            form_data_copy = form_data.copy()
            for k, v in form_data_copy.items():
                if k in [obj.nombre for obj in armador.formulario_campos_contiene.all()]:
                    form_data[f'{k}__contains'] = form_data.pop(k)
                if k in [obj.nombre for obj in armador.formulario_campos_empieza_con.all()]:
                    form_data[f'{k}__istartswith'] = form_data.pop(k)
                    if k == 'codigo':
                        es_codigo = True

            if form_data == {}:
                context['datos'] = []
            else:
                context['datos'] = list(model.objects.filter(**form_data).values())
                if len(context['datos'])==1 and context['model_name']=='Item':
                    item_trabajado = Item.objects.get(**context['datos'][0])
                    if item_trabajado.trabajado:
                        print('item_trabajado: ',item_trabajado.trabajado)
                        pass
                    else:
                        item_trabajado.trabajado = True
                        item_trabajado.save()
                        print('Guardando item trabajado')
                    
                print(context['datos'])
                if context['model_name'] == "Item":
                    # Filtrar datos para incluir solo aquellos cuyo campo "actualizado" sea verdadero
                    context['datos'] = [dato for dato in context['datos']]# if dato.get('actualizado') == True]
        else:
            context['form'] = form
        filtered_data = [{k: v for k, v in d.items() if k in context['titulos']} for d in context['datos']]
        context['datos'] = filtered_data

        return self.render_to_response(context)

class Inicio(MiVista):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        # Aquí puedes agregar código antes de llamar al método get original
        response = super().get(request, *args, **kwargs)
        # Aquí puedes agregar código después de llamar al método get original
        return response

    def post(self, request, *args, **kwargs):
        # Aquí puedes agregar código antes de llamar al método post original
        response = super().post(request, *args, **kwargs)
        # Aquí puedes agregar código después de llamar al método post original
        return response

class Prueba(MiVista):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        # Aquí puedes agregar código antes de llamar al método get original
        response = super().get(request, *args, **kwargs)
        # Aquí puedes agregar código después de llamar al método get original
        return response

    def post(self, request, *args, **kwargs):
        # Aquí puedes agregar código antes de llamar al método post original
        response = super().post(request, *args, **kwargs)
        # Aquí puedes agregar código después de llamar al método post original
        return response

#-----------------------------------------------------------------------------------------


class BusquedaForm(forms.Form):
    """
    Formulario de búsqueda que permite al usuario seleccionar una Marca, Cajón, Cajonera y Sector específicos.
    """
    marca = forms.ModelChoiceField(queryset=Marca.objects.all(), required=False)
    cajon = forms.ModelChoiceField(queryset=Cajon.objects.all(), required=False)
    cajonera = forms.ModelChoiceField(queryset=Cajonera.objects.all(), required=False)
    sector = forms.ModelChoiceField(queryset=Sector.objects.all(), required=False)

class BusquedaView(FormView):
    """
    Vista de formulario que maneja la lógica de búsqueda y muestra los resultados al usuario.
    """
    template_name = 'plantilla_prueba.html'
    form_class = BusquedaForm

    def get_context_data(self, **kwargs):
        """
        Obtiene el contexto para la plantilla. Agrega todos los sectores al contexto.
        """
        context = super().get_context_data(**kwargs)
        context['sectores'] = Sector.objects.all()
        return context

    def form_valid(self, form):
        """
        Procesa el formulario cuando es válido. Filtra los elementos en función de los campos del formulario y agrega los elementos filtrados al contexto.
        """
        marca = form.cleaned_data['marca']
        cajon = form.cleaned_data['cajon']
        cajonera = form.cleaned_data['cajonera']
        sector = form.cleaned_data['sector']

        items = Item.objects.all()
        if marca:
            items = items.filter(marca=marca)
        if cajon:
            items = items.filter(cajon=cajon)
        if cajonera:
            items = items.filter(cajon__cajonera=cajonera)
        if sector:
            items = items.filter(cajon__cajonera__sector=sector)

        # Aquí puedes procesar los resultados de la búsqueda y mostrarlos al usuario
        # Por ejemplo, puedes agregarlos al contexto y mostrarlos en el template
        context = self.get_context_data(form=form)
        context['items'] = items
        return self.render_to_response(context)




class ItemsView(View):
    def get(self, request, cajon_id):
        # Obtener items del cajón especificado
        cajon = Cajon.objects.get(id=cajon_id)
        items = Item.objects.filter(cajon=cajon)

        # Crear lista con los datos de los items
        data = []
        for item in items:
            data.append({
                'codigo': item.codigo,
                'descripcion': item.descripcion,
                'final': item.final,
            })

        # Devolver JSON con la lista de items
        return JsonResponse(data, safe=False)
#-----------------------------------------------------------------------------------------

class Imprimir(TemplateView):
    template_name = 'generic_template.html'
    ruta_actual = ''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barra_de_navegacion'] = NavBar.objects.all()
        self.ruta_actual = self.request.path

        print(self.ruta_actual)
        if self.ruta_actual == '/imprimir/':
            context['muro'] = 'muro_simple.html'
            context['lista_html'] = ['plantilla_formulario.html']
            context['lista_formulario_campos'] = ['sub_carpeta','sub_titulo']
            context['boton_form'] = 'Imprimir'
            context['action'] = 'tabla/'
            context['metodo'] = 'POST'
        elif self.ruta_actual == '/imprimir/tabla/':
            context['muro'] = 'muro_imprimir.html'
            context['lista_html'] = ['imprimir_carteles_x6.html']
            context['lista_formulario_campos'] = ['sub_carpeta','sub_titulo']
            context['action'] = ''
            context['campos'] = ['descripcion', 'final',  'final_efectivo', 'final_rollo', 'final_rollo_efectivo', 'actualizado']
            context['titulos'] = ['Descripcion', 'Publico',  'Efectivo', 'X Cantidad', 'X Cant Efectivo']
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = MyForm(request.GET, model_name='Item', fields_to_show=context['lista_formulario_campos'])
        context['ruta_actual'] = self.ruta_actual
        context['datos'] = []
        
        context['form'] = form
        context['payments'] = []
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        modelo = apps.get_model('bdd', 'Item')
        form = MyForm(request.POST, model_name='Item', fields_to_show=context['lista_formulario_campos'])
        context['ruta_actual'] = self.ruta_actual
        context['datos'] = []
        if form.is_valid():
            form_data = form.cleaned_data
            # Eliminamos los campos vacíos del formulario
            form_data = {k: v for k, v in form_data.items() if v}
            
            #print('form: ', form_data)
            
            context['datos'] = list(modelo.objects.filter(**form_data).values())
            #print('datos: ', context['datos'])
            
            if self.ruta_actual == '/imprimir/tabla/' and context['datos']:
                filtered_data = [{k: v for k, v in d.items() if k in context['campos']} for d in context['datos']]
                context['datos'] = filtered_data
                # Definimos el orden deseado de las columnas
                column_order = context['campos']

                # Reordenamos las columnas de los datos
                ordered_data = []
                for row in context['datos']:
                    ordered_row = {column: row[column] for column in column_order}
                    ordered_data.append(ordered_row)

                # Actualizamos los datos en el contexto
                context['datos'] = ordered_data

                print(context['datos'])
        
        return self.render_to_response(context)

#------------------------------------------- AJAX ----------------------------------------

def crear_modificar_lista_pedidos(request, proveedor_id=1):
    if request.method == 'GET':
        items = Lista_Pedidos.objects.filter(proveedor_id=proveedor_id)
        data = []
        for item in items:
            data.append({
                'id': item.id,
                'proveedor': {
                    'id': item.proveedor.id,
                    'text_display': item.proveedor.text_display,
                    # Agrega aquí los demás campos del proveedor que necesites
                },
                'item': {
                    'id': item.item.id,
                    'descripcion': item.item.descripcion,
                    # Agrega aquí los demás campos del item que necesites
                },
                'cantidad': item.cantidad,
                # Agrega aquí los demás campos que necesites
            })
        return JsonResponse(data, safe=False)


        
    if request.method == 'POST':
        # Obtener los datos enviados en la solicitud
        data = json.loads(request.body)
        codigo = data.get('codigo')

        # Obtener el objeto Item correspondiente al código enviado
        item = Item.objects.get(codigo=codigo)

        # Obtener la abreviatura del proveedor del código del objeto Item
        abreviatura =  '/' + codigo.split('/')[-1]

        # Buscar el objeto ListaProveedores correspondiente a la abreviatura
        print(abreviatura)
        lista_proveedores = ListaProveedores.objects.get(abreviatura=abreviatura)

        # Buscar el objeto Proveedor correspondiente al objeto ListaProveedores
        proveedor = Proveedor.objects.get(identificador=lista_proveedores)

        # Verificar si ya existe un registro en la tabla Lista_Pedidos para el Item correspondiente
        lista_pedido = Lista_Pedidos.objects.filter(item=item).first()
        if lista_pedido:
            # Si ya existe un registro, incrementar su cantidad en 1
            lista_pedido.cantidad += 1
            lista_pedido.save()
        else:
            # Si no existe un registro, crear uno nuevo con cantidad igual a 1 y el proveedor correspondiente
            lista_pedido = Lista_Pedidos.objects.create(item=item, cantidad=1, proveedor=proveedor)
            
        if item.trabajado:
            pass
        else:
            item.trabajado = True
            item.proveedor = proveedor
            item.save()
        # Devolver una respuesta JSON indicando que la operación fue exitosa
        return JsonResponse({'success': True})

    # Devolver una respuesta JSON indicando que ocurrió un error si el método de solicitud no es POST
    return JsonResponse({'error': 'Invalid request method'})




def seleccionar_proveedor(request):
    proveedores = Proveedor.objects.all()
    return render(request, 'seleccionar_proveedor.html', {'proveedores': proveedores})



def cambiar_cantidad_pedido(request, id_articulo, cantidad):
    print(request)
    if request.method == 'POST':
        # Aquí puedes buscar el artículo por ID y actualizar la cantidad
        # ...
        print(id_articulo, cantidad)
        
        pedido = Lista_Pedidos.objects.get(id=id_articulo)
        pedido.cantidad = cantidad
        pedido.save()
        
        nueva_cantidad = cantidad  # Aquí debes obtener la nueva cantidad
        return JsonResponse({'status': 'ok', 'nueva_cantidad': nueva_cantidad}, safe=False)
           


from django.forms.models import model_to_dict
def editar_item(request,id_articulo):
    
    if request.user.is_authenticated:
        carrito = Carrito(usuario=request.user)
    
    if request.method == 'GET':
        # Aquí puedes buscar el artículo por ID y actualizar la cantidad
        # ...
        articulo = Item.objects.get(id=id_articulo)
        modal_cantidad = articulo.stock
        modal_barras = articulo.barras
        tiene_cartel = articulo.tiene_cartel
        cajon = articulo.cajon
        cajon_dict = model_to_dict(cajon) if cajon else None  # Convierte el objeto Cajon a un diccionario
        
        cajon_vacio = Cajon(id=None, codigo="------")
        cajones = [cajon_vacio] + list(Cajon.objects.all())
        cajones = serializers.serialize('json', cajones)

        
        return JsonResponse({
            'status': 'ok',
            'modal_cantidad': modal_cantidad,
            'modal_barras': modal_barras,
            'modal_tiene_cartel':tiene_cartel,
            'modal_cajon': cajon_dict,
            'cajones':cajones,
            }, safe=False)
    
    if request.method == 'POST':
        # Aquí puedes buscar el artículo por ID y actualizar la cantidad
        # ...
        data = json.loads(request.body)
        
        articulo = Item.objects.get(id=id_articulo)
        articulo.stock = data.get('cantidad')
        if data.get('barras') == '':
            articulo.barras = '0'
        else:
            articulo.barras = data.get('barras')
            
        articulo.tiene_cartel = data.get('tiene_cartel')
        # Obtén el objeto Cajon correspondiente al ID y asigna este objeto al campo cajon de tu artículo
        cajon_id = data.get('cajon')
        if cajon_id and cajon_id != 'null':
            print('cajon_id: ',cajon_id)
            cajon = Cajon.objects.get(id=cajon_id)
            articulo.cajon = cajon
        else:
            articulo.cajon = None
        articulo.save()
        
        return JsonResponse({'status': 'ok'})
    



def agregar_articulo_a_carrito(request, id_articulo):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        print(data.get('cantidad'))
        if request.user.is_authenticated:
            item = Item.objects.get(id=id_articulo)
            
            usuario_caja_id = data.get('usuario_caja')
            print(usuario_caja_id)
            if usuario_caja_id:
                usuario_caja = User.objects.get(id=usuario_caja_id)
            else:
                usuario_caja = request.user
            carrito, created = Carrito.objects.get_or_create(usuario=usuario_caja)
            articulo, created = Articulo.objects.get_or_create(item=item, carrito=carrito, defaults={'cantidad': data.get('cantidad'), 'precio': item.final, 'precio_efectivo': item.final_efectivo})
            print('carrito: ',carrito)
            if not created:
                articulo.cantidad = F('cantidad') + data.get('cantidad')
                articulo.save()
            
            # Add diferencia de cantidad to Pedido
            pedido, pedido_created = Lista_Pedidos.objects.get_or_create(proveedor=item.proveedor, item=item, defaults={'cantidad': data.get('cantidad'),})
            print("pedido creado: ", pedido_created)
            print(pedido)
            if not pedido_created:
                pedido.cantidad = F('cantidad') + data.get('cantidad')
                pedido.save()
        return JsonResponse({'status': 'ok'})

    
def carrito_to_dict(carrito):
    return {
        'id': carrito.id,
        'usuario': carrito.usuario.username,
        # Agrega aquí otros campos que quieras incluir
    }

def carrito(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            carrito, created = Carrito.objects.get_or_create(usuario=request.user)
            #articulo = Articulo.obje
        return JsonResponse({'status': 'ok', 'carrito': carrito_to_dict(carrito)}, safe=False)
    
    
class ListadoPedidos(MiVista):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        form = MyForm(request.GET, model_name=context['model_name'], fields_to_show=context['lista_formulario_campos'])
        context['datos'] = []
        if form.is_valid():
            form_data = form.cleaned_data
            # Eliminamos los campos vacíos del formulario
            form_data = {k: v for k, v in form_data.items() if v}
            print(form_data)
            model = apps.get_model('bdd', context['model_name'])
            armador = context['armador']
            #armador.formulario_campos_contiene
            form_data_copy = form_data.copy()
            foreign_keys = [field for field in model._meta.get_fields() if isinstance(field, ForeignKey)]
            for fk in foreign_keys:
                for k, v in form_data_copy.items():
                    if k == fk.name and 'descripcion' in [field.name for field in fk.related_model._meta.get_fields()]:
                        form_data[f'{k}__descripcion'] = form_data.pop(k)
                    if k in [obj.nombre for obj in armador.formulario_campos_contiene.all()]:
                        form_data[f'{k}__contains'] = form_data.pop(k)
                    if k in [obj.nombre for obj in armador.formulario_campos_empieza_con.all()]:
                        form_data[f'{k}__istartswith'] = form_data.pop(k)

            if form_data == {}:
                context['datos'] = []
            else:
                print(form_data)
                context['datos'] = list(model.objects.filter(**form_data).values('id', 'item__codigo', 'item__descripcion', 'cantidad', 'pedido'))

                print('contexto: ',context['datos'])
                if context['model_name'] == "Item":
                    # Filtrar datos para incluir solo aquellos cuyo campo "actualizado" sea verdadero
                    context['datos'] = [dato for dato in context['datos']]# if dato.get('actualizado') == True]
        else:
            context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(request)
        return self.render_to_response(context)

def articulo_to_dict(articulo):
    if isinstance(articulo, Articulo):
        return {
            'id': str(articulo.id),
            'item': str(articulo.item),
            'cantidad': articulo.cantidad,
            'precio': str(articulo.precio),
            'precio_efectivo': str(articulo.precio_efectivo),
        }
    elif isinstance(articulo, ArticuloSinRegistro):
        return {
            'id': str(articulo.id),
            'descripcion': articulo.descripcion,
            'cantidad': articulo.cantidad,
            'precio': str(articulo.precio),
        }


def calcular_total(datos):
    for nombre, carrito in datos.items():
        total = 0
        total_efectivo = 0
        for articulo in carrito['articulos']:
            total += float(articulo['precio']) * articulo['cantidad']
            total_efectivo += float(articulo['precio_efectivo']) * articulo['cantidad']
        for articulo in carrito['articulos_sin_registro']:
            total += float(articulo['precio']) * articulo['cantidad']
            total_efectivo += float(articulo['precio']) * articulo['cantidad']
        carrito['total'] = total
        carrito['total_efectivo'] = total_efectivo
    return datos



def consultar_carrito(request):
    if request.method == 'GET':
        datos = {}
        if request.user.is_authenticated:
            if str(request.user) == 'darkydiel':
                carrito_mati = Carrito.objects.get(id=2)
                articulos_mati = Articulo.objects.filter(carrito=carrito_mati)
                articulos_sin_registro_mati = ArticuloSinRegistro.objects.filter(carrito=carrito_mati)
                carrito_carlos = Carrito.objects.get(id=3)
                articulos_carlos = Articulo.objects.filter(carrito=carrito_carlos)
                articulos_sin_registro_carlos = ArticuloSinRegistro.objects.filter(carrito=carrito_carlos)
                datos = {
                    'Mati': {
                        "articulos": [articulo_to_dict(articulo) for articulo in articulos_mati],
                        "articulos_sin_registro": [articulo_to_dict(articulo) for articulo in articulos_sin_registro_mati],
                        "carrito_id": carrito_mati.id
                    },
                    'Carlos': {
                        "articulos": [articulo_to_dict(articulo) for articulo in articulos_carlos],
                        "articulos_sin_registro": [articulo_to_dict(articulo) for articulo in articulos_sin_registro_carlos],
                        "carrito_id": carrito_carlos.id
                    }
                }
            else:
                carrito = Carrito.objects.get(usuario=request.user)
                articulos = Articulo.objects.filter(carrito=carrito)
                articulos_sin_registro = ArticuloSinRegistro.objects.filter(carrito=carrito)
                datos = {
                    str(request.user): {
                        "articulos": [articulo_to_dict(articulo) for articulo in articulos],
                        "articulos_sin_registro": [articulo_to_dict(articulo) for articulo in articulos_sin_registro],
                        "carrito_id": carrito.id
                    }
                }
            datos = calcular_total(datos)
        return JsonResponse(datos)





def usuarios_caja(request):
    if request.method == 'GET':
        # Aquí debes obtener tus usuarios "caja". Este es solo un ejemplo.
        usuarios = [
            {'nombre': 'Mati', 'id': 1},
            {'nombre': 'Carlos', 'id': 2},
            # Agrega aquí otros usuarios "caja" que quieras incluir
        ]
        return JsonResponse(usuarios, safe=False)

def eliminar_articulo_pedido(request):
    if request.method == 'POST':
        print('id: ', request.POST.get('id'))
        print('quantity: ', request.POST.get('quantity'))
        print('confirmed: ', request.POST.get('confirmed'))

        pedido = Lista_Pedidos.objects.get(id=request.POST.get('id'))
        if request.POST.get('confirmed'):
            # Aquí puedes agregar el código para procesar la cantidad y la confirmación
            pedido.pedido = True
            pedido.cantidad = request.POST.get('quantity')
            pedido.save()
        else:
            pedido.delete()
    return JsonResponse({'status': 'ok'})

from django.db.models import Q

class ListarCarteles(TemplateView):
    template_name = 'generic_template.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barra_de_navegacion'] = NavBar.objects.all()
        self.ruta_actual = self.request.path

        print(self.ruta_actual)
        if self.ruta_actual == '/listar_carteles/':
            context['muro'] = 'muro_doble.html'
            context['lista_html'] = ['plantilla_formulario.html','tabla_listado_carteles_prueva.html']
            lista_formulario_campos = ['proveedor', 'revisar']
            formulario = MyForm(model_name='Carteles', fields_to_show=lista_formulario_campos)
            context['form'] = formulario
            context['boton_form'] = 'Buscar'
            context['action'] = '/listar_carteles/'
            context['metodo'] = 'GET'
            context['campos'] = ['descripcion']
            context['titulos'] = ['Descripcion']
            cajones = Cajon.objects.all()
            cajones_ids = list(cajones.values_list('id', flat=True))
            for id in cajones_ids:
                _ = CartelesCajon.objects.get_or_create(id=id)
        return context
    

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        proveedor = request.GET.get('proveedor')
        revisar = request.GET.get('revisar')
        if revisar == "true":
            filtro = True
        else:
            filtro = False

        # Anotar cada cajón con un campo calculado que indica si tiene al menos un item que necesita ser revisado
        cajones = Cajon.objects.annotate(
            tiene_item_para_revisar=Exists(
                Item.objects.filter(cajon=OuterRef('id'), carteles__revisar=True)
            )
        )

        # Filtrar los cajones basándote en el proveedor y en si tienen al menos un item que necesita ser revisado
        if proveedor:
            cajones = cajones.filter(item__proveedor=proveedor, tiene_item_para_revisar=True)
        else:
            cajones = cajones.filter(tiene_item_para_revisar=True)

        for cajon in cajones:
            cajon.items = Item.objects.filter(cajon=cajon.id)
            for item in cajon.items:
                print('')
                print(item.descripcion)
                if item.carteles_set.first():
                    print(item.carteles_set.first().revisar)
                item.url = f"/x_cartel/imprimir/{item.id}"


        items_sin_cajon = Item.objects.filter(tiene_cartel=True, cajon__isnull=True, carteles__revisar=filtro)
        for item in items_sin_cajon:
            item.url = f"/x_cartel/imprimir/{item.id}"

        context['cajones'] = cajones
        context['items_sin_cajon'] = items_sin_cajon

        return render(request, self.template_name, context)






    
    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aquí puedes agregar código antes de llamar al método post original
        '''
        print("POST: ",request.POST.get('proveeodor'))
        carteles=Carteles.objects.filter(proveedor=request.POST.get('proveedor'))
        context['items']=Item.objects.filter(id__in=carteles.values_list('item_id', flat=True))
        print("items: ", context['datos'])
        '''
        # Aquí puedes agregar código después de llamar al método post original
        return render(request, self.template_name, context)   
    


def descargar_archivo(request):
    nombre_del_archivo = 'script_pyinstaller.py'  # Reemplaza esto con el nombre real de tu archivo
    ruta_al_archivo = os.path.join(settings.MEDIA_ROOT, nombre_del_archivo)
    response = FileResponse(open(ruta_al_archivo, 'rb'), content_type='application/rar')
    response['Content-Disposition'] = f'attachment; filename="{nombre_del_archivo}"'
    return response
