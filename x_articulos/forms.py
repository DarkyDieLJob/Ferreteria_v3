from django import forms
from .models import Articulo
from bdd.models import Item

class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = ['codigo','precio_base', 'precio_efectivo',]

class Item_Form(forms.ModelForm):
    class Meta:
        model = Item
        fields = [
            'codigo',
            'barras',
            'final_rollo',
            'final_rollo_efectivo',
            'final',
            'final_efectivo',
            'sub_carpeta',
            'sub_titulo',
            'actualizado',
            'stock',
            'proveedor',
            ]
