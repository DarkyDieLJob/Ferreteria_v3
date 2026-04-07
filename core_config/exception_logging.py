import logging


class ExceptionLoggingMiddleware:
    """
    Captura excepciones no manejadas en vistas y las registra con logger.exception
    usando como nombre de logger el módulo de la vista cuando es posible.
    No altera la respuesta final (re-lanza la excepción) y se ejecuta temprano.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception:
            logger_name = 'django.request'
            try:
                rm = getattr(request, 'resolver_match', None)
                if rm is not None:
                    func = getattr(rm, 'func', None)
                    module = getattr(func, '__module__', None)
                    if module:
                        logger_name = module
            except Exception:
                # En caso de que resolver_match no esté disponible o falle, usar por defecto
                logger_name = 'django.request'

            logger = logging.getLogger(logger_name)
            # request_id, user e ip serán añadidos por el filtro request_context
            logger.exception("Unhandled exception processing %s %s", request.method, request.path)
            raise
