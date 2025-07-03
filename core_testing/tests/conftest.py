"""
Configuración de pytest para las pruebas de Django.
"""
import os
import sys
import django
from django.conf import settings

# Configuración básica de Django para pruebas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

def pytest_configure():
    """Configura el entorno de pruebas de Django."""
    # Configuración mínima necesaria para las pruebas
    settings_dict = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        'INSTALLED_APPS': [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'core_testing',
        ],
        'MIDDLEWARE': [
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
        'TEMPLATES': [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'APP_DIRS': True,
            },
        ],
        'ROOT_URLCONF': 'core_testing.urls',
        'SECRET_KEY': 'test-secret-key',
    }
    
    # Aplicar la configuración
    settings.configure(**settings_dict)
    
    # Inicializar Django
    django.setup()
