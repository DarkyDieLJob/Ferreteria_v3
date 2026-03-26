from django.urls import path
from .views import DailyReportView
from .views_batch import DriveBatchView
from .views_api import (
    AnnualSummaryAPI,
    MonthlySummaryAPI,
    WeeklySnapshotAPI,
    WeeklySnapshotCSV,
)

app_name = 'reportes'

urlpatterns = [
    path('reportes/diario/', DailyReportView.as_view(), name='diario'),
    path('reportes/drive-batch/', DriveBatchView.as_view(), name='drive_batch'),
    # API endpoints para dashboards
    path('reportes/api/annual/', AnnualSummaryAPI.as_view(), name='api_annual'),
    path('reportes/api/monthly/', MonthlySummaryAPI.as_view(), name='api_monthly'),
    path('reportes/api/weekly/', WeeklySnapshotAPI.as_view(), name='api_weekly'),
    path('reportes/api/weekly.csv', WeeklySnapshotCSV.as_view(), name='api_weekly_csv'),
]
