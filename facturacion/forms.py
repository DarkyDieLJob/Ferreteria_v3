from django import forms
from .models import Cliente


BS_INPUT = {"class": "form-control"}
BS_SELECT = {"class": "form-select"}


class ClienteForm(forms.ModelForm):
    """Formulario completo de Cliente usado para alta y edición."""

    class Meta:
        model = Cliente
        fields = "__all__"
        widgets = {
            "razon_social": forms.TextInput(attrs=BS_INPUT),
            "cuit_dni": forms.TextInput(attrs=BS_INPUT),
            "responsabilidad_iva": forms.Select(attrs=BS_SELECT),
            "tipo_documento": forms.Select(attrs=BS_SELECT),
            "domicilio": forms.TextInput(attrs=BS_INPUT),
            "telefono": forms.TextInput(attrs=BS_INPUT),
        }


class ClienteQuickForm(forms.ModelForm):
    """Formulario para alta rápida desde el buscador (todos los campos del modelo)."""

    class Meta:
        model = Cliente
        fields = "__all__"
        widgets = {
            "razon_social": forms.TextInput(attrs=BS_INPUT),
            "cuit_dni": forms.TextInput(attrs=BS_INPUT),
            "responsabilidad_iva": forms.Select(attrs=BS_SELECT),
            "tipo_documento": forms.Select(attrs=BS_SELECT),
            "domicilio": forms.TextInput(attrs=BS_INPUT),
            "telefono": forms.TextInput(attrs=BS_INPUT),
        }


class ClienteFilterForm(forms.Form):
    """Filtros del listado de clientes."""

    q = forms.CharField(
        required=False,
        label="Razón social",
        widget=forms.TextInput(attrs={**BS_INPUT, "placeholder": "Razón social"}),
    )
    cuit = forms.CharField(
        required=False,
        label="CUIT/DNI",
        widget=forms.TextInput(attrs={**BS_INPUT, "placeholder": "CUIT/DNI"}),
    )
    iva = forms.ChoiceField(
        required=False,
        label="Resp. IVA",
        choices=[("", "Todas")] + Cliente.RESPONSABILIDAD_IVA_OPCIONES,
        widget=forms.Select(attrs=BS_SELECT),
    )
    tdoc = forms.ChoiceField(
        required=False,
        label="Tipo doc.",
        choices=[("", "Todos")] + Cliente.TIPO_DOCUMENTO_OPCIONES,
        widget=forms.Select(attrs=BS_SELECT),
    )
