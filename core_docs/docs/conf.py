# conf.py
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, os.path.abspath('../../'))
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'
django.setup()

# -- Project information -----------------------------------------------------
project = 'Ferreteria'
copyright = '2023, DarkyDielJob'
author = 'DarkyDielJob'

# Obtener versión dinámica desde package.json
def get_version():
    try:
        package_path = Path('../../package.json').resolve()
        with open(package_path, 'r') as f:
            data = json.load(f)
            return data.get('version', 'N/A')
    except Exception as e:
        print(f"Error al obtener versión: {e}")
        return 'N/A'

release = get_version()

# -- General configuration ---------------------------------------------------

# Configuración de MyST
extensions = [
    'myst_parser',
    'sphinx.ext.autodoc'
]
myst_enable_extensions = [
    "dollarmath",
    "amsmath",
    "deflist",
    "html_admonition",
    "html_image",
    "colon_fence",
    "smartquotes",
    "replacements",
    #"linkify",
    "substitution",
]

# Si tu archivo index es .md
master_doc = 'index'

# Otras configuraciones de Sphinx...
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

source_suffix = ['.rst', '.md']

language = 'es'

# -- Options for HTML output -------------------------------------------------
html_theme = 'furo'
html_static_path = ['_static']

# Configuración adicional para el tema furo
html_theme_options = {
    'sidebar_hide_name': True,
    'navigation_with_keys': True,
    'top_of_page_button': 'edit',
    'source_repository': 'https://github.com/DarkyDieLJob/Ferreteria_v3/',
    'source_branch': 'main',
    'source_directory': 'core_docs/docs/',
    'announcement': f'Versión actual: {release}',
    'light_logo': 'logo.png',
    'dark_logo': 'logo.png',
}

# Configuración para mostrar la versión en la barra lateral
html_context = {
    'github_user': 'DarkyDieLJob',
    'github_repo': 'Ferreteria_v3',
    'github_version': 'main',
    'conf_py_path': '/core_docs/docs/',
    'source_suffix': '.md',
    'version': release
}