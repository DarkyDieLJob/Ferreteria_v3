"""
Configuración local para desarrollo.
Este archivo debe ser ignorado por git.
"""
from .settings import *

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
