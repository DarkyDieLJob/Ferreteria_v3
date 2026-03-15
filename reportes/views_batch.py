from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
import logging

from .forms import DriveBatchForm
from .adapters_patoba import PatobaDriveAdapter
from .adapters_storage import DjangoStorageAdapter
from .excel_io import PandasExcelIO
from .usecases import RunDailyReport, ReportRequest
from .conf import (
    REPORTES_REQUIRE_STAFF,
    REPORTES_INPUT_FOLDER_ID,
    REPORTES_INPUT_FOLDER_NAME,
    REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID,
    REPORTES_MIN_YEAR,
)
from .models import ReportControlEntry

logger = logging.getLogger('reportes')


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (self.request.user.is_authenticated and self.request.user.is_staff) if REPORTES_REQUIRE_STAFF else self.request.user.is_authenticated


class DriveBatchView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    template_name = 'reportes/drive_batch.html'
    form_class = DriveBatchForm
    success_url = reverse_lazy('reportes:drive_batch')

    def get(self, request, *args, **kwargs):
        entries = ReportControlEntry.objects.all().order_by('-updated_at')
        # Best-effort resolver carpeta de entrada para mostrar link
        input_folder_id = REPORTES_INPUT_FOLDER_ID
        input_folder_url = None
        try:
            if input_folder_id:
                input_folder_url = f"https://drive.google.com/drive/folders/{input_folder_id}"
            elif REPORTES_INPUT_FOLDER_NAME:
                drive = PatobaDriveAdapter(self.request)
                fid = drive.find_child_folder_by_name(
                    REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID,
                    REPORTES_INPUT_FOLDER_NAME,
                )
                if fid:
                    input_folder_url = f"https://drive.google.com/drive/folders/{fid}"
        except Exception:
            pass
        context = self.get_context_data()
        context.update({'form': self.get_form(), 'entries': entries, 'batch_results': [], 'input_folder_url': input_folder_url})
        return self.render_to_response(context)

    def form_valid(self, form):
        logger.info('DriveBatchView: inicio')
        drive = PatobaDriveAdapter(self.request)
        storage = DjangoStorageAdapter()
        excel = PandasExcelIO()
        uc = RunDailyReport(drive, storage, excel)

        # Resolver carpeta de entrada
        input_folder_id = REPORTES_INPUT_FOLDER_ID
        if not input_folder_id and REPORTES_INPUT_FOLDER_NAME:
            try:
                input_folder_id = drive.find_child_folder_by_name(
                    REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID,
                    REPORTES_INPUT_FOLDER_NAME,
                ) or input_folder_id
            except Exception as e:
                logger.warning(f'DriveBatchView: no se pudo resolver carpeta de entrada por nombre: {e}')
        logger.debug(f'DriveBatchView: input_folder_id={input_folder_id}')
        input_folder_url = f"https://drive.google.com/drive/folders/{input_folder_id}" if input_folder_id else None

        action = form.cleaned_data.get('action') or 'sync'
        batch_results = []

        # Sincronizar listado desde Drive a DB
        if action == 'sync' and input_folder_id:
            try:
                # 1) Listar solo subcarpetas (años) dentro de la carpeta de entrada
                top = drive.list_folder(input_folder_id, page_size=500)
                year_folders = []
                for it in top:
                    if it.get('mimeType') == 'application/vnd.google-apps.folder':
                        name = (it.get('name') or '').strip()
                        try:
                            year_num = int(name)
                            # Aceptar solo años válidos (4 dígitos) y por encima del mínimo configurado
                            if 1000 <= year_num <= 9999 and year_num >= REPORTES_MIN_YEAR:
                                year_folders.append({'id': it['id'], 'name': name, 'year': year_num})
                        except ValueError:
                            continue
                # 1.b) Corregir entradas existentes bajo la raíz (no año): year=None
                corrected = ReportControlEntry.objects.filter(folder_id=input_folder_id).exclude(year__isnull=True).update(year=None)

                total_synced = 0
                for yf in year_folders:
                    files = drive.list_folder(yf['id'], page_size=500)
                    files = [f for f in files if f.get('mimeType') != 'application/vnd.google-apps.folder']
                    for f in files:
                        ReportControlEntry.objects.update_or_create(
                            drive_file_id=f['id'],
                            defaults={
                                'name': f.get('name', ''),
                                'mime_type': f.get('mimeType', ''),
                                'folder_id': yf['id'],
                                'allowed': True,
                                'year': yf['year'],
                            },
                        )
                        total_synced += 1
                logger.info(f"DriveBatchView: corregidos {corrected} registros bajo raiz (year=None). Sincronizados {total_synced} archivos desde subcarpetas de años: {[yf['year'] for yf in year_folders]}")
            except Exception as e:
                logger.exception(f'DriveBatchView: error al sincronizar: {e}')
                batch_results.append({'name': 'SYNC_ERROR', 'error': str(e)})

        # Procesar seleccionados
        if action == 'process':
            ids = self.request.POST.getlist('selected')
            logger.info(f'DriveBatchView: procesando seleccionados: {len(ids)}')
            qs = ReportControlEntry.objects.filter(pk__in=ids, allowed=True, processed=False)
            for entry in qs:
                try:
                    # Derivar nombre base desde entry.name sin extensión
                    name = entry.name or 'informe de ventas'
                    base = name.rsplit('.', 1)[0]
                    req = ReportRequest(
                        file_bytes=None,
                        drive_file_id=entry.drive_file_id,
                        output_formats=form.cleaned_data.get('output_formats') or ['xlsx'],
                        output_file_name=base,
                        output_parent_folder_id=None,
                        output_subfolder_name=str(entry.year) if getattr(entry, 'year', None) else None,
                    )
                    res = uc.execute(req)
                    ReportControlEntry.objects.filter(pk=entry.pk).update(processed=True)
                    batch_results.append({'name': entry.name, 'media_urls': res.media_urls, 'drive_file_ids': res.drive_file_ids})
                except Exception as e:
                    ReportControlEntry.objects.filter(pk=entry.pk).update(error_message=str(e))
                    batch_results.append({'name': entry.name, 'error': str(e)})

        # Renderizar tabla completa con resultados
        entries = ReportControlEntry.objects.all().order_by('-year', '-updated_at')
        context = self.get_context_data()
        context.update({'batch_results': batch_results, 'form': self.get_form_class()(), 'entries': entries, 'input_folder_url': input_folder_url})
        return self.render_to_response(context)
