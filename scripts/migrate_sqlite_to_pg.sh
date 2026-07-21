#!/bin/bash
# Script de migracion SQLite -> PostgreSQL
# Ejecutar DENTRO del contenedor web despues de que PostgreSQL este listo
# Uso: docker exec ferreteria_web bash /Ferreteria_v3/scripts/migrate_sqlite_to_pg.sh

set -e

echo "=== Migracion SQLite -> PostgreSQL ==="
echo "Este script asume que:"
echo "1. PostgreSQL esta corriendo y accesible via DB_HOST"
echo "2. El archivo db.sqlite3 existe en /Ferreteria_v3/"
echo "3. Las migraciones ya se ejecutaron en PostgreSQL (migrate)"
echo ""

# Verificar que db.sqlite3 existe
if [ ! -f /Ferreteria_v3/db.sqlite3 ]; then
    echo "ERROR: No se encontro db.sqlite3 en /Ferreteria_v3/"
    exit 1
fi

# Paso 1: Dump desde SQLite
echo "=== Paso 1: Dump data desde SQLite ==="
# Temporalmente cambiar a SQLite para el dump
DB_HOST_BACKUP="$DB_HOST"
export DB_HOST=""
python manage.py dumpdata \
    --natural-foreign \
    --natural-primary \
    --exclude contenttypes \
    --exclude auth.permission \
    --exclude sessions.session \
    --exclude django.admin.log \
    --indent 2 \
    --output /tmp/fulldump.json
echo "Dump creado: $(wc -c < /tmp/fulldump.json) bytes"

# Restaurar DB_HOST para usar PostgreSQL
export DB_HOST="$DB_HOST_BACKUP"

# Paso 2: Verificar que PostgreSQL esta vacio
echo "=== Paso 2: Verificar PostgreSQL ==="
TABLE_COUNT=$(python -c "
import django, os
django.setup()
from django.db import connection
with connection.cursor() as cursor:
    cursor.execute('SELECT count(*) FROM information_schema.tables WHERE table_schema = %s', ['public'])
    print(cursor.fetchone()[0])
")
echo "Tablas en PostgreSQL: $TABLE_COUNT"

# Paso 3: Cargar datos en PostgreSQL
echo "=== Paso 3: Cargar datos en PostgreSQL ==="
python manage.py loaddata /tmp/fulldump.json
echo "Datos cargados exitosamente."

# Paso 4: Verificar
echo "=== Paso 4: Verificar conteos ==="
python -c "
import django
django.setup()
from bdd.models import Item
from django.contrib.auth.models import User
print(f'Items en PostgreSQL: {Item.objects.count()}')
print(f'Users en PostgreSQL: {User.objects.count()}')
"

echo "=== Migracion completada ==="
echo "NO eliminar db.sqlite3 hasta verificar que todo funciona correctamente."
