import os
from celery import Celery
#esta en la ruta "/Ferreteria_v3/core_config/" y necesito mudarlo a "/" (raiz)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','core_config.settings')

app = Celery(main='core_config')

app.config_from_object('django.conf:settings',namespace='CELERY')

app.autodiscover_tasks()