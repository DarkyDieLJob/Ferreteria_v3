# tu_app/views/forms.py
from django import forms
from django.apps import apps
# Asegúrate de que estos modelos estén definidos o importa desde donde estén
# from ..models import Marca, Cajon, Cajonera, Sector  # Ejemplo si están en models.py de la app
from ..models import * # Importa todos los modelos de la app padre si es más fácil inicialmente


import logging

logger = logging.getLogger(__name__)

class DateInput(forms.DateInput):
    """
    Widget personalizado para campos de fecha.
    Establece el tipo de entrada a 'date'.
    """
    input_type = 'date'
    logger.debug("Widget DateInput inicializado.") # Ejemplo de uso del logger

class TimeInput(forms.TimeInput):
    """
    Widget personalizado para campos de tiempo.
    Establece el tipo de entrada a 'time'.
    """
    input_type = 'time'
    logger.debug("Widget TimeInput inicializado.")

class DateTimeInput(forms.DateTimeInput):
    """
    Widget personalizado para campos de fecha y hora.
    Establece el tipo de entrada a 'datetime-local'.
    """
    input_type = 'datetime-local'
    logger.debug("Widget DateTimeInput inicializado.")

class EmailInput(forms.EmailInput):
    """
    Widget personalizado para campos de correo electrónico.
    Establece el tipo de entrada a 'email'.
    """
    input_type = 'email'
    logger.debug("Widget EmailInput inicializado.")

class MyForm(forms.Form):
    """
    Formulario personalizado que construye dinámicamente un conjunto de campos de formulario
    basados en un modelo y una lista de campos especificados.
    """
    def __init__(self, *args, **kwargs):
        logger.info(f"Inicializando MyForm con kwargs: {kwargs}")
        model_name = kwargs.pop('model_name')
        fields_to_show = kwargs.pop('fields_to_show')
        model = None # Inicializar model
        try:
            # Intenta obtener el modelo de la app 'bdd' o 'x_cartel'
            # Sería mejor pasar la app_label explícitamente si es posible
            model = apps.get_model(app_label='bdd', model_name=model_name)
            logger.debug(f"Modelo '{model_name}' encontrado en app 'bdd'.")
        except LookupError:
            logger.warning(f"Modelo '{model_name}' no encontrado en 'bdd', intentando en 'x_cartel'.")
            try:
                model = apps.get_model(app_label='x_cartel', model_name=model_name)
                logger.debug(f"Modelo '{model_name}' encontrado en app 'x_cartel'.")
            except LookupError:
                logger.error(f"Modelo '{model_name}' no encontrado en ninguna app configurada ('bdd', 'x_cartel').")
                # Considera lanzar un error o manejarlo de otra forma
                # raise ValueError(f"Modelo '{model_name}' no encontrado.")
                pass # O manejar como prefieras si el modelo no se encuentra

        super(MyForm, self).__init__(*args, **kwargs)

        if model: # Solo proceder si se encontró el modelo
            if fields_to_show == ['__all__']:
                fields = model._meta.fields
            elif fields_to_show == ['None']:
                fields = []
            else:
                try:
                    fields = [model._meta.get_field(field_name) for field_name in fields_to_show]
                except Exception as e:
                     logger.error(f"Error obteniendo campos para {model_name} con fields_to_show={fields_to_show}: {e}")
                     fields = [] # O maneja el error como prefieras


            for field in fields:
                if field.name == 'id':
                    continue
                try:
                    formfield = field.formfield()
                    if formfield is None:
                        logger.warning(f"El campo '{field.name}' del modelo '{model_name}' no tiene un campo de formulario válido.")
                    else:
                        self.fields[field.name] = formfield
                except Exception as e:
                    logger.error(f"Error al crear formfield para {field.name} en modelo {model_name}: {e}")


            # Aplicar widgets personalizados
            for field_name, form_field_instance in self.fields.items():
                 if isinstance(form_field_instance, forms.DateField):
                     form_field_instance.widget = DateInput()
                 elif isinstance(form_field_instance, forms.TimeField):
                     form_field_instance.widget = TimeInput()
                 elif isinstance(form_field_instance, forms.DateTimeField):
                     form_field_instance.widget = DateTimeInput()
                 elif isinstance(form_field_instance, forms.EmailField):
                     form_field_instance.widget = EmailInput()
        else:
             logger.warning(f"No se pudo inicializar MyForm porque el modelo '{model_name}' no fue encontrado.")


    def save(self, model_name):
        logger.info(f"Intentando guardar datos para el modelo '{model_name}'.")
        if not self.is_valid():
             logger.warning(f"Intento de guardar MyForm fallido. Errores: {self.errors}")
             return None # O lanzar excepción
        form_data = self.cleaned_data
        model = None
        try:
            # De nuevo, intenta obtener el modelo. Idealmente, la app_label debería ser conocida.
            model = apps.get_model('bdd', model_name)
        except LookupError:
            logger.warning(f"Modelo '{model_name}' no encontrado en 'bdd' durante save, intentando 'x_cartel'.")
            try:
                 model = apps.get_model('x_cartel', model_name)
            except LookupError:
                 logger.error(f"Modelo '{model_name}' no encontrado en save.")
                 raise ValueError(f"Modelo '{model_name}' no encontrado para guardar.")

        try:
            obj = model(**form_data)
            obj.full_clean() # Validar a nivel de modelo
            obj.save()
            logger.info(f"Objeto {model_name} guardado exitosamente. ID: {obj.pk}, Datos: {form_data}")
            return obj
        except Exception as e:
             logger.error(f"Error al guardar objeto {model_name} con datos {form_data}: {e}", exc_info=True)
             # Puedes añadir el error a los errores del formulario si quieres mostrarlo al usuario
             # self.add_error(None, f"Error al guardar: {e}")
             return None # O lanzar la excepción


class BusquedaForm(forms.Form):
    """
    Formulario de búsqueda que permite al usuario seleccionar una Marca, Cajón, Cajonera y Sector específicos.
    """
    logger.debug("Inicializando BusquedaForm.")
    marca = forms.ModelChoiceField(queryset=Marca.objects.all(), required=False)
    cajon = forms.ModelChoiceField(queryset=Cajon.objects.all(), required=False)
    cajonera = forms.ModelChoiceField(queryset=Cajonera.objects.all(), required=False)
    sector = forms.ModelChoiceField(queryset=Sector.objects.all(), required=False)