from django import forms


class DailyReportForm(forms.Form):
    file = forms.FileField(required=False, label='Archivo (xlsx/ods)')
    drive_file_id = forms.CharField(required=False, label='ID de archivo en Drive')
    base_name = forms.CharField(required=False, initial='informe de ventas', label='Prefijo de nombre (opcional)')
    month = forms.ChoiceField(
        required=True,
        choices=[
            ('1', 'Enero'), ('2', 'Febrero'), ('3', 'Marzo'), ('4', 'Abril'),
            ('5', 'Mayo'), ('6', 'Junio'), ('7', 'Julio'), ('8', 'Agosto'),
            ('9', 'Septiembre'), ('10', 'Octubre'), ('11', 'Noviembre'), ('12', 'Diciembre')
        ],
        label='Mes'
    )
    year = forms.IntegerField(required=True, label='Año', min_value=2000, max_value=2100)
    include_year = forms.BooleanField(required=False, initial=True, label='Incluir año en el nombre')
    use_control_book = forms.BooleanField(required=False, initial=False, label='Usar libro de control (procesar carpeta de entrada en Drive)')
    output_formats = forms.MultipleChoiceField(
        required=False,
        choices=[('xlsx', 'XLSX'), ('ods', 'ODS')],
        initial=['xlsx'],
        widget=forms.CheckboxSelectMultiple,
        label='Formatos de salida',
    )
    output_file_name = forms.CharField(required=False, label='Nombre de salida (avanzado)')

    def clean(self):
        data = super().clean()
        if not data.get('file') and not data.get('drive_file_id'):
            raise forms.ValidationError('Debe subir un archivo o indicar un ID de Drive.')
        return data


class DriveBatchForm(forms.Form):
    action = forms.ChoiceField(
        required=False,
        choices=[('sync', 'Sincronizar lista'), ('process', 'Procesar seleccionados')],
        initial='sync',
        label='Acción'
    )
    output_formats = forms.MultipleChoiceField(
        required=False,
        choices=[('xlsx', 'XLSX'), ('ods', 'ODS')],
        initial=['xlsx'],
        widget=forms.CheckboxSelectMultiple,
        label='Formatos de salida',
    )
