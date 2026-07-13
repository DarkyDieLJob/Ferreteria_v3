---
description: Generar un release con conventional commits en la rama produccion
---

# Release con Conventional Commits

## Precondiciones

1. Estar en la rama `produccion`
2. Working tree limpio (sin cambios sin commitear)
3. Node.js instalado (>= 16)
4. `standard-version` instalado (`npm install` si falta)

## Pasos

1. Verificar precondiciones y commits pendientes:

```bash
git branch --show-current  # debe ser produccion
git status --porcelain     # debe estar vacio
git log <ultimo_tag>..HEAD --oneline  # commits a releasear
```

2. Previsualizar el release (dry run):

```bash
./scripts/release.sh --dry-run
```

3. Generar el release:

```bash
./scripts/release.sh
```

Esto hara automaticamente:
- Bump de version en `package.json` ( alimenta el navbar via `bdd/views/base.py`)
- Actualizacion de `CHANGELOG.md` ( alimenta la vista `/change_log`)
- Commit `chore(release): X.Y.Z`
- Tag `vX.Y.Z`

4. Publicar (push):

```bash
./scripts/release.sh --push
# o manualmente:
git push --follow-tags origin produccion
```

## Forzar tipo de bump

```bash
./scripts/release.sh --patch   # forzar patch (x.y.Z)
./scripts/release.sh --minor   # forzar minor (x.Y.0)
./scripts/release.sh --major   # forzar major (X.0.0)
```

## Convencion de Commits

Los commits deben seguir el formato `type(scope): descripcion`:

- **feat**: nueva funcionalidad -> bump MINOR
- **fix**: correccion de bug -> bump PATCH
- **BREAKING CHANGE** o `!`: cambio incompatible -> bump MAJOR
- **chore, docs, style, refactor, perf, test**: no generan bump

## Componentes involucrados

- `package.json`: version fuente (leida por `bdd/views/base.py:42-57`)
- `CHANGELOG.md`: historial de cambios (leido por `core_docs/views.py:42-48`)
- `static/templates/generic_template.html:95`: navbar muestra `V-{{version}}`
- `core_docs/templates/change_log.html`: renderiza el changelog
- `scripts/release.sh`: script de release documentado
