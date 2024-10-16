from django import forms
from django.apps import apps

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
        model = apps.get_model(app_label='bdd', model_name=model_name)
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