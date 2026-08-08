from django.core.management.base import BaseCommand
from actualizador.actualizador_main import _load_django_deps
from bdd.classes import Patoba
from django.conf import settings as const
from bdd.models import Listado_Planillas
from googleapiclient.errors import HttpError
import pandas as pd
import logging


def leer_nombres_hojas(buffer, mime_type, nombre_archivo):
    """Lee los nombres de las hojas de un archivo Excel.
    Usa xlrd2 para .xls viejos y openpyxl para .xlsx."""
    sheet_names = []
    es_xls = nombre_archivo.lower().endswith('.xls')

    if es_xls:
        try:
            import xlrd2
            wb = xlrd2.open_workbook(file_contents=buffer.read())
            sheet_names = wb.sheet_names()
            buffer.seek(0)
            return sheet_names
        except Exception as e1:
            buffer.seek(0)
            logger.error("xlrd2 fallo leyendo '%s': %s", nombre_archivo, e1)
            raise
    else:
        try:
            xls = pd.read_excel(buffer, sheet_name=None, engine='openpyxl')
            sheet_names = list(xls.keys())
        except Exception as e1:
            buffer.seek(0)
            logger.warning("openpyxl fallo leyendo '%s': %s. Intentando sin engine explicito.", nombre_archivo, e1)
            try:
                xls = pd.read_excel(buffer, sheet_name=None)
                sheet_names = list(xls.keys())
            except Exception as e2:
                logger.error("No se pudieron leer hojas de '%s': %s", nombre_archivo, e2)
                raise
    buffer.seek(0)
    return sheet_names

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Detecta planillas en Drive Inbox, lee sus hojas y las marca para etiquetar."

    def handle(self, *args, **options):
        _load_django_deps()
        self.stdout.write("Iniciando deteccion de planillas...")

        patoba = Patoba(None)
        drive_service = patoba.drive_service
        if not drive_service:
            self.stderr.write("ERROR: Servicio de Drive no inicializado.")
            return

        # Paso 2: Listar archivos de Drive y crear Listado_Planillas
        self.stdout.write("Listando archivos de Drive Inbox...")
        try:
            items_drive = patoba.listar(100, const.INBOX)
            created_count = 0
            for item_info in items_drive:
                item_name = item_info.get("name")
                item_id = item_info.get("id")
                if not item_name or not item_id:
                    continue
                try:
                    obj, created = Listado_Planillas.objects.update_or_create(
                        identificador=item_id, defaults={"descripcion": item_name}
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f"  CREADO: {item_name}")
                except Exception as e:
                    self.stderr.write(f"  Error creando {item_name}: {e}")
            self.stdout.write(f"Detectadas {created_count} planillas nuevas.")
        except Exception as e:
            self.stderr.write(f"Error listando Drive: {e}")
            return

        # Paso 3: Leer hojas de planillas pendientes
        self.stdout.write("Leyendo hojas de planillas pendientes...")
        datos_pendientes = Listado_Planillas.objects.filter(listo=False, descargar=False)
        for dato in datos_pendientes:
            try:
                from actualizador.actualizador_main import descargar_archivo_drive
                file_sheets, metadata = descargar_archivo_drive(
                    drive_service, dato.identificador
                )
                mime_type = metadata.get("mimeType", "")
                nombres = leer_nombres_hojas(file_sheets, mime_type, dato.descripcion)
                sheet_names = [""]
                sheet_names.extend(nombres)
                dato.hojas = ";".join(sheet_names)
                dato.save()
                self.stdout.write(f"  Hojas de '{dato.descripcion}': {dato.hojas}")
            except HttpError as http_e:
                if http_e.resp.status == 404:
                    self.stdout.write(f"  404: eliminando '{dato.descripcion}'")
                    dato.delete()
                else:
                    self.stderr.write(f"  Error HTTP en '{dato.descripcion}': {http_e}")
            except Exception as e:
                self.stderr.write(f"  Error leyendo hojas de '{dato.descripcion}': {e}")

        self.stdout.write(self.style.SUCCESS(
            f"Deteccion finalizada. {created_count} planillas listas para etiquetar."
        ))
