#!/bin/bash
# Script de deploy para migracion a docker-compose + PostgreSQL
# Ejecutar en el VPS (Raspberry Pi) despues de las 19:30 HS
# Uso: bash deploy.sh

set -e

echo "========================================="
echo "  DEPLOY FERRETERIA v3 - Docker Compose"
echo "  $(date)"
echo "========================================="

# Variables
BACKUP_DIR="/home/diel/backup_pre_migracion_$(date +%Y%m%d_%H%M%S)"
OLD_CONTAINER="django_server"

echo ""
echo "=== FASE 1: BACKUP TOTAL ==="
mkdir -p "$BACKUP_DIR"

# Backup DB
echo "Backupeando db.sqlite3..."
docker cp $OLD_CONTAINER:/Ferreteria_v3/db.sqlite3 "$BACKUP_DIR/"
echo "  OK: $(ls -lh $BACKUP_DIR/db.sqlite3 | awk '{print $5}')"

# Backup media
echo "Backupeando media/..."
docker cp $OLD_CONTAINER:/Ferreteria_v3/media "$BACKUP_DIR/media"
echo "  OK: $(du -sh $BACKUP_DIR/media | awk '{print $1}')"

# Backup credenciales
echo "Backupeando credenciales..."
docker cp $OLD_CONTAINER:/Ferreteria_v3/service_credentials.json "$BACKUP_DIR/" 2>/dev/null || echo "  (no existe)"
docker cp $OLD_CONTAINER:/Ferreteria_v3/mp_access_token.txt "$BACKUP_DIR/" 2>/dev/null || echo "  (no existe)"
docker cp $OLD_CONTAINER:/Ferreteria_v3/core_config/settings.py "$BACKUP_DIR/settings_prod.py" 2>/dev/null || echo "  (no existe)"
echo "  OK"

# Backup logs (opcional, solo error logs)
echo "Backupeando error logs..."
mkdir -p "$BACKUP_DIR/logs"
for app in actualizador bdd facturacion pedido; do
    docker cp $OLD_CONTAINER:/Ferreteria_v3/logs/$app/error.log "$BACKUP_DIR/logs/${app}_error.log" 2>/dev/null || true
done
echo "  OK"

echo ""
echo "Backup completo en: $BACKUP_DIR"
echo "Tamaño total: $(du -sh $BACKUP_DIR | awk '{print $1}')"

echo ""
echo "=== FASE 2: VERIFICAR BACKUP ==="
echo "Archivos en backup:"
ls -la "$BACKUP_DIR/"
echo ""
echo "¿Verificar que el backup se descargo a local via SCP antes de continuar?"
echo "Comando sugerido en local:"
echo "  sshpass -p '224436aA' scp -r diel@ferreteria.tail1ca260.ts.net:$BACKUP_DIR ./backup_pre_migracion/"
echo ""
echo "Presionar ENTER para continuar o Ctrl+C para abortar..."
read

echo ""
echo "=== FASE 3: DETENER CONTENEDOR VIEJO ==="
docker stop $OLD_CONTAINER
echo "Contenedor $OLD_CONTAINER detenido (no eliminado, para rollback)"

echo ""
echo "=== FASE 4: BUILD Y START CON COMPOSE ==="
cd /home/diel/Ferreteria_v3
docker compose build
docker compose up -d db
echo "Esperando a que PostgreSQL este listo..."
sleep 10
docker compose up -d web
echo "Esperando a que Django inicie..."
sleep 10

echo ""
echo "=== FASE 5: MIGRACION DE DATOS ==="
# Copiar db.sqlite3 al contenedor web para el dump
docker cp "$BACKUP_DIR/db.sqlite3" ferreteria_web:/Ferreteria_v3/db.sqlite3
# Ejecutar migracion
docker exec ferreteria_web bash /Ferreteria_v3/scripts/migrate_sqlite_to_pg.sh

echo ""
echo "=== FASE 6: VERIFICACION ==="
echo "Test HTTP:"
curl -s -o /dev/null -w "HTTP %{http_code}" http://localhost:8000/ || echo "FAIL"
echo ""
echo "Items en DB:"
docker exec ferreteria_web python -c "
import django; django.setup()
from bdd.models import Item
print(f'  Items: {Item.objects.count()}')
"

echo ""
echo "========================================="
echo "  DEPLOY COMPLETADO"
echo "  Backup: $BACKUP_DIR"
echo "  Para rollback: docker start $OLD_CONTAINER && docker compose down"
echo "========================================="
