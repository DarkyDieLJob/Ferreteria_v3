from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.db import models
from .models import *
from django.db.models.fields.reverse_related import ManyToOneRel

class BaseModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.fields = [field.name for field in model._meta.get_fields() if not isinstance(field, ManyToOneRel) and field.name != 'id' and not (model.__name__ == 'Listado_Planillas' and field.name == 'fecha')]
        if model.__name__ in ['Formulario_Campos', 'Modelo_Campos'] and 'armador' in self.fields:
            self.fields.remove('armador')
        self.list_display = self.fields.copy()
        self.search_fields = self.fields
        for field in model._meta.many_to_many:
            display_method_name = f'{field.name}_display'
            display_method = self.create_display_method(field)
            display_method.short_description = field.verbose_name.title()
            setattr(self, display_method_name, display_method)
            self.list_display.append(display_method_name)
        if model.__name__ == 'Armador':
            self.list_display.remove('modelo_campos')
            self.list_display.remove('formulario_campos')
            self.list_display.remove('formulario_campos_contiene')
            self.list_display.remove('formulario_campos_empieza_con')
        if model.__name__ == 'Item':
            if 'fecha' in self.fields:
                self.fields.remove('fecha')
            if 'fecha' in self.list_display:
                self.list_display.remove('fecha')
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