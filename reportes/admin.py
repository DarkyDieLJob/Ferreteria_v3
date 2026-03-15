from django.contrib import admin
from .models import ReportControlEntry


@admin.register(ReportControlEntry)
class ReportControlEntryAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'drive_file_id', 'allowed', 'processed', 'year', 'month', 'updated_at'
    )
    list_filter = ('allowed', 'processed', 'year', 'month')
    search_fields = ('name', 'drive_file_id', 'folder_id')
