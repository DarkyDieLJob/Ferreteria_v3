from django import forms
from .models import Planilla


class DateInput(forms.DateInput):
    input_type = 'date'

class TimeInput(forms.TimeInput):
    input_type = 'time'

class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetime-local'

class EmailInput(forms.EmailInput):
    input_type = 'email'

class BaseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name in self.fields:
            if isinstance(self.fields[field_name], forms.DateField):
                self.fields[field_name].widget = DateInput()
            elif isinstance(self.fields[field_name], forms.TimeField):
                self.fields[field_name].widget = TimeInput()
            elif isinstance(self.fields[field_name], forms.DateTimeField):
                self.fields[field_name].widget = DateTimeInput()
            elif isinstance(self.fields[field_name], forms.EmailField):
                self.fields[field_name].widget = EmailInput()
            # Aquí puedes agregar más condiciones para otros tipos de campos
            # y asignarles widgets personalizados
            if field_name == 'barras':
                self.fields[field_name].widget.attrs.update({'autofocus': 'autofocus'})

class Planilla_Form(BaseForm):
    class Meta:
        model = Planilla
        fields = [
            'nombre',
            'fecha',
        ]