import os
import time
from django.conf import settings
import os
from bdd.classes import Patoba

def medir_tiempo(func):
    def wrapper(*args, **kwargs):
        inicio = time.time()  # Tiempo de inicio
        print(f"Se va a ejecutar la función '{func.__name__}'.")
        print(f"Los argumentos son: {args}.")
        print(f"Los argumentos clave son: {kwargs}.")
        resultado = func(*args, **kwargs)  # Ejecutar la función original
        fin = time.time()  # Tiempo de finalización
        print(f"La función '{func.__name__}' tardó {fin - inicio:.4f} segundos.")
        return resultado
    return wrapper

#@medir_tiempo
def buckup():
    ruta_sqlite3 = settings.DATABASES['default']['NAME']
    nombre_archivo_sqlite3 = os.path.basename(ruta_sqlite3)  # Obtiene solo el nombre del archivo
    
    patoba = Patoba(None)
    patoba.subir_sqlite3_a_drive(ruta_sqlite3, nombre_archivo_sqlite3, '1aAipX6U0thSHElqcIV2nsti8738IM2p2')
    
#@medir_tiempo
def reckup():
    ruta_destino_sqlite3 = settings.DATABASES['default']['NAME']
    nombre_archivo_sqlite3 = os.path.basename(ruta_destino_sqlite3)
    
    patoba = Patoba(None)  # O Patoba(None) si no tienes request
    patoba.descargar_sqlite3_de_drive(nombre_archivo_sqlite3, '1aAipX6U0thSHElqcIV2nsti8738IM2p2', ruta_destino_sqlite3)