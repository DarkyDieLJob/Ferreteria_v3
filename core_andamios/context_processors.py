from .models import Nav_Bar

def mi_procesador_de_contexto(request):
    
    contexto = {}
    contexto['barra_de_navegacion'] = Nav_Bar.objects.all()
    contexto['core_navbar_html'] = 'core_andamios/core_navbar.html'
    contexto['core_contenedor_html'] = 'core_andamios/core_contenedor.html'
    contexto['core_pie_html'] = 'core_andamios/core_pie.html'
    contexto['core_head_html'] = 'core_andamios/core_head.html'
    
    return contexto