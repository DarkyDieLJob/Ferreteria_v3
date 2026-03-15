from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import FormView
from django.urls import reverse_lazy
import mimetypes
import logging

from .forms import DailyReportForm
from .adapters_patoba import PatobaDriveAdapter
from .adapters_storage import DjangoStorageAdapter
from .excel_io import PandasExcelIO
from .usecases import RunDailyReport, ReportRequest
from .conf import (
    REPORTES_REQUIRE_STAFF,
    REPORTES_INPUT_FOLDER_ID,
    REPORTES_CONTROL_SHEET_ID,
    REPORTES_CONTROL_TAB,
)
from .conf import (
    REPORTES_INPUT_FOLDER_NAME,
    REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID,
)
from .models import ReportControlEntry

# Logger para la app 'reportes'
logger = logging.getLogger('reportes')


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return (self.request.user.is_authenticated and self.request.user.is_staff) if REPORTES_REQUIRE_STAFF else self.request.user.is_authenticated


class DailyReportView(LoginRequiredMixin, StaffRequiredMixin, FormView):
    template_name = 'reportes/diario.html'
    form_class = DailyReportForm
    success_url = reverse_lazy('reportes:diario')

    def form_valid(self, form):
        drive = PatobaDriveAdapter(self.request)
        storage = DjangoStorageAdapter()
        excel = PandasExcelIO()
        uc = RunDailyReport(drive, storage, excel)

        f = form.cleaned_data.get('file')
        file_bytes = f.read() if f else None

        # Build monthly base name: "{base_name} {M}-{Mes}[-YYYY]"
        base_name = (form.cleaned_data.get('base_name') or 'informe de ventas').strip()
        month_num = int(form.cleaned_data.get('month'))
        month_names = [
            '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        month_text = month_names[month_num]
        include_year = bool(form.cleaned_data.get('include_year'))
        year = form.cleaned_data.get('year')
        monthly_base = f"{base_name} {month_num}-{month_text}"
        if include_year and year:
            monthly_base = f"{monthly_base}-{year}"

        output_file_name = form.cleaned_data.get('output_file_name') or monthly_base

        drive_file_id = form.cleaned_data.get('drive_file_id') or None

        # Determine input folder id (prefer configured ID; else resolve by name under output root)
        input_folder_id = REPORTES_INPUT_FOLDER_ID
        if not input_folder_id and REPORTES_INPUT_FOLDER_NAME:
            # Try to resolve as a child under the default output root (Informes Ferretería)
            try:
                input_folder_id = drive.find_child_folder_by_name(
                    REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID,
                    REPORTES_INPUT_FOLDER_NAME,
                ) or input_folder_id
            except Exception as e:
                logger.warning(f"DailyReportView: no se pudo resolver carpeta de entrada por nombre: {e}")
        logger.debug(f"DailyReportView: input_folder_id={input_folder_id}")

        # Control-book DB flow: if selected and there's an upload, push it to INPUT folder first
        if form.cleaned_data.get('use_control_book') and f is not None and input_folder_id:
            upload_name = getattr(f, 'name', output_file_name)
            mime, _ = mimetypes.guess_type(upload_name)
            mime = mime or 'application/octet-stream'
            uploaded_id = drive.upload_or_update(
                file_name=upload_name,
                folder_id=input_folder_id,
                data=file_bytes,
                mime=mime,
            )
            drive_file_id = uploaded_id
            file_bytes = None  # force reading from Drive

            # Upsert control entry and mark allowed=True (auto-permitir nuevos)
            try:
                entry, _created = ReportControlEntry.objects.update_or_create(
                    drive_file_id=uploaded_id,
                    defaults={
                        'name': upload_name,
                        'mime_type': mime,
                        'folder_id': input_folder_id,
                        'allowed': True,
                        'year': year,
                        'month': month_num,
                    },
                )
            except Exception:
                pass

        # Batch: if using control and NO explicit input, sync folder and process allowed & unprocessed
        if form.cleaned_data.get('use_control_book') and not drive_file_id and not file_bytes and input_folder_id:
            batch_results = []
            try:
                # 1) Sync folder entries into DB
                items = drive.list_folder(input_folder_id, page_size=200)
                for it in items:
                    if it.get('mimeType') == 'application/vnd.google-apps.folder':
                        continue  # skip subfolders
                    ReportControlEntry.objects.update_or_create(
                        drive_file_id=it['id'],
                        defaults={
                            'name': it.get('name', ''),
                            'mime_type': it.get('mimeType', ''),
                            'folder_id': input_folder_id,
                            # nuevos: allowed=True según tu preferencia
                            'allowed': True,
                            'year': year,
                            'month': month_num,
                        },
                    )

                # 2) Process allowed & not processed
                qs = ReportControlEntry.objects.filter(
                    folder_id=input_folder_id, allowed=True, processed=False
                )
                for entry in qs[:50]:  # limite de seguridad
                    try:
                        req = ReportRequest(
                            file_bytes=None,
                            drive_file_id=entry.drive_file_id,
                            output_formats=form.cleaned_data.get('output_formats') or ['xlsx'],
                            output_file_name=output_file_name,
                            output_parent_folder_id=None,
                            output_subfolder_name=str(year) if year else None,
                        )
                        res = uc.execute(req)
                        ReportControlEntry.objects.filter(pk=entry.pk).update(processed=True)
                        batch_results.append({
                            'name': entry.name,
                            'media_urls': res.media_urls,
                            'drive_file_ids': res.drive_file_ids,
                        })
                    except Exception as e:
                        ReportControlEntry.objects.filter(pk=entry.pk).update(error_message=str(e))
                        batch_results.append({
                            'name': entry.name,
                            'error': str(e),
                        })
            except Exception as e:
                batch_results = [{'name': 'SYNC_ERROR', 'error': str(e)}]

            context = self.get_context_data()
            context.update({
                'batch_results': batch_results,
                'form': self.get_form_class()(),
            })
            return self.render_to_response(context)

        # Optional: verify control sheet allows processing; if control sheet configured
        if form.cleaned_data.get('use_control_book') and drive_file_id and REPORTES_CONTROL_SHEET_ID:
            try:
                values = drive.read_sheet_values(REPORTES_CONTROL_SHEET_ID, REPORTES_CONTROL_TAB)
                # Try to match by file name in first column; allow if second column is affirmative
                allowed = True
                if values:
                    # header optional; scan rows
                    target_name = None
                    if f is not None and hasattr(f, 'name'):
                        target_name = f.name
                    # If no upload name, cannot reliably check; default allow
                    if target_name:
                        allowed = False
                        for row in values:
                            if not row:
                                continue
                            name_cell = str(row[0]).strip() if len(row) >= 1 else ''
                            flag = str(row[1]).strip().lower() if len(row) >= 2 else ''
                            if name_cell == target_name and flag in {'si', 'sí', '1', 'true', 'permitir'}:
                                allowed = True
                                break
                if not allowed:
                    context = self.get_context_data()
                    context.update({
                        'form': self.get_form_class()(),
                        'media_urls': {},
                        'drive_file_ids': {},
                    })
                    return self.render_to_response(context)
            except Exception:
                # If control sheet read fails, proceed (fail-open) to match your flow
                pass

        req = ReportRequest(
            file_bytes=file_bytes,
            drive_file_id=drive_file_id,
            output_formats=form.cleaned_data.get('output_formats') or ['xlsx'],
            output_file_name=output_file_name,
            output_parent_folder_id=None,  # usa default de conf
            output_subfolder_name=str(year) if year else None,
        )
        resp = uc.execute(req)
        # Mark processed=True if entry exists
        try:
            if drive_file_id:
                ReportControlEntry.objects.filter(drive_file_id=drive_file_id).update(processed=True)
        except Exception:
            pass
        context = self.get_context_data()
        context.update({
            'media_urls': resp.media_urls,
            'drive_file_ids': resp.drive_file_ids,
            'form': self.get_form_class()(),
        })
        return self.render_to_response(context)
