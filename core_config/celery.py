import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE','core_config.settings')

app = Celery(main='core_config', broker="amqp://guest:guest@0.0.0.0:5672//", )

app.config_from_object('django.conf:settings',namespace='CELERY')

app.autodiscover_tasks()