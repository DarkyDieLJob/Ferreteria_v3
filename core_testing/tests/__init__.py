"""
Módulo de pruebas para core_testing.
"""

# This file makes Python treat the directory as a package.

# Configuración para pytest
def pytest_configure(config):
    """Configuración de pytest."""
    # Ignorar advertencias específicas
    import warnings
    warnings.filterwarnings(
        'ignore',
        message=r".*cannot collect test class '.*' because it has a __init__ constructor.*",
        category=pytest.PytestCollectionWarning
    )

# Excluir clases abstractas de la recolección de pruebas
collect_ignore = [
    'test_interfaces_base.py',  # Este archivo contiene pruebas para clases abstractas
]
