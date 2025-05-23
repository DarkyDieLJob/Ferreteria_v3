import subprocess
import threading
import logging
import queue
import time
import datetime
import sys
from typing import Optional # Para logging más detallado si es necesario

# Configura un logger específico para este módulo si lo deseas, o usa el root logger
logger = logging.getLogger(__name__)

# --- Importación de tus tareas reales ---
# Asegúrate de que estos archivos y funciones realmente existan en tu app 'actualizador'
try:
    from .actualizador_main import principal
    logger.debug("Importado 'principal' desde .actualizador_main")
except ImportError:
    logger.error("No se pudo importar 'principal' desde .actualizador_main. La tarea no estará disponible.")
    def principal(): # Define una función dummy para evitar NameError más tarde
        logger.error("La tarea 'principal' no está definida debido a un error de importación.")

try:
    from .actualizador_csv import principal_csv, apply_custom_round
    logger.debug("Importado 'principal_csv' y 'apply_custom_round' desde .actualizador_csv")
except ImportError:
    logger.error("No se pudo importar 'principal_csv' o 'apply_custom_round' desde .actualizador_csv.")
    def principal_csv():
        logger.error("La tarea 'principal_csv' no está definida.")
    def apply_custom_round():
         logger.error("La tarea 'apply_custom_round' no está definida.")

try:
    from .sincronizador import buckup # O 'backup' si el nombre correcto es ese
    logger.debug("Importado 'buckup' desde .sincronizador")
except ImportError:
    logger.error("No se pudo importar 'buckup' desde .sincronizador.")
    def buckup():
        logger.error("La tarea 'buckup' no está definida.")

# --- Tus funciones existentes ---

