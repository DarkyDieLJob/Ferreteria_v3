from django.db import models
from utils.constantes_django import TIPOS_LOGS

# Create your models here.
class Log(models.Model):
    '''
    
    '''
    fecha = models.DateTimeField(auto_now_add=True)
    nivel = models.CharField(max_length=5,choices=TIPOS_LOGS, default="I")
    msg = models.TextField()
    app_label = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
