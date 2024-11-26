from django.db import models
from utils.constantes_django import TIPOS_LOGS

# Create your models here.
class Log(models.Model):
    '''
    
    '''
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=5,choices=TIPOS_LOGS, default="I")
    msg = models.TextField()
    ruta = models.CharField(max_length="200", default=".loguer")


