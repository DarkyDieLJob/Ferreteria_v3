from django.views import generic
from .models import Log


class ListLogs(generic.ListView):
    template_name = "loguer/short_log_list.html"
    context_object_name = "ni_idea"

    def get_queryset(self):
        ''' Retorna los 20 ultimos logs'''
        return Log.objects.all().order_by("-fecha")[:20]

