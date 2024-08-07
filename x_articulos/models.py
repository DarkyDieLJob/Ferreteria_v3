from django.db import models

# Create your models here.
class Articulo(models.Model):
    codigo = models.CharField(max_length=50)
    descripcion = models.CharField(max_length=250)
    precio_base = models.FloatField(default=0.0)
    ultimo_cambio = models.DateField(auto_now_add=True, blank=True, null=True)
    actualizado = models.BooleanField(default=False)
    precio_efectivo = models.FloatField(default=0.0)