#!/usr/bin/env bash
#
# ============================================================================
#  release.sh - Script de release para Ferreteria v3
# ============================================================================
#
#  DESCRIPCION:
#    Automatiza la generacion de releases usando conventional commits.
#    Utiliza standard-version para:
#      1. Analizar commits desde el ultimo tag
#      2. Calcular el bump de version (major/minor/patch)
#      3. Actualizar CHANGELOG.md
#      4. Actualizar package.json (version del navbar)
#      5. Crear commit chore(release): X.Y.Z
#      6. Crear tag vX.Y.Z
#
#  USO:
#    ./scripts/release.sh              # Release automatico (detecta bump)
#    ./scripts/release.sh --dry-run    # Previsualizar sin cambios
#    ./scripts/release.sh --patch      # Forzar bump patch (3.10.0 -> 3.10.1)
#    ./scripts/release.sh --minor      # Forzar bump minor (3.10.0 -> 3.11.0)
#    ./scripts/release.sh --major      # Forzar bump major (3.10.0 -> 4.0.0)
#    ./scripts/release.sh --push       # Ademas hace push de commits y tags
#
#  REQUISITOS:
#    - Node.js >= 16
#    - npm (standard-version instalado como devDependency)
#    - Estar en la rama produccion (o pasar --force para usar otra rama)
#    - Working tree limpio (sin cambios sin commitear)
#
#  CONVENCION DE COMMITS:
#    Los commits deben seguir el formato:
#      type(scope): descripcion
#
#    Types reconocidos:
#      feat     -> bump MINOR (nueva funcionalidad)
#      fix      -> bump PATCH (correccion de bug)
#      BREAKING -> bump MAJOR (cambio incompatible)
#      chore, docs, style, refactor, perf, test -> no bump (solo aparecen en changelog)
#
#  EJEMPLOS DE COMMITS:
#    feat(carrito): badge con cantidad de articulos
#    fix(buscador): botones de carrito ya no se solapan en mobile
#    feat(api)!: cambiar formato de respuesta (BREAKING CHANGE)
#
#  FLUJO:
#    1. Verificar precondiciones (rama, working tree, node)
#    2. Mostrar commits desde el ultimo tag
#    3. Ejecutar standard-version (o dry-run)
#    4. Mostrar resumen del release
#    5. (Opcional) Push con --follow-tags
#
#  NOTAS:
#    - standard-version esta DEPRECATED pero sigue funcionando.
#    - El navbar muestra la version desde package.json via bdd/views/base.py
#    - La vista /change_log lee CHANGELOG.md via core_docs/views.py
#    - Los tags son globales (no por rama), pero standard-version solo
#      considera tags alcanzables desde la rama actual.
#
# ============================================================================

set -euo pipefail

# ----------------------------------------------------------------------------
#  Configuracion
# ----------------------------------------------------------------------------
BRANCH_ESPERADA="produccion"
COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[0;34m'
COLOR_NC='\033[0m' # No Color

# ----------------------------------------------------------------------------
#  Helpers
# ----------------------------------------------------------------------------
log_info()  { echo -e "${COLOR_BLUE}[INFO]${COLOR_NC} $*"; }
log_ok()    { echo -e "${COLOR_GREEN}[OK]${COLOR_NC} $*"; }
log_warn()  { echo -e "${COLOR_YELLOW}[WARN]${COLOR_NC} $*"; }
log_error() { echo -e "${COLOR_RED}[ERROR]${COLOR_NC} $*"; exit 1; }

# ----------------------------------------------------------------------------
#  Parseo de argumentos
# ----------------------------------------------------------------------------
DRY_RUN=false
FORCE_BRANCH=false
DO_PUSH=false
RELEASE_AS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)      DRY_RUN=true; shift ;;
        --force)        FORCE_BRANCH=true; shift ;;
        --push)         DO_PUSH=true; shift ;;
        --patch)        RELEASE_AS="--release-as patch"; shift ;;
        --minor)        RELEASE_AS="--release-as minor"; shift ;;
        --major)        RELEASE_AS="--release-as major"; shift ;;
        --help|-h)      head -50 "$0" | tail -48; exit 0 ;;
        *)              log_error "Argumento desconocido: $1 (usar --help)" ;;
    esac
done

# ----------------------------------------------------------------------------
#  1. Verificar precondiciones
# ----------------------------------------------------------------------------
log_info "Verificando precondiciones..."

