from django.db import models

from bdd.models import Item, Proveedor
    
class Vendido(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    cantidad = models.FloatField(default=0.0)
    
    pedido = models.BooleanField(default=False)

class Pedido(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    cantidad = models.FloatField(default=0.0)
    
    pedido = models.BooleanField(default=False)