from django.core.management.base import BaseCommand
import os
import subprocess
from django.conf import settings

class Command(BaseCommand):
    help = 'Reconstruye la documentación usando Sphinx'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Limpia la documentación antes de reconstruirla'
        )

    def handle(self, *args, **options):
        """
        Reconstruye la documentación usando Sphinx.
        """
        try:
            docs_dir = os.path.join(settings.BASE_DIR, 'core_docs/docs')
            os.chdir(docs_dir)
            
            if options['clean']:
                self.stdout.write('Limpiando la documentación...')
                subprocess.run(['make', 'clean'], check=True)
            
            self.stdout.write('Reconstruyendo la documentación...')
            subprocess.run(['make', 'html'], check=True)
            self.stdout.write(self.style.SUCCESS('Documentación reconstruida exitosamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al reconstruir la documentación: {e}'))
            raise
