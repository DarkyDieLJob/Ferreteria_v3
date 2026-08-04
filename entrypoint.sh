#!/bin/bash
set -e

echo "=== Entrypoint: iniciando ==="

# Esperar a que PostgreSQL esté listo
if [ -n "$DB_HOST" ]; then
    echo "Esperando PostgreSQL en $DB_HOST:$DB_PORT..."
    while ! python -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('$DB_HOST', int('${DB_PORT:-5432}')))
    s.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null; do
        sleep 1
    done
    echo "PostgreSQL está listo."
fi

echo "=== Ejecutando migrate ==="
python manage.py migrate --noinput

echo "=== Ejecutando collectstatic ==="
python manage.py collectstatic --noinput

echo "=== Iniciando gunicorn ==="
exec gunicorn core_config.wsgi:application \
    --config gunicorn.conf.py
