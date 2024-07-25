from django.db import models

# Create your models here.
class Modelo_Base(models.Model):
    nombre = models.CharField(max_length=30, default='')
    elemento_html = models.CharField(max_length=30, default='')
    
    def __str__(self):
        text = "{}".format(self.nombre,)
        return text
    
    class Meta:
        abstract = True

class Modelo_Tablas(Modelo_Base):
    lista_de_titulos = models.TextField(max_length=300, default='')
    lista_articulos = models.TextField(max_length=300, default='')
 
    
class Modelo_Formularios(Modelo_Base):
    lista_de_campos = models.TextField(max_length=300, default='')
 
    
class Modelo_Tarjetas(Modelo_Base):
    titulo = models.CharField(max_length=30, default='')
    descripcion = models.CharField(max_length=30, default='')
    
class Modelo_Listas(Modelo_Base):
    pass
 
class Paginas(models.Model):
    
    tiene_tabla = models.BooleanField(default=False)
    modelo_tablas = models.ManyToManyField(Modelo_Tablas)
    
    tiene_formulario = models.BooleanField(default=False)
    modelo_formularios = models.ManyToManyField(Modelo_Formularios)
    
    tiene_tarjeta = models.BooleanField(default=False)
    modelo_tarjetas = models.ManyToManyField(Modelo_Tarjetas)
    
    tiene_lista = models.BooleanField(default=False)
    modelo_lista = models.ManyToManyField(Modelo_Listas)

    def __str__(self):
        text = "{}".format(self.html,)
        return text
    
