from django.views.generic import TemplateView
from .models import Nav_Bar, Url, Contenedor, Script, Pie

class ContextoAndamio(TemplateView):
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['titulo'] = 'Index'
        context['core_andamio_id'] = 1
        context['hay_navbar_html'] = True
        context['hay_contenedor_html'] = True
        context['hay_pie_html'] = True
        
        return context
        
        #---------------------------------------------------
        # Seteo basico desde el armador, futuro andamio
        
        #---------------------------------------------------
        # Formularios desde armador, futuro andamios
        
        #--------------------------------------------------------------------------------------
        # Planillas de descargas para etiquetar Actualizador

