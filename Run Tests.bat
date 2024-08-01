@echo off
cd C:/Users/LaFerreteria/Documents/GitHub/Ferreteria_v3
IF %ERRORLEVEL% NEQ 0 (
    echo No se encontro la ruta... estaremos en casa seguramente
    cd C:/Users/programar/Documents/GitHub/Ferreteria_v3
    pause
)

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
pytest
IF %ERRORLEVEL% NEQ 0 (
    echo Error al iniciar el test.
    pause
    exit /b
)
pause