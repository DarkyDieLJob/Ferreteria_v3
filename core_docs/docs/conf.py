# conf.py
import os
import sys
sys.path.insert(0, os.path.abspath('../../'))
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'core_config.settings'
django.setup()

# -- Project information -----------------------------------------------------
project = 'Ferreteria'
copyright = '2023, DarkyDielJob'
author = 'DarkyDielJob'
release = 'v2.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'myst_parser',  # Para soportar archivos .md
    # otras extensiones necesarias
]


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