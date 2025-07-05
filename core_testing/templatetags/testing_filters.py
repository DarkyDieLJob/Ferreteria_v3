"""
Filtros personalizados para las plantillas del módulo de testing.
"""
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import floatformat
from django.template.defaulttags import register
import os

register = template.Library()

@register.filter(name='percentage')
def percentage(value, total):
    """
    Calcula el porcentaje de un valor respecto a un total.
    
    Args:
        value: El valor a calcular
        total: El valor total (100%)
        
    Returns:
        float: El porcentaje calculado, o 0 si el total es 0
    """
    try:
        if total == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.filter(name='get_status_bg_class')
def get_status_bg_class(status):
    """
    Devuelve la clase de color de fondo según el estado de la prueba.
    """
    status_classes = {
        'passed': 'success',
        'failed': 'danger',
        'error': 'danger',
        'skipped': 'warning',
        'running': 'info',
        'pending': 'secondary',
    }
    return status_classes.get(status.lower(), 'secondary')

@register.filter(name='get_status_icon')
def get_status_icon(status):
    """
    Devuelve el ícono correspondiente al estado de la prueba.
    """
    status_icons = {
        'passed': 'check-circle',
        'failed': 'times-circle',
        'error': 'exclamation-circle',
        'skipped': 'forward',
        'running': 'spinner fa-spin',
        'pending': 'clock',
    }
    return status_icons.get(status.lower(), 'question-circle')

@register.filter(name='coverage_badge_class')
def coverage_badge_class(coverage_percent):
    """
    Devuelve la clase de color para la insignia de cobertura según el porcentaje.
    """
    if coverage_percent is None:
        return 'secondary'
    
    coverage_percent = float(coverage_percent)
    if coverage_percent >= 80:
        return 'success'
    elif coverage_percent >= 50:
        return 'warning'
    else:
        return 'danger'

@register.filter(name='format_duration')
def format_duration(seconds):
    """
    Formatea la duración en segundos a un formato legible.
    """
    if seconds is None:
        return "N/A"
    
    try:
        seconds = float(seconds)
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.0f}s"
    except (TypeError, ValueError):
        return str(seconds)

@register.filter(name='test_result_summary')
def test_result_summary(test_run):
    """
    Genera un resumen de los resultados de las pruebas.
    """
    parts = []
    if test_run.tests_passed:
        parts.append(f"{test_run.tests_passed} ✓")
    if test_run.tests_failed:
        parts.append(f"{test_run.tests_failed} ✗")
    if test_run.tests_error:
        parts.append(f"{test_run.tests_error} ⚠")
    if test_run.tests_skipped:
        parts.append(f"{test_run.tests_skipped} ➤")
    
    return " ".join(parts)

@register.filter(name='test_result_progress')
def test_result_progress(test_run):
    """
    Genera una barra de progreso para los resultados de las pruebas.
    """
    total = test_run.total_tests or 1
    passed_width = (test_run.tests_passed / total) * 100 if test_run.tests_passed else 0
    failed_width = (test_run.tests_failed / total) * 100 if test_run.tests_failed else 0
    error_width = (test_run.tests_error / total) * 100 if test_run.tests_error else 0
    skipped_width = (test_run.tests_skipped / total) * 100 if test_run.tests_skipped else 0
    
    html = f"""
    <div class="progress" style="height: 20px;">
        <div class="progress-bar bg-success" role="progressbar" 
             style="width: {passed_width}%" 
             title="{passed} pruebas pasadas">
        </div>
        <div class="progress-bar bg-danger" role="progressbar" 
             style="width: {failed_width}%" 
             title="{failed} pruebas fallidas">
        </div>
        <div class="progress-bar bg-warning" role="progressbar" 
             style="width: {error_width}%" 
             title="{error} pruebas con error">
        </div>
        <div class="progress-bar bg-secondary" role="progressbar" 
             style="width: {skipped_width}%" 
             title="{skipped} pruebas omitidas">
        </div>
    </div>
    """.format(
        passed_width=passed_width,
        failed_width=failed_width,
        error_width=error_width,
        skipped_width=skipped_width,
        passed=test_run.tests_passed or 0,
        failed=test_run.tests_failed or 0,
        error=test_run.tests_error or 0,
        skipped=test_run.tests_skipped or 0,
    )
    
    return mark_safe(html)

