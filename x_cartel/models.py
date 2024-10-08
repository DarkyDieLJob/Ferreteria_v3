from django.db import models
from bdd.models import Item, Proveedor

class Cartelitos(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    revisar = models.BooleanField(default= False, null=True, blank=True)
    habilitado = models.BooleanField(default= False, null=True, blank=True)
    
    descripcion = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk is None:  # Esto verifica si el objeto es nuevo
            self.descripcion = self.item.descripcion  # Aquí asignas el valor inicial
        super().save(*args, **kwargs)


class Carteles(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    revisar = models.BooleanField(default= False, null=True, blank=True)
    
    descripcion = models.TextField(null=True, blank=True)
    tamano_descripcion = models.IntegerField(default=100)
    texto_final = models.TextField(null=True, blank=True)
    tamano_texto_final = models.IntegerField(null=True, blank=True)
    final = models.TextField(null=True, blank=True)
    tamano_final = models.IntegerField(null=True, blank=True)
    texto_final_efectivo = models.TextField(null=True, blank=True)
    tamano_texto_final_efectivo = models.IntegerField(null=True, blank=True)
    final_efectivo = models.TextField(null=True, blank=True)
    tamano_final_efectivo = models.IntegerField(null=True, blank=True)
    
    def set_description(self):
        if not self.descripcion:
            self.descripcion = self.item.descripcion
    
    def __str__(self):
        return f"{self.descripcion} num: {self.id}"
    
class CartelesCajon(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    revisar = models.BooleanField(default= False, null=True, blank=True)
    
    descripcion = models.TextField(null=True, blank=True)
    tamano_descripcion = models.IntegerField(default=100)
    texto_final = models.TextField(null=True, blank=True)
    tamano_texto_final = models.IntegerField(null=True, blank=True)
    final = models.TextField(null=True, blank=True)
    tamano_final = models.IntegerField(null=True, blank=True)
    texto_final_efectivo = models.TextField(null=True, blank=True)
    tamano_texto_final_efectivo = models.IntegerField(null=True, blank=True)
    final_efectivo = models.TextField(null=True, blank=True)
    tamano_final_efectivo = models.IntegerField(null=True, blank=True)
    
    def set_description(self):
        if not self.descripcion:
            self.descripcion = self.item.descripcion
    
    def __str__(self):
        return f"{self.descripcion} num: {self.id}"