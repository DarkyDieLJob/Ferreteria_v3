#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID="1IaqfSk0z3Oy8huw7XpxmFsLaGXE7jouO" \
#   ENV=prod \
#   ./scripts/deploy_reportes.sh

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
PYTHON_BIN=${PYTHON_BIN:-python3}
MANAGE="$PYTHON_BIN $PROJECT_DIR/manage.py"

# Ensure folder ID available (can also be set in Django settings instead)
export REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID=${REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID:-"1IaqfSk0z3Oy8huw7XpxmFsLaGXE7jouO"}

# Prevent starting background workers in actualizador.apps ready()
export RUNNING_ACTUALIZADOR_SCRIPT=1

# Django checks
$MANAGE check --deploy || true

# Migrations
$MANAGE makemigrations reportes --noinput || true
$MANAGE migrate --noinput

# Collect static
$MANAGE collectstatic --noinput

# Optional: clear old sessions
$MANAGE clearsessions || true

echo "Deploy tasks for 'reportes' completed."
