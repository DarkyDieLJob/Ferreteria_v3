from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from bdd.models import Item
from .models import ArticuloPedido
from dal_select2.widgets import ModelSelect2



from django import forms
from .models import Item

class ArticuloPedidoForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=Item.objects.all(),
        widget=ModelSelect2(url='pedido:item-autocomplete')
    )

    class Meta:
        model = ArticuloPedido
        fields = ('item','cantidad')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
