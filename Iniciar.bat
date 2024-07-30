@echo off
cd C:/Users/Programar/Documents/GitHub/Ferreteria_v3
IF NOT EXIST "venv" (
    echo El entorno virtual no existe.
    pause
    exit /b
)
call venv/Scripts/activate
IF %ERRORLEVEL% NEQ 0 (
    echo Error al activar el entorno virtual.
    pause
    exit /b
)
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 192.168.0.231:8000
IF %ERRORLEVEL% NEQ 0 (
    echo Error al iniciar el servidor Django.
    pause
    exit /b
)
pause