from django.core.management.base import BaseCommand
from actualizador.actualizador_main import procesar_planillas_listas


class Command(BaseCommand):
    help = "Fuerza el procesado de planillas etiquetadas como listas. No procesa emails ni detecta nuevas."

    def handle(self, *args, **options):
        self.stdout.write("Iniciando procesado de planillas...")
        procesar_planillas_listas()
        self.stdout.write(self.style.SUCCESS("Procesado finalizado."))
