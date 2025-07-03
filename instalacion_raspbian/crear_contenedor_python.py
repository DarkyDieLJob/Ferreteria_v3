import subprocess
import sys
import os

def ejecutar_comando(comando):
    """Ejecuta un comando en la terminal e imprime la salida."""
    print(f"Ejecutando: {' '.join(comando)}")
    proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proceso.communicate()
    if stdout:
        print(stdout.decode())
    if stderr:
        print(f"Error: {stderr.decode()}")
    return proceso.returncode == 0

def verificar_docker_instalado():
    """Verifica si Docker está instalado."""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        return False

def instalar_docker():
    """Intenta instalar Docker si no está instalado."""
    if not verificar_docker_instalado():
        print("Docker no está instalado. Intentando instalar...")
        ejecutar_comando(["sudo", "apt-get", "update"])
        ejecutar_comando(["sudo", "apt-get", "install", "-y", "docker.io"])
        if verificar_docker_instalado():
            print("Docker instalado exitosamente.")
            # Añadir el usuario actual al grupo docker para no usar sudo
            usuario = os.getlogin()
            if ejecutar_comando(["sudo", "usermod", "-aG", "docker", usuario]):
                print(f"Usuario '{usuario}' añadido al grupo 'docker'. Puede que necesites cerrar sesión y volver a entrar para que los cambios surtan efecto.")
            else:
                print(f"No se pudo añadir el usuario '{usuario}' al grupo 'docker'. Puede que necesites ejecutar los comandos de docker con 'sudo'.")
            return True
        else:
            print("Error al instalar Docker. Por favor, instálalo manualmente.")
            return False
    else:
        print("Docker ya está instalado.")
        return True

def crear_contenedor_django(nombre_base):
    """Crea un volumen y un contenedor de Python para Django."""
    nombre_volumen = f"{nombre_base}_volumen"
    nombre_contenedor = f"{nombre_base}_server"

    print(f"\nCreando volumen: {nombre_volumen}")
    ejecutar_comando(["docker", "volume", "create", nombre_volumen])

    print(f"\nCreando contenedor: {nombre_contenedor}")
    if ejecutar_comando([
        "docker", "run", "-d", "--name", nombre_contenedor,
        "-v", f"{nombre_volumen}:/app",
        "-p", "8000:8000",
        "python:3-slim-buster",
        "sleep", "infinity"
    ]):
        print(f"Contenedor '{nombre_contenedor}' creado exitosamente.")

        print(f"\nConfigurando el contenedor '{nombre_contenedor}'...")
        ejecutar_comando(["docker", "exec", "-it", nombre_contenedor, "apt-get", "update"])
        ejecutar_comando(["docker", "exec", "-it", nombre_contenedor, "apt-get", "install", "-y", "python3-pip"])
        ejecutar_comando(["docker", "exec", "-it", nombre_contenedor, "python3", "-m", "venv", "/app/venv"])
        print("Entorno virtual creado en /app/venv dentro del contenedor.")
    else:
        print(f"Error al crear el contenedor '{nombre_contenedor}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py <nombre_base>")
        sys.exit(1)

    nombre_base = sys.argv[1]

    if instalar_docker():
        crear_contenedor_django(nombre_base)
        print("\n¡Listo! Ahora puedes usar Docker para gestionar tu contenedor Django.")
        print(f"El volumen creado es: {nombre_base}_volumen")
        print(f"El contenedor creado es: {nombre_base}_server")
        print(f"Puedes acceder al contenedor con: 'docker exec -it {nombre_base}_server bash'")
        print("Dentro del contenedor, activa el entorno virtual con: 'source /app/venv/bin/activate'")
        print("Luego podrás clonar tu proyecto Django en la carpeta /app.")