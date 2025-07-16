from django.apps import AppConfig

class AppDocsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core_docs'

    def ready(self):
        """Conecta los signals cuando la app está lista."""
        from . import signals
        import bdd.models  # Importa los modelos para que estén disponibles
        signals.setup_signals()  # Configura los signals
