@echo off
cd C:/Users/Programar/Documents/GitHub/Ferreteria_v3
IF NOT EXIST "venv" (
    echo Creando entorno virtual...
    python -m virtualenv venv
)
call venv/Scripts/activate
IF %ERRORLEVEL% NEQ 0 (
    echo Error al activar el entorno virtual.
    pause
    exit /b
)
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    echo Error al instalar las dependencias.
    pause
    exit /b
)

