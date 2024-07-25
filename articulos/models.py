from django.db import models

  
class Marca(models.Model):
    nombre = models.CharField(max_length=20)
    
class Categoria(models.Model):
    nombre = models.CharField(max_length=20)
    
class Cartel(models.Model):
    nombre = models.CharField(max_length=20)

class Proveedor(models.Model):
    nombre = models.CharField(max_length=20)
    constante = models.FloatField(default=0.0)
    abreviatura = models.CharField(max_length=20)

class Articulo(models.Model):
    display = models.CharField(max_length=200)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, blank=True, null=True)
    trabajado = models.BooleanField(default=False)

class CodigoBarras(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    codigo_barras = models.CharField(max_length=200, unique=True)  # Ajusta la longitud según tus necesidades


class ArticuloProveedor(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    codigo_base = models.CharField(max_length=20)  # Código específico del proveedor
    descripcion = models.CharField(max_length=200)  # Descripción específica del proveedor
    precio_base = models.FloatField(default=0.0)
    actualizado = models.BooleanField(default=True)
    fecha = models.DateField(auto_now_add=True, blank=True, null=True)
    
    
    codigo_final = models.CharField(max_length=20)
    precio_final = models.FloatField(default=0.0, blank=True)
    precio_contado = models.FloatField(default=0.0, blank=True)
    precio_cantidad = models.FloatField(default=0.0, blank=True)
    precio_cantidad_contado = models.FloatField(default=0.0, blank=True)
    cartel = models.ForeignKey(Cartel, on_delete=models.CASCADE, blank=True, null=True)