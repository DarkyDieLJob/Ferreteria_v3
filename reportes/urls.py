from django.urls import path
from .views import DailyReportView
from .views_batch import DriveBatchView

app_name = 'reportes'

urlpatterns = [
    path('reportes/diario/', DailyReportView.as_view(), name='diario'),
    path('reportes/drive-batch/', DriveBatchView.as_view(), name='drive_batch'),
]
