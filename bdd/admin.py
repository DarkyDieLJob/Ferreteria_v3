from django.contrib import admin
from django.db import models
from .models import *
from django.db.models.fields.reverse_related import ManyToOneRel, ManyToManyRel


class BaseModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.fields = [
            field.name
            for field in model._meta.get_fields()
            if not isinstance(field, ManyToOneRel)
            and not isinstance(field, ManyToManyRel)
            and field.name != "id"
            and not (model.__name__ == "Listado_Planillas" and field.name == "fecha")
        ]
        if (
            model.__name__ in ["Formulario_Campos", "Modelo_Campos"]
            and "armador" in self.fields
        ):
            self.fields.remove("armador")
        self.list_display = self.fields.copy()
        self.search_fields = self.fields
        for field in model._meta.many_to_many:
            display_method_name = f"{field.name}_display"
            display_method = self.create_display_method(field)
            display_method.short_description = field.verbose_name.title()
            setattr(self, display_method_name, display_method)
            self.list_display.append(display_method_name)
        if model.__name__ == "Armador":
            self.list_display.remove("modelo_campos")
            self.list_display.remove("formulario_campos")
            self.list_display.remove("formulario_campos_contiene")
            self.list_display.remove("formulario_campos_empieza_con")
        if model.__name__ == "Item":
            if "fecha" in self.fields:
                self.fields.remove("fecha")
            if "fecha" in self.list_display:
                self.list_display.remove("fecha")
        super().__init__(model, admin_site)

    def create_display_method(self, field):
        def display_method(obj):
            related_objects = getattr(obj, field.name).all()
            return ", ".join(str(related_object) for related_object in related_objects)

        return display_method

    # --- Admin action: marcar hay_csv_pendiente=True cuando el modelo posee ese campo ---
    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            field_names = [f.name for f in self.model._meta.get_fields()]
            if "hay_csv_pendiente" in field_names:
                actions["marcar_csv_pendiente"] = (
                    BaseModelAdmin.marcar_csv_pendiente,
                    "marcar_csv_pendiente",
                    "Marcar CSV pendiente (hay_csv_pendiente=True)",
                )
                actions["alternar_csv_pendiente"] = (
                    BaseModelAdmin.alternar_csv_pendiente,
                    "alternar_csv_pendiente",
                    "Alternar CSV pendiente (cambiar True/False)",
                )
        except Exception:
            pass
        return actions

    def marcar_csv_pendiente(self, request, queryset):
        # Marca el flag hay_csv_pendiente=True en lote
        queryset.update(hay_csv_pendiente=True)

    def alternar_csv_pendiente(self, request, queryset):
        # Alterna el valor de hay_csv_pendiente por fila seleccionada
        for obj in queryset:
            try:
                current = bool(getattr(obj, "hay_csv_pendiente", False))
                setattr(obj, "hay_csv_pendiente", not current)
                obj.save(update_fields=["hay_csv_pendiente"])
            except Exception:
                # En caso de error en algún objeto, continuar con el resto
                continue


import inspect
from . import models as my_models

model_classes = [
    cls
    for name, cls in inspect.getmembers(my_models)
    if inspect.isclass(cls) and issubclass(cls, models.Model) and not cls._meta.abstract
]
for model in model_classes:
    admin.site.register(model, BaseModelAdmin)
