from django.db import models

class ModeloBase(models.Model):
    nombre = models.CharField(max_length=30, default='')
    text_display = models.CharField(max_length=30, default='')

    class Meta:
        abstract = True

    def __str__(self):
        text = "{}".format(self.text_display,)
        return text

class Contenedor(ModeloBase):
    html = models.CharField(max_length=250, default='')
    
class Script(ModeloBase):
    html = models.CharField(max_length=250, default='')

class Pie(ModeloBase):
    html = models.CharField(max_length=250, default='')

class Url(ModeloBase):
    ruta = models.CharField(max_length=250, default='')
    contenedor = models.ForeignKey(Contenedor, on_delete=models.CASCADE)
    script = models.ForeignKey(Script, on_delete=models.CASCADE)
    pie = models.ForeignKey(Pie, on_delete=models.CASCADE)

class Nav_Bar(ModeloBase):
    url = models.OneToOneField(Url, on_delete=models.CASCADE)

class Contexto(models.Model):
    json = models.JSONField(default=dict)
