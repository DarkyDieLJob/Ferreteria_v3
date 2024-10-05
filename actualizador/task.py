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

@shared_task
def recoleccion():
    pass

@shared_task
def etiquetado():
    pass

@shared_task
def procesar():
    pass

@shared_task
def recolectar_procesar():
    '''
    Se va a cambiar a futuro cuando
     se refactorize el modo en el que se capuran las planillas.
    '''
    principal()
    return f"Se registraron o procesaron planillas correctamente."


@shared_task
def actualizar():
    print("Se envio a actualizar via csv...")
    principal_csv()
    apply_custom_round()
    return f"Se actualizo la base de datos correctamente."