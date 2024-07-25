from django.db import models

class Comando(models.Model):
    comando = models.CharField(max_length=500)
    def __str__(self):
        text = "{}".format(self.comando,)
        return text

class Boleta(models.Model):
    comandos = models.ManyToManyField(Comando, through='OrdenComando')
    tipo = models.CharField(max_length=1)  # 'A', 'B' o 'C'
    impreso = models.BooleanField(default=True)
    def __str__(self):
        text = "Tipo: {} - Impreso: {}".format(self.tipo, str(self.impreso))
        return text

class OrdenComando(models.Model):
    boleta = models.ForeignKey(Boleta, on_delete=models.CASCADE)
    comando = models.ForeignKey(Comando, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField()
    def __str__(self):
        text = "{}".format(self.boleta,)
        return text
