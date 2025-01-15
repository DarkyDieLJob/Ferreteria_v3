def arrancar_django_config():
    '''
    Este metodo se encarga de arrancar la configuracion de Django.
    
    '''
    import os
    os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'
    import django
    django.setup()