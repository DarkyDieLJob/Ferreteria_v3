from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from bdd.models import Item
from .models import Pedido
from dal_select2.widgets import ModelSelect2



from django import forms
from .models import Item

class PedidoForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        widget=ModelSelect2(url='item-autocomplete')
    )

    class Meta:
        model = Pedido
        fields = ('item','cantidad','pedido')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
