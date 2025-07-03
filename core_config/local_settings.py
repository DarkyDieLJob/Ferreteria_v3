"""
Configuración local para desarrollo.
Este archivo debe ser ignorado por git.
"""
from .settings import *

# Agregar core_testing a INSTALLED_APPS
INSTALLED_APPS += [
    'core_testing',
]

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
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