def tirar_comando(comando="ls"): # Quitamos 'self', no es un método de clase aquí
    try:
        logging.info(f"Tirando comando: {comando}")
        # Usar Popen podría ser mejor para no bloquear si es necesario, pero call es más simple
        subprocess.call(comando, shell=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e: # Capturar FileNotFoundError también
        logging.error(f"Error al intentar ejecutar el comando '{comando}': {e}")
    except Exception as e:
        logging.error(f"Error inesperado al ejecutar el comando '{comando}': {e}", exc_info=True)


def fake_principal():
    logging.info("Iniciando fake-principal")
    # Cuidado: Este while True nunca termina! Si se ejecuta, bloqueará el hilo.
    # Probablemente debería tener una condición de salida o ser rediseñado.
    # while True:
    #    time.sleep(60)
    time.sleep(5) # Simular trabajo finito
    logging.info("Finalizando fake-principal")

def fake_principal_csv():
    logging.info("Iniciando fake-principal-csv")
    time.sleep(3) # Simular trabajo finito
    logging.info("Finalizando fake-principal-csv")

def fake_apply_custom_round():
    logging.info("Iniciando fake-applay-custom-round")
    time.sleep(4) # Simular trabajo finito
    logging.info("Finalizando fake-applay-custom-round")


# --- Tu HiloManager existente ---
# ADVERTENCIA: Crear instancias locales de esto en funciones no gestionará hilos
# de forma centralizada. El método agregar_proceso() es BLOQUEANTE debido a .join().
# Considera refactorizar si necesitas gestión avanzada de hilos.
class HiloManager():
    def __init__(self):
        self.hilos = {
            # No tiene sentido inicializar con un hilo sin target
            # 'hilo':threading.Thread(target=None),
        }

    def nuevo_hilo(self, name, proceso, *args, **kwargs): # Permitir args/kwargs
        if name in self.hilos and self.hilos[name].is_alive():
             logger.warning(f"Intentando crear nuevo hilo '{name}' pero ya existe uno vivo.")
             # Podrías decidir no hacer nada, o manejarlo de otra forma
             return
        # Crear hilo daemon para que no impida salir a la aplicación principal
        self.hilos[name] = threading.Thread(target=proceso, args=args, kwargs=kwargs, daemon=True)
        logger.info(f"Hilo '{name}' creado apuntando a '{proceso.__name__}'.")

    def iniciar_hilo(self, name):
        if name in self.hilos:
            if not self.hilos[name].is_alive():
                logger.info(f"Iniciando hilo '{name}'...")
                self.hilos[name].start()
            else:
                logger.warning(f"Intentando iniciar hilo '{name}' pero ya está corriendo.")
        else:
            logger.error(f"Intentando iniciar hilo '{name}' pero no existe.")


    def agregar_proceso(self, name, nuevo_name, proceso_nuevo, *args_nuevo, **kwargs_nuevo):
        # !!! ADVERTENCIA: ESTE MÉTODO ES BLOQUEANTE !!!
        if name in self.hilos:
            logger.info(f"Esperando que el hilo '{name}' termine antes de agregar '{nuevo_name}'...")
            self.hilos[name].join() # Bloquea hasta que el hilo 'name' termine
            logger.info(f"Hilo '{name}' terminado. Creando e iniciando '{nuevo_name}'.")
            self.nuevo_hilo(nuevo_name, proceso_nuevo, *args_nuevo, **kwargs_nuevo)
            self.iniciar_hilo(nuevo_name)
        else:
             logger.error(f"Intentando agregar proceso después del hilo '{name}', pero este no existe.")


# --- Implementación de la Cola de Tareas en Segundo Plano (Corregida) ---

class ColaTareasWorker:
    """
    Gestor Singleton para una cola de tareas simple ejecutada en un hilo
    separado en segundo plano. Las tareas se agregan de forma no bloqueante.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ColaTareasWorker, cls).__new__(cls)
        return cls._instance

    def __init__(self, hora_inicio: Optional[datetime.time] = None):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self.cola_tareas = queue.Queue()
                    self.hilo_principal = threading.Thread(target=self.ejecutar_tareas, daemon=True)
                    # La lógica de hora_inicio/fecha_inicio aquí es global para el worker.
                    # Si necesitas scheduling por tarea, usa Celery/Django-Q.
                    self.hora_inicio = hora_inicio if hora_inicio else datetime.time(23, 59)
                    self._worker_started = False
                    self._initialized = True
                    logger.info("Instancia de ColaTareasWorker inicializada.")

    def start_worker(self):
        with self._lock:
            if not self._worker_started and hasattr(self, 'hilo_principal') and self.hilo_principal:
                logger.info("Iniciando hilo trabajador de la cola de tareas...")
                try:
                    self.hilo_principal.start()
                    self._worker_started = True
                    logger.info("Hilo trabajador iniciado correctamente.")
                except RuntimeError as e:
                     # Podría pasar si se intenta iniciar un hilo ya iniciado o terminado
                     logger.error(f"Error al intentar iniciar el hilo trabajador: {e}")
                     # Podríamos intentar recrear el hilo si es necesario y posible
            elif self._worker_started:
                logger.debug("El hilo trabajador ya estaba iniciado.")
            else:
                 logger.error("No se pudo iniciar el hilo trabajador (hilo_principal no existe?).")


    def agregar_tarea(self, tarea, *args, **kwargs):
        """Agrega una tarea (función) y sus argumentos a la cola. No bloqueante."""
        if not callable(tarea):
             logger.error(f"Intento de agregar algo que no es una función a la cola: {tarea}")
             return
        tarea_nombre = getattr(tarea, '__name__', repr(tarea))
        logger.info(f"Agregando tarea '{tarea_nombre}' a la cola.")
        self.cola_tareas.put((tarea, args, kwargs))
        # Asegurarse que el worker esté corriendo (importante si se agregan tareas antes del ready())
        self.start_worker()

    def ejecutar_tareas(self):
        """
        Método ejecutado por el hilo trabajador. Espera y procesa tareas de la cola.
        """
        logger.info(f"Hilo trabajador [{threading.current_thread().name}] iniciado. Esperando tareas...")

        # Lógica de espera inicial (opcional) - Afecta al primer arranque antes de la hora
        ahora = datetime.datetime.now()
        fecha_inicio_hoy = datetime.date.today()
        proxima_ejecucion_inicial = datetime.datetime.combine(fecha_inicio_hoy, self.hora_inicio)

        if ahora < proxima_ejecucion_inicial:
            tiempo_espera = (proxima_ejecucion_inicial - ahora).total_seconds()
            if tiempo_espera > 0:
                logger.info(f"Hilo trabajador esperando {tiempo_espera:.2f} segundos hasta las {self.hora_inicio}...")
                time.sleep(tiempo_espera)

        logger.info("Hilo trabajador activo y procesando cola...")
        while True:
            try:
                # get() es bloqueante por defecto, esperará si la cola está vacía
                tarea_func, args, kwargs = self.cola_tareas.get()
                tarea_nombre = getattr(tarea_func, '__name__', repr(tarea_func))
                logger.info(f"Procesando tarea '{tarea_nombre}'...")
                try:
                    # Ejecutar la tarea
                    tarea_func(*args, **kwargs)
                    logger.info(f"Tarea '{tarea_nombre}' completada.")
                except Exception as e:
                    logger.error(f"Error al ejecutar la tarea '{tarea_nombre}': {e}", exc_info=True)
                finally:
                    self.cola_tareas.task_done() # Marca la tarea como completada
            except queue.Empty:
                # Teóricamente no debería pasar con get() bloqueante sin timeout
                logger.warning("La cola estaba vacía inesperadamente? Esperando...")
                time.sleep(1)
            except Exception as e:
                # Error en el propio bucle del worker
                logger.error(f"Error inesperado en el bucle del worker de tareas: {e}", exc_info=True)
                # Esperar un poco para no saturar en caso de errores repetitivos
                time.sleep(5)

# --- Función para llamar desde las vistas (NO BLOQUEANTE) ---
def agregar_tareas_en_cola(hora_inicio: Optional[datetime.time] = None):
    """
    Función auxiliar para agregar el conjunto estándar de tareas
    (principal, csv, backup) a la cola compartida. Retorna inmediatamente.
    """
    logger.info("Solicitud para agregar tareas estándar a la cola...")
    try:
        worker = ColaTareasWorker() # Obtiene la instancia Singleton
        # Asegúrate que las funciones referenciadas existan y estén importadas
        worker.hora_inicio = hora_inicio if hora_inicio else datetime.time(23, 59)
        worker.agregar_tarea(principal)
        worker.agregar_tarea(principal_csv)
        worker.agregar_tarea(buckup) # O backup si es el nombre correcto
        logger.info("Tareas estándar (principal, csv, backup) agregadas a la cola.")
    except NameError as ne:
         # Esto pasa si una de las funciones (principal, etc.) no se pudo importar
         logger.error(f"Error al agregar tarea - ¿Función no importada correctamente?: {ne}", exc_info=True)
    except Exception as e:
        logger.error(f"Error inesperado al agregar tareas a la cola: {e}", exc_info=True)


# --- Tus otras funciones y placeholders ---

# @shared_task # Placeholder para futura migración a Celery?
def recoleccion():
    pass

# @shared_task
def etiquetado():
    pass

# @shared_task
def procesar():
    pass

# @shared_task
def recolectar_procesar():
    '''
    Se va a cambiar a futuro cuando
     se refactorize el modo en el que se capuran las planillas.
    '''
    # Esta función inicia un hilo usando una instancia LOCAL de HiloManager.
    # El hilo 'principal' se ejecutará, pero no hay gestión centralizada.
    logger.info("Ejecutando recolectar_procesar (usando HiloManager local)...")
    hiloManager = HiloManager()
    hiloManager.nuevo_hilo('principal', principal) # Asume que 'principal' existe
    hiloManager.iniciar_hilo('principal')
    # La función retorna inmediatamente, el hilo 'principal' queda corriendo.
    logger.info(f"Hilo 'principal' iniciado desde recolectar_procesar: {hiloManager.hilos.get('principal')}")
    return f"Se inició el proceso de planillas."


def actualizador():
    # Esta función usa HiloManager local y su método BLOQUEANTE agregar_proceso.
    logger.info("Ejecutando actualizador (puede bloquear)...")
    print("Se envio a actualizar via csv...") # Evitar prints directos, usar logger
    logger.info("Se envio a actualizar via csv...")
    hiloManager = HiloManager()
    hiloManager.nuevo_hilo('principal_csv', principal_csv) # Asume que existe
    hiloManager.iniciar_hilo('principal_csv')
    logger.info(f"Hilo 'principal_csv' iniciado desde actualizador: {hiloManager.hilos.get('principal_csv')}")
    # La siguiente línea BLOQUEARÁ hasta que 'principal_csv' termine.
    hiloManager.agregar_proceso('principal_csv','apply_custom_round', apply_custom_round) # Asume que existen
    logger.info(f"Hilo 'apply_custom_round' iniciado después de 'principal_csv': {hiloManager.hilos.get('apply_custom_round')}")
    logger.info("Función 'actualizador' completada (después del bloqueo).")


# @shared_task
def actualizar():
    # Inicia la función 'actualizador' (que puede bloquear) en un hilo nuevo.
    logger.info("Ejecutando 'actualizar' (inicia 'actualizador' en un hilo)...")
    hiloManager = HiloManager()
    # Inicia la función 'actualizador' en un hilo separado
    hiloManager.nuevo_hilo('actualizador_thread', actualizador)
    hiloManager.iniciar_hilo('actualizador_thread')
    # Esta función 'actualizar' retorna inmediatamente.
    # El hilo 'actualizador_thread' ejecutará 'actualizador', que a su vez puede bloquear.
    logger.info(f"Hilo 'actualizador_thread' iniciado: {hiloManager.hilos.get('actualizador_thread')}")
    return f"Se inició la actualización de la base de datos en segundo plano."

