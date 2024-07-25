'''from django.contrib import admin
from django.db import models
from .models import *
from django.db.models.fields.reverse_related import ManyToOneRel

class BaseModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.fields = [field.name for field in model._meta.get_fields() if not isinstance(field, ManyToOneRel) and not isinstance(field, models.ManyToManyField) and field.name != 'id' and not (model.__name__ == 'Listado_Planillas' and field.name == 'fecha')]
        if model.__name__ in ['Formulario_Campos', 'Modelo_Campos'] and 'armador' in self.fields:
            self.fields.remove('armador')
        self.list_display = []
        self.search_fields = self.fields
        for field in model._meta.get_fields():
            if not isinstance(field, ManyToOneRel) and not isinstance(field, models.ManyToManyField):
                self.list_display.append(field.name)
            elif isinstance(field, models.ManyToManyField):
                display_method_name = f'{field.name}_display'
                display_method = self.create_display_method(field)
                display_method.short_description = field.verbose_name.title()
                setattr(self, display_method_name, display_method)
                self.list_display.append(display_method_name)
        super().__init__(model, admin_site)

    def create_display_method(self, field):
        def display_method(obj):
            related_objects = getattr(obj, field.name).all()
            return ', '.join(str(related_object) for related_object in related_objects)
        return display_method

import inspect
from . import models as my_models

model_classes = [cls for name, cls in inspect.getmembers(my_models) if inspect.isclass(cls) and issubclass(cls, models.Model) and not cls._meta.abstract]
for model in model_classes:
    admin.site.register(model, BaseModelAdmin)
'''

from django.contrib import admin
from .models import Modelo_Tablas, Modelo_Formularios, Modelo_Tarjetas, Modelo_Listas, Paginas

admin.site.register(Modelo_Tablas)
admin.site.register(Modelo_Formularios)
admin.site.register(Modelo_Tarjetas)
admin.site.register(Modelo_Listas)
admin.site.register(Paginas)