# Node.js
if ! command -v node &>/dev/null; then
    log_error "Node.js no encontrado. Instalar Node.js >= 16."
fi
NODE_VERSION=$(node --version)
log_ok "Node.js: $NODE_VERSION"

# standard-version instalado
if [ ! -f "node_modules/.bin/standard-version" ]; then
    log_warn "standard-version no instalado. Ejecutando npm install..."
    npm install --save-dev standard-version@9.5.0
fi
log_ok "standard-version disponible"

# Rama actual
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$BRANCH_ESPERADA" ] && [ "$FORCE_BRANCH" = false ]; then
    log_error "Rama actual: '$CURRENT_BRANCH'. Se esperaba '$BRANCH_ESPERADA'. Usar --force para omitir."
fi
log_ok "Rama: $CURRENT_BRANCH"

# Working tree limpio
if [ "$(git status --porcelain)" != "" ]; then
    log_error "Working tree no limpio. Commitear o stashear cambios antes de releasear."
fi
log_ok "Working tree limpio"

# Tag mas reciente (alcanzable desde la rama actual)
LATEST_TAG=$(git tag --merged "$CURRENT_BRANCH" --sort=-v:refname | head -1)
if [ -z "$LATEST_TAG" ]; then
    log_warn "No hay tags previos en esta rama. Se creara el primer release."
    LATEST_TAG="(ninguno)"
fi
log_ok "Ultimo tag alcanzable: $LATEST_TAG"

# Version actual en package.json
CURRENT_VERSION=$(node -p "require('./package.json').version")
log_ok "Version actual en package.json: $CURRENT_VERSION"

# ----------------------------------------------------------------------------
#  2. Mostrar commits desde el ultimo tag
# ----------------------------------------------------------------------------
echo ""
log_info "Commits desde $LATEST_TAG:"
echo "---"
if [ "$LATEST_TAG" = "(ninguno)" ]; then
    git log --oneline -20
else
    git log "$LATEST_TAG..HEAD" --oneline
fi
echo "---"
COMMIT_COUNT=$(git log "$LATEST_TAG..HEAD" --oneline 2>/dev/null | wc -l)
log_info "Total: $COMMIT_COUNT commits desde $LATEST_TAG"

if [ "$COMMIT_COUNT" -eq 0 ] && [ "$LATEST_TAG" != "(ninguno)" ]; then
    log_error "No hay commits nuevos desde $LATEST_TAG. Nada que releasear."
fi

# ----------------------------------------------------------------------------
#  3. Ejecutar standard-version
# ----------------------------------------------------------------------------
echo ""
if [ "$DRY_RUN" = true ]; then
    log_info "Ejecutando DRY RUN (no se haran cambios)..."
    npx standard-version --dry-run $RELEASE_AS
    echo ""
    log_ok "Dry run completado. Revisar output arriba."
    log_info "Ejecutar sin --dry-run para aplicar cambios."
    exit 0
else
    log_info "Ejecutando standard-version..."
    npx standard-version $RELEASE_AS
fi

# ----------------------------------------------------------------------------
#  4. Resumen del release
# ----------------------------------------------------------------------------
NEW_VERSION=$(node -p "require('./package.json').version")
NEW_TAG="v$NEW_VERSION"

echo ""
echo "========================================"
log_ok "Release $NEW_TAG generado exitosamente!"
echo "========================================"
echo ""
log_info "Cambios realizados:"
echo "  - package.json:    $CURRENT_VERSION -> $NEW_VERSION"
echo "  - CHANGELOG.md:    entrada $NEW_TAG agregada"
echo "  - Commit:          chore(release): $NEW_VERSION"
echo "  - Tag:             $NEW_TAG"
echo ""
log_info "El navbar mostrara:  Ferreteria Paoli V-$NEW_VERSION"
log_info "Vista /change_log:   actualizada con nuevos cambios"
echo ""

# ----------------------------------------------------------------------------
#  5. Push (opcional)
# ----------------------------------------------------------------------------
if [ "$DO_PUSH" = true ]; then
    log_info "Haciendo push de commits y tags..."
    git push --follow-tags origin "$CURRENT_BRANCH"
    log_ok "Push completado."
else
    log_info "Para publicar ejecutar:"
    echo "  git push --follow-tags origin $CURRENT_BRANCH"
fi

echo ""
log_ok "Listo!"
