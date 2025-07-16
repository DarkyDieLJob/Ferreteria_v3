"""
Configuración local para desarrollo.
Este archivo debe ser ignorado por git.
"""
from .settings import *
import os

# Configuración de plantillas para incluir las de DRF-YASG
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'venv/lib/python3.10/site-packages/drf_yasg/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core_andamios.context_processors.mi_procesador_de_contexto',
            ],
            'libraries': {
                'staticfiles': 'django.templatetags.static',
            },
        },
    },
]

# Asegurarse de que las aplicaciones necesarias estén en INSTALLED_APPS
if 'drf_yasg' not in INSTALLED_APPS:
    INSTALLED_APPS += ['drf_yasg']

# Configuración de DRF YASG
SWAGGER_SETTINGS = {
    'DEFAULT_INFO': 'core_config.api.v4.urls.api_info',
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
    'DEFAULT_MODEL_RENDERING': 'example',
    'DEFAULT_MODEL_DEPTH': 2,
}

REDOC_SETTINGS = {
    'LAZY_RENDERING': True,
    'HIDE_HOSTNAME': False,
    'EXPAND_DEFAULT_TAGS': True,
}

# Aplicaciones adicionales para desarrollo
INSTALLED_APPS += [
    'core_testing',
    'django_extensions',  # Para generación de diagramas
    'uml_visualizer',    # Nuestra aplicación de visualización UML
    'django.contrib.humanize',  # Para filtros de plantilla como intcomma
]

# Configuración de zona horaria
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_TZ = True

# Configuración para testing
TESTING = True

# Configuración de base de datos para testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Configuración de logging para testing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core_testing': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
