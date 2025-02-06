import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'
import django
django.setup()

from bdd.models import Lista_Pedidos

def setear_false_lista_faltantes():
    pedidos = Lista_Pedidos.objects.all()
    for pedido in pedidos:
        pedido.pedido = False
        pedido.save()

if __name__ == '__main__':
    setear_false_lista_faltantes()