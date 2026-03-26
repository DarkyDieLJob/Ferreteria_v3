from django.contrib import admin
from django.contrib import messages
from datetime import date
from django.urls import path
from django.shortcuts import redirect

from .models import ReportControlEntry, WeeklySalesSnapshot
from .usecases_db import get_last_completed_week, generate_weekly_snapshot, get_week_bounds_for


@admin.register(ReportControlEntry)
class ReportControlEntryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'drive_file_id', 'allowed', 'processed', 'year', 'month', 'updated_at'
    )
    list_filter = ('allowed', 'processed', 'year', 'month')
    search_fields = ('name', 'drive_file_id', 'folder_id')


@admin.register(WeeklySalesSnapshot)
class WeeklySalesSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'week_start', 'week_end', 'proveedor', 'item', 'is_sin_registro', 'cantidad_vendida', 'updated_at'
    )
    list_filter = ('week_start', 'proveedor', 'is_sin_registro')
    search_fields = ('item__descripcion', 'proveedor__text_display')

    change_list_template = 'admin/reportes/weeklysalessnapshot/change_list.html'

    actions = [
        'accion_generar_semana_cerrada',
        'accion_regenerar_semana_cerrada',
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('generate_week/', self.admin_site.admin_view(self.view_generate_week), name='reportes_weekly_generate_week'),
            path('regenerate_week/', self.admin_site.admin_view(self.view_regenerate_week), name='reportes_weekly_regenerate_week'),
            path('download_csv/', self.admin_site.admin_view(self.view_download_csv_latest), name='reportes_weekly_download_csv'),
        ]
        return custom + urls

    def view_generate_week(self, request):
        # Permitir forzar semana via ?week_start=YYYY-MM-DD
        ws_param = request.GET.get('week_start')
        if ws_param:
            try:
                ws = date.fromisoformat(ws_param)
                week_start, week_end = get_week_bounds_for(ws)
            except ValueError:
                week_start, week_end = get_last_completed_week(date.today())
        else:
            week_start, week_end = get_last_completed_week(date.today())
        created = generate_weekly_snapshot(week_start, week_end)
        self.message_user(
            request,
            f"Generado snapshot semanal {week_start}..{week_end}. Filas creadas: {created}",
            level=messages.SUCCESS,
        )
        return redirect('admin:reportes_weeklysalessnapshot_changelist')

    def view_regenerate_week(self, request):
        ws_param = request.GET.get('week_start')
        if ws_param:
            try:
                ws = date.fromisoformat(ws_param)
                week_start, week_end = get_week_bounds_for(ws)
            except ValueError:
                week_start, week_end = get_last_completed_week(date.today())
        else:
            week_start, week_end = get_last_completed_week(date.today())
        created = generate_weekly_snapshot(week_start, week_end)
        self.message_user(
            request,
            f"Regenerado snapshot semanal {week_start}..{week_end}. Filas: {created}",
            level=messages.SUCCESS,
        )
        return redirect('admin:reportes_weeklysalessnapshot_changelist')

    def view_download_csv_latest(self, request):
        latest = WeeklySalesSnapshot.objects.order_by('-week_end', '-updated_at').first()
        if not latest:
            self.message_user(request, 'No hay snapshots semanales para descargar.', level=messages.WARNING)
            return redirect('admin:reportes_weeklysalessnapshot_changelist')
        # Redirigir al endpoint CSV con el week_start del último snapshot
        return redirect(f"/reportes/api/weekly.csv?week_start={latest.week_start.isoformat()}")

    def accion_generar_semana_cerrada(self, request, queryset):
        week_start, week_end = get_last_completed_week(date.today())
        created = generate_weekly_snapshot(week_start, week_end)
        self.message_user(
            request,
            f"Generado snapshot semanal {week_start}..{week_end}. Filas creadas: {created}",
            level=messages.SUCCESS,
        )
    accion_generar_semana_cerrada.short_description = "Generar snapshot de la última semana cerrada (L–S)"

    def accion_regenerar_semana_cerrada(self, request, queryset):
        week_start, week_end = get_last_completed_week(date.today())
        created = generate_weekly_snapshot(week_start, week_end)
        self.message_user(
            request,
            f"Regenerado snapshot semanal {week_start}..{week_end}. Filas: {created}",
            level=messages.SUCCESS,
        )
    accion_regenerar_semana_cerrada.short_description = "Regenerar snapshot de la última semana cerrada (borra y vuelve a crear)"
