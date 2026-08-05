from django.core.management.base import BaseCommand
from actualizador.actualizador_main import principal


class Command(BaseCommand):
    help = "Fuerza el procesado de planillas etiquetadas como listas."

    def handle(self, *args, **options):
        self.stdout.write("Iniciando procesado de planillas...")
        principal()
        self.stdout.write(self.style.SUCCESS("Procesado finalizado."))
