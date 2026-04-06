from django import forms
from datetime import date, timedelta

from .models import Boleta, Servicio, Impuesto, Cheque, ProveedorFinanciero, Cuenta, TarjetaCredito, TicketDePago


def _add_months(d: date, months: int) -> date:
    # Suma de meses simple sin dependencias externas
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(
        d.day,
        [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][
            month - 1
        ],
    )
    return date(year, month, day)


class BoletaForm(forms.ModelForm):
    class Meta:
        model = Boleta
        fields = [
            "proveedor",
            "fecha_emision",
            "punto_venta",
            "numero",
            "monto",
        ]


class ProveedorFinancieroForm(forms.ModelForm):
    class Meta:
        model = ProveedorFinanciero
        fields = [
            "plazo_unidad",
            "plazo_valor",
            "descuento_boleta_A",
            "descuento_boleta_B",
            "punto_venta",
        ]


class CuentaForm(forms.ModelForm):
    class Meta:
        model = Cuenta
        fields = [
            "tipo",
            "nombre",
            # banco, identificador y vigencias quedan ocultos en el form
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customizar etiquetas del tipo sin cambiar los valores almacenados
        self.fields["tipo"].choices = [
            ("mp", "Digital (MP)"),
            ("banco", "Bancaria (BIP)"),
            ("efectivo", "Efectivo (cuenta general)"),
        ]


class TarjetaCreditoForm(forms.ModelForm):
    class Meta:
        model = TarjetaCredito
        fields = [
            "cuenta_liquidacion",
            "nombre",
            "ult4",
            "cierre_dia",
            "vencimiento_dia",
        ]


class ImpuestoTicketForm(forms.Form):
    impuesto = forms.ModelChoiceField(queryset=Impuesto.objects.all())
    periodo = forms.CharField(max_length=7, help_text="YYYY-MM")
    vencimiento = forms.DateField()
    monto = forms.DecimalField(max_digits=12, decimal_places=2)


class ServicioTicketForm(forms.Form):
    servicio = forms.ModelChoiceField(queryset=Servicio.objects.all())
    periodo = forms.CharField(max_length=7, help_text="YYYY-MM")
    vencimiento = forms.DateField()
    monto = forms.DecimalField(max_digits=12, decimal_places=2)


class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = [
            "nombre",
            "sujeto_pasivo",
            "cuentas_permitidas",
        ]
        widgets = {
            "cuentas_permitidas": forms.CheckboxSelectMultiple,
        }


class ImpuestoForm(forms.ModelForm):
    class Meta:
        model = Impuesto
        fields = [
            "nombre",
            "sujeto_pasivo",
            "tipo",
            "jurisdiccion",
            "cuentas_permitidas",
        ]
        widgets = {
            "cuentas_permitidas": forms.CheckboxSelectMultiple,
        }


class ChequeForm(forms.ModelForm):
    class Meta:
        model = Cheque
        fields = [
            "proveedor",
            "cuenta_emisora",
            "numero",
            "monto",
            "fecha_emision",
            "fecha_diferido",
        ]
