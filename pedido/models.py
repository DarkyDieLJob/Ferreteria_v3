from datetime import timezone
from django.db import models

from bdd.models import Item, Proveedor, Lista_Pedidos

    
class Vendido(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    cantidad = models.FloatField(default=0.0)
    
    umbral = models.FloatField(default=0.0)
    
    pedido = models.BooleanField(default=False)

class ArticuloPedido(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    cantidad = models.FloatField(default=0.0)
    
    llego = models.BooleanField(default=False)
    
    fecha = models.DateField(auto_created=True, default='2021-01-01')
    
class Pedido(models.Model):
    ESTADOS_PEDIDOS = (
        ('Pd', 'Pendiente'),
        ('En', 'Enviado'),
        ('Et', 'Entregado'),
        ('Co', 'Controlado'),
    )
    
    fecha = models.DateField(auto_now_add=True, blank=True, null=True)
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    
    articulo_pedido = models.ManyToManyField(ArticuloPedido)
    
    total = models.FloatField(default=0.0)
    
    fecha_entrega = models.DateField(blank=True, null=True)
    
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDOS, default='Pd')
    
    def __str__(self):
        return str(self.fecha) + " " + str(self.proveedor) + " " + str(self.estado)
    

