"""
Core configuration package for Ferreteria_v3.

This module initializes the Django settings and loads any local overrides.
"""

# Import all settings from settings.py
from .settings import *

# Try to import local settings if they exist
try:
    from .local_settings import *  # noqa
    print("Local settings loaded successfully.")
except ImportError:
    print("No local settings found. Using production settings.")
    pass