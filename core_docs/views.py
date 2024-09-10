# app_docs/views.py
from django.conf import settings
from django.views.static import serve
from django.http import Http404
from django.shortcuts import render


def serve_docs(request, path):
    """
    Esta función sirve documentos HTML generados por Sphinx.

    Parámetros
    ----------
    request : HttpRequest
        Una instancia de HttpRequest.
    path : str
        La ruta del documento solicitado.

    Devoluciones
    ------------
    HttpResponse
        Una instancia de HttpResponse que contiene el documento solicitado.

    Notas
    -----
    Los documentos HTML deben estar ubicados en 'core_docs/docs/_build/html' dentro del directorio BASE_DIR.
    Si el archivo solicitado no se encuentra, esta función redirigirá a 'index.html' como página predeterminada.
    """
    document_root = settings.BASE_DIR / 'core_docs/docs/_build/html'
    try:
        return serve(request, path, document_root=document_root)
    except Http404:
        # Si el archivo no se encuentra, puedes redirigir a 'index.html' como página predeterminada
        return serve(request, 'index.html', document_root=document_root)

import markdown2

def changeLog(request):
    with open('CHANGELOG.md', 'r', encoding='utf-8') as f:
        markdown_text = f.read()
        html = markdown2.markdown(markdown_text)
    return render(request, 'change_log.html', {'changelog': html})
