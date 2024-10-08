# app_docs/urls.py
from django.urls import re_path, path
from .views import serve_docs, changeLog

urlpatterns = [
    re_path(r'^docs/(?P<path>.*)$', serve_docs),
    path('change_log/', changeLog, name='change-log'),

]