@register.filter(name='coverage_progress')
def coverage_progress(coverage_percent, size='normal'):
    """
    Genera una barra de progreso para la cobertura de código.
    """
    if coverage_percent is None:
        return "N/A"
        
    height = "20px" if size == 'normal' else "10px"
    badge_class = coverage_badge_class(coverage_percent)
    
    html = f"""
    <div class="progress" style="height: {height};">
        <div class="progress-bar bg-{badge_class}" role="progressbar" 
             style="width: {coverage_percent}%" 
             aria-valuenow="{coverage_percent}" 
             aria-valuemin="0" 
             aria-valuemax="100">
             {coverage_percent:.1f}%
        </div>
    </div>
    """.format(
        height=height,
        badge_class=badge_class,
        coverage_percent=float(coverage_percent)
    )
    
    return mark_safe(html)

@register.filter(name='test_trend_icon')
def test_trend_icon(trend_value):
    """
    Devuelve un ícono que representa la tendencia del rendimiento de las pruebas.
    """
    if trend_value > 0:
        return mark_safe('<i class="fas fa-arrow-up text-success"></i>')
    elif trend_value < 0:
        return mark_safe('<i class="fas fa-arrow-down text-danger"></i>')
    else:
        return mark_safe('<i class="fas fa-minus text-muted"></i>')

@register.filter(name='format_coverage_trend')
def format_coverage_trend(trend_value):
    """
    Formatea el valor de tendencia de cobertura.
    """
    if trend_value is None:
        return "N/A"
    
    trend_value = float(trend_value)
    if trend_value > 0:
        return f"+{trend_value:.1f}%"
    elif trend_value < 0:
        return f"{trend_value:.1f}%"
    else:
        return "0.0%"

@register.filter(name='test_status_count')
def test_status_count(test_runs, status):
    """
    Cuenta el número de ejecuciones con un estado específico.
    """
    return test_runs.filter(status=status).count()

@register.filter(name='test_status_percent')
def test_status_percent(test_runs, status):
    """
    Calcula el porcentaje de ejecuciones con un estado específico.
    """
    total = len(test_runs)
    if total == 0:
        return 0
    count = sum(1 for run in test_runs if run.status.lower() == status.lower())
    return (count / total) * 100

@register.filter(name='test_status_bg_color')
def test_status_bg_color(status):
    """
    Devuelve la clase de color de fondo para un estado de prueba.
    """
    status_colors = {
        'passed': 'success',
        'failed': 'danger',
        'error': 'danger',
        'skipped': 'warning',
        'running': 'info',
        'pending': 'secondary',
    }
    return status_colors.get(status.lower(), 'secondary')

@register.filter(name='coverage_color')
def coverage_color(coverage_percent):
    """
    Devuelve la clase de color para la cobertura según el porcentaje.
    """
    try:
        if coverage_percent is None or coverage_percent == '':
            return 'secondary'
        
        coverage_percent = float(coverage_percent)
        if coverage_percent >= 80:
            return 'success'
        elif coverage_percent >= 50:
            return 'warning'
        else:
            return 'danger'
    except (ValueError, TypeError):
        return 'secondary'

@register.filter(name='status_color')
def status_color(status):
    """
    Devuelve la clase de color de Bootstrap para un estado de prueba.
    
    Args:
        status (str): Estado de la prueba (passed, failed, error, skipped, running, pending)
        
    Returns:
        str: Clase de color de Bootstrap (success, danger, warning, info, secondary)
    """
    status = str(status).lower()
    color_map = {
        'passed': 'success',
        'failed': 'danger',
        'error': 'danger',
        'skipped': 'warning',
        'running': 'info',
        'pending': 'secondary',
    }
    return color_map.get(status, 'secondary')

@register.filter(name='basename')
def basename(filepath):
    """
    Extrae el nombre base de una ruta de archivo.
    
    Args:
        filepath (str): Ruta completa del archivo
        
    Returns:
        str: Nombre del archivo con su extensión
    """
    return os.path.basename(filepath) if filepath else ''
