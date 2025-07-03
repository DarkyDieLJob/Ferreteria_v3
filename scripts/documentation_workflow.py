#!/usr/bin/env python3
"""
Script para automatizar el flujo de trabajo de documentación.

Este script ayuda a manejar los cambios de documentación siguiendo el flujo:
1. Crear rama de documentación desde develop
2. Mover cambios de documentación a la rama
3. Crear PR a la rama documentation
4. Luego crear PR de documentation a develop
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Tuple, List, Optional

# Configuración
DOC_BRANCH = "documentation"
DEVELOP_BRANCH = "develop"
FEATURE_PREFIX = "feature/documentation"

def run_command(cmd: List[str], cwd: str = None) -> Tuple[bool, str]:
    """Ejecuta un comando y devuelve (éxito, salida)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            check=True,
            text=True,
            capture_output=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def get_current_branch() -> str:
    """Obtiene la rama actual."""
    success, output = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if not success:
        print(f"Error al obtener la rama actual: {output}")
        sys.exit(1)
    return output

def check_git_status() -> bool:
    """Verifica si hay cambios sin confirmar."""
    success, output = run_command(["git", "status", "--porcelain"])
    if not success:
        print(f"Error al verificar el estado de git: {output}")
        return False
    return bool(output.strip())

def create_documentation_branch() -> bool:
    """Crea la rama de documentación si no existe."""
    # Verificar si la rama documentation existe
    success, _ = run_command(["git", "show-ref", "--verify", f"refs/heads/{DOC_BRANCH}"])
    
    if not success:
        print(f"Creando rama {DOC_BRANCH} desde {DEVELOP_BRANCH}...")
        success, output = run_command(["git", "checkout", "-b", DOC_BRANCH, DEVELOP_BRANCH])
        if not success:
            print(f"Error al crear la rama {DOC_BRANCH}: {output}")
            return False
        
        # Hacer push de la rama al repositorio remoto
        success, output = run_command(["git", "push", "-u", "origin", DOC_BRANCH])
        if not success:
            print(f"Error al hacer push de la rama {DOC_BRANCH}: {output}")
            return False
        
        print(f"Rama {DOC_BRANCH} creada exitosamente.")
    else:
        print(f"La rama {DOC_BRANCH} ya existe.")
    
    return True

def create_feature_branch() -> str:
    """Crea una rama de feature para los cambios de documentación."""
    # Obtener un nombre descriptivo para la rama
    branch_name = input("Ingrese un nombre descriptivo para la rama de documentación (ej: setup-docs): ")
    branch_name = branch_name.strip().replace(" ", "-")
    feature_branch = f"{FEATURE_PREFIX}-{branch_name}"
    
    # Crear la rama desde develop
    success, output = run_command(["git", "checkout", "-b", feature_branch, DEVELOP_BRANCH])
    if not success:
        print(f"Error al crear la rama {feature_branch}: {output}")
        sys.exit(1)
    
    print(f"Rama {feature_branch} creada exitosamente.")
    return feature_branch

def commit_changes():
    """Confirma los cambios con un mensaje descriptivo."""
    # Mostrar cambios
    run_command(["git", "status"])
    
    # Preguntar por el mensaje del commit
    commit_message = input("\nIngrese un mensaje para el commit: ")
    if not commit_message.strip():
        commit_message = "docs: actualización de documentación"
    
    # Hacer commit
    success, output = run_command(["git", "commit", "-m", commit_message])
    if not success:
        print(f"Error al hacer commit: {output}")
        return False
    
    print("Cambios confirmados exitosamente.")
    return True

def push_changes(branch: str):
    """Hace push de los cambios al repositorio remoto."""
    print(f"\nHaciendo push de los cambios a {branch}...")
    success, output = run_command(["git", "push", "-u", "origin", branch])
    if not success:
        print(f"Error al hacer push: {output}")
        return False
    
    print(f"Cambios subidos exitosamente a {branch}.")
    return True

def create_pr(base: str, head: str, title: str = None):
    """Crea un Pull Request usando el comando gh (GitHub CLI)."""
    if not title:
        title = f"Documentation: {head}"
    
    print(f"\nCreando PR desde {head} a {base}...")
    success, output = run_command([
        "gh", "pr", "create",
        "--base", base,
        "--head", head,
        "--title", title,
        "--body", f"Actualización de documentación para {head}"
    ])
    
    if not success:
        print(f"No se pudo crear el PR automáticamente. Por favor, créalo manualmente en GitHub/GitLab.")
        print(f"Base: {base}, Head: {head}")
        return False
    
    print(f"PR creado exitosamente: {output}")
    return True

def main():
    print("=== Flujo de Trabajo de Documentación ===\n")
    
    # 1. Verificar estado de git
    if check_git_status():
        print("\n¡Atención! Hay cambios sin confirmar en el repositorio.")
        confirm = input("¿Desea continuar de todos modos? (s/n): ")
        if confirm.lower() != 's':
            print("Operación cancelada.")
            sys.exit(1)
    
    # 2. Crear rama de documentación si no existe
    if not create_documentation_branch():
        print("No se pudo crear la rama de documentación.")
        sys.exit(1)
    
    # 3. Crear rama de feature para los cambios
    current_branch = get_current_branch()
    if current_branch == DEVELOP_BRANCH:
        feature_branch = create_feature_branch()
    else:
        print(f"\nUsando la rama actual: {current_branch}")
        feature_branch = current_branch
    
    # 4. Mostrar instrucciones para agregar cambios
    print("\n=== Siguientes Pasos ===")
    print(f"1. Agrega los archivos de documentación a la rama {feature_branch}")
    print("2. Usa 'git add .' para preparar los cambios")
    print("3. Ejecuta este script nuevamente para confirmar y crear el PR")
    
    # 5. Si hay cambios para confirmar, hacer commit
    if check_git_status():
        print("\nSe detectaron cambios sin confirmar.")
        if input("¿Desea confirmar los cambios ahora? (s/n): ").lower() == 's':
            if commit_changes():
                # 6. Hacer push de los cambios
                if push_changes(feature_branch):
                    # 7. Crear PR a la rama documentation
                    if input(f"\n¿Desea crear un PR a la rama {DOC_BRANCH}? (s/n): ").lower() == 's':
                        create_pr(DOC_BRANCH, feature_branch)
    else:
        print("\nNo hay cambios para confirmar.")
    
    print("\n=== Flujo de Trabajo Completado ===")
    print("Recuerda que después de aprobar el PR a la rama documentation,")
    print(f"deberás crear otro PR de {DOC_BRANCH} a {DEVELOP_BRANCH}.")

if __name__ == "__main__":
    main()
