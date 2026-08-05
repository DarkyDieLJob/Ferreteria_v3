from django.core.management.base import BaseCommand
from bdd.classes import Patoba
from bdd.funtions import get_emails


class Command(BaseCommand):
    help = "Procesa emails de Gmail y sube attachments Excel a Drive Inbox."

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=1,
            help="Cantidad de dias hacia atras para buscar emails (default: 1)",
        )

    def handle(self, *args, **options):
        days = options["days"]
        self.stdout.write(f"Procesando emails de los ultimos {days} dia(s)...")

        patoba = Patoba(None)
        gmail_service = patoba.gmail_service
        drive_service = patoba.drive_service

        if not drive_service:
            self.stderr.write("ERROR: Servicio de Google Drive no inicializado.")
            return
        if not gmail_service:
            self.stderr.write("ERROR: Servicio de Gmail no inicializado.")
            return

        get_emails(gmail_service, drive_service, days_back=days)
        self.stdout.write(self.style.SUCCESS("Procesamiento de emails finalizado."))
