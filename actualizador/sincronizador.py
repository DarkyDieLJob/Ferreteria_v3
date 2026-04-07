import os
import time
from django.conf import settings
import os
from bdd.classes import Patoba

import logging

logger = logging.getLogger(__name__)


def medir_tiempo(func):
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()  # Tiempo de inicio de alta resolución
        logger.debug("Ejecutando función %s args=%s kwargs=%s", func.__name__, args, kwargs)
        resultado = func(*args, **kwargs)  # Ejecutar la función original
        fin = time.perf_counter()  # Tiempo de finalización
        logger.info("Función %s completada en %.4f s", func.__name__, (fin - inicio))
        return resultado

    return wrapper


# @medir_tiempo
def buckup():
    ruta_sqlite3 = settings.DATABASES["default"]["NAME"]
    nombre_archivo_sqlite3 = os.path.basename(
        ruta_sqlite3
    )  # Obtiene solo el nombre del archivo

    patoba = Patoba(None)
    patoba.subir_sqlite3_a_drive(
        ruta_sqlite3, nombre_archivo_sqlite3, "1aAipX6U0thSHElqcIV2nsti8738IM2p2"
    )


# @medir_tiempo
def reckup():
    ruta_destino_sqlite3 = settings.DATABASES["default"]["NAME"]
    nombre_archivo_sqlite3 = os.path.basename(ruta_destino_sqlite3)

    patoba = Patoba(None)  # O Patoba(None) si no tienes request
    patoba.descargar_sqlite3_de_drive(
        nombre_archivo_sqlite3,
        "1aAipX6U0thSHElqcIV2nsti8738IM2p2",
        ruta_destino_sqlite3,
    )
