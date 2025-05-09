import os

# --- Función Generadora de Configuración de Logging ---
def generate_app_logging_config(apps, base_log_dir, base_formatter='verbose'):
    """
    Genera configuraciones de handlers y loggers para cada app especificada.
    """
    app_handlers = {}
    app_loggers = {}

    for app_name in apps:
        app_log_dir = os.path.join(base_log_dir, app_name)
        # Crear directorio específico de la app si no existe
        try:
            os.makedirs(app_log_dir, exist_ok=True)
            # ¡Importante! Considera los permisos en producción.
            # El proceso de Django necesita escribir aquí.
        except OSError as e:
            print(f"ADVERTENCIA: No se pudo crear el directorio de logs para '{app_name}': {e}")
            # Decide si quieres continuar o lanzar una excepción aquí
            # Por ahora, sólo imprimimos una advertencia

        # Handler para INFO y superior específico de la app
        handler_info_name = f'{app_name}_file_info'
        app_handlers[handler_info_name] = {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(app_log_dir, 'info.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': base_formatter,
            'encoding': 'utf-8',
        }

        # Handler para ERROR y superior específico de la app
        handler_error_name = f'{app_name}_file_error'
        app_handlers[handler_error_name] = {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(app_log_dir, 'error.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 3,
            'formatter': base_formatter,
            'encoding': 'utf-8',
        }

        # Logger para la app
        # Capturará logs de esta app y sus submódulos (por propagación)
        logger_name = app_name
        app_loggers[logger_name] = {
            # Los handlers específicos + el de consola para errores
            'handlers': [handler_info_name, handler_error_name, 'console_errors'],
            # Nivel base para el logger. DEBUG para capturar todo y que los handlers filtren.
            # Si pones INFO aquí, los logger.debug() de la app no llegarán a ningún handler.
            'level': 'DEBUG',
            # Propagate a True (default) es crucial para que los submódulos funcionen
            # sin configuración explícita. Poner False aquí rompería eso.
            # Lo dejamos sin especificar (usa el default True) o lo ponemos explícito:
            'propagate': True,
        }

    return app_handlers, app_loggers