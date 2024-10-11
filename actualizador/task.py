from celery import shared_task
import subprocess
from core_config.log_config import logging
from .actualizador_main import principal
from .actualizador_csv import principal_csv, apply_custom_round

def tirar_comando(self, comando="ls"):
    try:
        logging.info(f"Tirando comando: {comando}")
        subprocess.call(comando, shell=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al intentar enviar el comando {comando}")
        logging.error(e)

class HiloManager():
    def __init__(self):
        self._hilos = {
            'hilo':threading.Thread(target=None),
        }

    def nuevo_hilo(self, name, proceso):
        self.hilos[name] = threading.Trhead(target=proceso)
    
    def iniciar_hilo(self, name):
        self.hilos[name].start()

    def agregar_proceso(self, name, nuevo, proceso):
        self.hilos[name].join()
        self.nuevo_hilo(nuevo, proseso)
        self.iniciar_hilo(nuevo)


@shared_task
def recoleccion():
    pass

@shared_task
def etiquetado():
    pass

@shared_task
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
    return f"Se registraron o procesaron planillas correctamente."


#@shared_task
def actualizar():
    print("Se envio a actualizar via csv...")
    hiloManager = HiloManager()
    hiloManager.nuevo_hilo('principal_csv', principal_csv)
    hiloManager.nuevo_hilo('apply_custom_round', apply_custom_round)
    return f"Se actualizo la base de datos correctamente."