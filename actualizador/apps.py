from django.apps import AppConfig
import logging
import threading # Para identificar el hilo si es necesario

# Obtener el logger
logger = logging.getLogger(__name__) # Mejor usar un logger específico o el de Django

# Flag a nivel de módulo para intentar asegurar que solo se inicie una vez
# incluso si ready() es llamado múltiples veces por alguna razón.
# Nota: Esto NO previene múltiples inicios si Django corre en múltiples procesos
# (ej. gunicorn/uwsgi con varios workers, o el reloader de runserver).
# La lógica dentro de ColaTareasWorker.start_worker() ayuda a mitigar esto
# al no iniciar si el flag interno _worker_started ya está True en esa instancia.
_worker_inicializado = False
_lock_inicializacion = threading.Lock() # Para seguridad en caso de concurrencia aquí

class ActualizadorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'actualizador'

    def ready(self):
        """
        Este método es llamado por Django cuando la aplicación está lista.
        Es un buen lugar para inicializar tareas de fondo, etc.
        """
        global _worker_inicializado
        with _lock_inicializacion:
            if not _worker_inicializado:
                # Solo intenta iniciar si no lo hemos hecho ya en este proceso.
                thread_id = threading.current_thread().name
                logger.info(f"App '{self.name}' lista (en hilo {thread_id}). Intentando iniciar ColaTareasWorker...")

                try:
                    # Importar aquí para evitar problemas de carga temprana
                    from .task import ColaTareasWorker

                    # Obtener la instancia Singleton
                    worker = ColaTareasWorker()

                    # Intentar iniciar el hilo trabajador
                    # El método start_worker() tiene lógica interna para no
                    # iniciar el hilo si ya está corriendo en ESTA instancia.
                    worker.start_worker()

                    logger.info("Llamada a start_worker() completada.")
                    _worker_inicializado = True # Marcar como inicializado en este proceso

                except ImportError:
                    logger.exception(f"Error Crítico: No se pudo importar 'ColaTareasWorker' desde '.tasks'. ¡El worker de tareas no se iniciará!")
                except Exception as e:
                    # Captura cualquier otro error durante la inicialización del worker
                    logger.exception(f"Error Crítico al intentar iniciar ColaTareasWorker en ready(): {e}")
            else:
                 logger.debug(f"App '{self.name}' lista: El worker ya fue inicializado en este proceso.")