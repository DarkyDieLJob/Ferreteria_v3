import subprocess
import threading
from actualizador.log_config import logging
from .actualizador_main import principal
from .actualizador_csv import principal_csv, apply_custom_round
import queue
import time
import datetime

def tirar_comando(self, comando="ls"):
    try:
        logging.info(f"Tirando comando: {comando}")
        subprocess.call(comando, shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al intentar enviar el comando {comando}")
        logging.error(e)

def fake_principal():
    logging.info("Iniciando fake-principal")
    while True:
        time.sleep(60)
    logging.info("Finalizando fake-principal")

def fake_principal_csv():
    logging.info("Iniciando fake-principal-csv")
    time.sleep(60)
    logging.info("Finalizando fake-principal-csv")

def fake_apply_custom_round():
    logging.info("Iniciando fake-applay-custom-round")
    time.sleep(60)
    logging.info("Finalizando fake-applay-custom-round")


class HiloManager():
    def __init__(self):
        self.hilos = {
            'hilo':threading.Thread(target=None),
        }

    def nuevo_hilo(self, name, proceso):
        self.hilos[name] = threading.Thread(target=proceso)
    
    def iniciar_hilo(self, name):
        self.hilos[name].start()

    def agregar_proceso(self, name, nuevo, proceso):
        self.hilos[name].join()
        self.nuevo_hilo(nuevo, proceso)
        self.iniciar_hilo(nuevo)



class ColaTareas:
    def __init__(self):
        self.cola_tareas = queue.Queue()
        self.hilo_principal = threading.Thread(target=self.ejecutar_tareas)
        self.hora_inicio = datetime.time(23, 59)  # Hora de inicio: 00:00
        self.fecha_inicio = datetime.date.today()  # Fecha de inicio: hoy

    def agregar_tarea(self, tarea):
        self.cola_tareas.put(tarea)

    def ejecutar_tareas(self):
        ahora = datetime.datetime.now()

        # Calcular la diferencia en segundos y esperar
        tiempo_espera = (datetime.datetime.combine(self.fecha_inicio, self.hora_inicio) - ahora).total_seconds()
        if tiempo_espera > 0:
            time.sleep(tiempo_espera)

        while True:
            tarea = self.cola_tareas.get()
            tarea()
            self.cola_tareas.task_done()

def ejecutar_cola_tareas():
    colaTareas = ColaTareas()
    colaTareas.agregar_tarea(principal)
    colaTareas.agregar_tarea(principal_csv)
    colaTareas.ejecutar_tareas()


#@shared_task
def recoleccion():
    pass

#@shared_task
def etiquetado():
    pass

#@shared_task
def procesar():
    pass

#@shared_task
def recolectar_procesar():
    '''
    Se va a cambiar a futuro cuando
     se refactorize el modo en el que se capuran las planillas.
    '''

    hiloManager = HiloManager()
    hiloManager.nuevo_hilo('principal', principal)
    hiloManager.iniciar_hilo('principal')

    logging.info(hiloManager.hilos['principal'])
    return f"Se registraron o procesaron planillas correctamente."


def actualizador():
    print("Se envio a actualizar via csv...")
    hiloManager = HiloManager()
    hiloManager.nuevo_hilo('principal_csv', principal_csv)
    hiloManager.iniciar_hilo('principal_csv')
    hiloManager.agregar_proceso('principal_csv','apply_custom_round', apply_custom_round)
    logging.info(hiloManager.hilos['principal_csv'])
    logging.info(hiloManager.hilos['apply_custom_round'])

#@shared_task
def actualizar():
    hiloManager = HiloManager()
    hiloManager.nuevo_hilo('actualizador', actualizador)
    hiloManager.iniciar_hilo('actualizador')

    logging.info(hiloManager.hilos['actualizador'])

    return f"Se actualizo la base de datos correctamente."