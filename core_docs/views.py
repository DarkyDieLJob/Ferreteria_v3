# app_docs/views.py
from django.conf import settings
from django.views.static import serve
from django.http import Http404
from django.shortcuts import render
import logging
import markdown2
import emojis
import os

logger = logging.getLogger(__name__)

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
        Un objeto HttpResponse con el documento solicitado.

    Notas
    -----
    Los documentos HTML deben estar ubicados en 'core_docs/docs/_build/html' dentro del directorio BASE_DIR.
    Si el archivo solicitado no se encuentra, esta función redirigirá a 'index.html' como página predeterminada.
    """
    # Construir la ruta completa al archivo de documentación
    docs_dir = os.path.join(settings.BASE_DIR, 'core_docs/docs/_build/html')
    full_path = os.path.join(docs_dir, path)
    
    logger.debug(f"Buscando documento en: {full_path}")

    # Verificar si el archivo existe
    if not os.path.exists(full_path):
        logger.error(f"El archivo solicitado no existe: {full_path}")
        raise Http404(f"El archivo solicitado no existe: {full_path}")

    # Servir el archivo
    return serve(request, path, document_root=docs_dir)

def changeLog(request):
    dir_file = os.path.join(settings.BASE_DIR, 'CHANGELOG.md')
    with open(dir_file, 'r', encoding='utf-8') as f:
        markdown_text = f.read()
        html = markdown2.markdown(markdown_text)
        change_log = emojis.encode(html)
    return render(request, 'change_log.html', {'changelog': change_log})
