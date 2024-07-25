import os

# Usa os.getcwd() para obtener el directorio actual
directorio = os.getcwd()

# Abre tu archivo .gitignore en modo append
with open('.gitignore', 'a') as gitignore:
    # Usa os.listdir para obtener los nombres de todos los archivos en el directorio
    for nombre_archivo in os.listdir(directorio):
        # Si el nombre del archivo termina en .csv, lo agrega al .gitignore
        if nombre_archivo.endswith('.csv'):
            gitignore.write(nombre_archivo + '\n')


# Abre tu archivo .gitignore en modo lectura
with open('.gitignore', 'r') as gitignore:
    # Lee cada línea en el archivo .gitignore
    for linea in gitignore:
        # Si la línea termina en .csv, intenta eliminar el archivo del seguimiento de Git
        if linea.strip().endswith('.csv'):
            os.system(f'git rm --cached {linea.strip()}')
