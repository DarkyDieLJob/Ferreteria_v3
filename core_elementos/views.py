from django.views.generic import TemplateView
from x_articulos.models import Articulo
from x_articulos.forms import ArticuloForm
from django.http import JsonResponse

# Create your views here.
class Crud(TemplateView):
    template_name = 'x_articulos/crud.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['titulo'] = 'R.U.'
        
        context['core_andamio_id'] = 1
        context['hay_navbar_html'] = True
        context['hay_contenedor_html'] = True
        context['hay_pie_html'] = False
        context['hay_modal_html'] = False

        datos = Articulo.objects.all()

        # Define los campos que deseas omitir
        campos_omitidos = ['ultimo_cambio', 'actualizado', 'id', ]

        # Preparar los datos para la plantilla
        datos_para_plantilla = []
        for dato in datos:
            dato_para_plantilla = {}
            for field in Articulo._meta.fields:
                # Solo agrega el campo si no está en la lista de campos omitidos
                if field.name not in campos_omitidos:
                    dato_para_plantilla[field.name] = getattr(dato, field.name)
            datos_para_plantilla.append(dato_para_plantilla)


        
        # Define lista_titulos
        lista_titulos = ['codigo', 'descripcion',]
        
        # Agrega lista_titulos al contexto
        context['lista_titulos'] = lista_titulos
        
        context['datos'] = datos_para_plantilla
        
        context['tabla_crud_html'] = 'core_elementos/core_tabla_crud.html'
        context['modal_html'] = 'core_elementos/core_modal.html'
        context['form'] = ArticuloForm()

        return context
    
    def post(self, request, *args, **kwargs):
        form = ArticuloForm(request.POST)
        if form.is_valid():
            # Obtén el objeto Articulo correspondiente
            articulo = Articulo.objects.get(codigo=form.cleaned_data['codigo'])

            # Itera sobre los campos del formulario
            for field in form.cleaned_data:
                # Actualiza el atributo correspondiente en el objeto Articulo
                setattr(articulo, field, form.cleaned_data[field])

            # Guarda el objeto Articulo actualizado
            articulo.save()

            # Crea el diccionario para la respuesta
            dic = {'status': 'ok'}
            for field in form.cleaned_data:
                dic[field] = form.cleaned_data[field]

            return JsonResponse(dic)
        else:
            return JsonResponse({'errors': form.errors}, status=400)

