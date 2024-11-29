from core_andamios.views import ContextoAndamio

# Create your views here.

class Vista_Index(ContextoAndamio):
    template_name = 'core_index/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        
        context['contenido_1'] = 'core_elementos/core_formulario.html'
        context['elemento_parrafo'] = 'core_elementos/core_parrafo.html'
        context['parrafo'] = 'Un parrafo'
        context['components'] = 'core_elementos/components.html'
        context['World'] = "Nombre"
        
        
        return context
    
    