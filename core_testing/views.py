"""
Vistas para el módulo de testing.
Proporciona las vistas necesarias para el dashboard de pruebas.
"""
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q, Min, Max
from django.utils import timezone

from .models import TestRun, TestCase, ModuleCoverage





class TestRunDetailView(LoginRequiredMixin, View):
    """Vista para mostrar los detalles de una ejecución de pruebas."""
    template_name = 'core_testing/testrun_detail.html'
    
    def get(self, request: HttpRequest, run_id: int) -> HttpResponse:
        """Muestra los detalles de una ejecución de pruebas.
        
        Args:
            request: Objeto HttpRequest
            run_id: ID de la ejecución de pruebas
            
        Returns:
            HttpResponse con los detalles de la ejecución
        """
        test_run = get_object_or_404(TestRun, id=run_id)
        test_cases = test_run.test_cases.all()
        
        # Estadísticas de los casos de prueba
        test_stats = test_cases.aggregate(
            total=Count('id'),
            passed=Count('id', filter=Q(status='passed')),
            failed=Count('id', filter=Q(status='failed')),
            error=Count('id', filter=Q(status='error')),
            skipped=Count('id', filter=Q(status='skipped')),
        )
        
        # Agrupar por estado para el gráfico
        status_counts = {
            'passed': test_stats['passed'],
            'failed': test_stats['failed'],
            'error': test_stats['error'],
            'skipped': test_stats['skipped'],
        }
        
        context = {
            'test_run': test_run,
            'test_cases': test_cases,
            'test_stats': test_stats,
            'status_counts': status_counts,
        }
        return render(request, self.template_name, context)


class TestingDashboardView(LoginRequiredMixin, View):
    """Vista principal del dashboard de testing."""
    template_name = 'core_testing/dashboard.html'
    
    def get(self, request: HttpRequest):
        """
        Muestra el dashboard con el estado actual de las pruebas.
        """
        # Obtener estadísticas de pruebas
        test_runs = TestRun.objects.all().order_by('-started_at')
        last_run = test_runs.first()
        
        # Calcular estadísticas generales
        total_runs = test_runs.count()
        passed_runs = TestRun.objects.filter(status='passed').count()
        failed_runs = TestRun.objects.filter(status='failed').count()
        
        stats = {
            'total_runs': total_runs,
            'passed_runs': passed_runs,
            'failed_runs': failed_runs,
            'last_run': last_run,
            'success_rate': (passed_runs / total_runs * 100) if total_runs > 0 else 0,
            'avg_duration': TestRun.objects.aggregate(avg=Avg('duration'))['avg'] or 0,
        }
        
        # Obtener estadísticas de cobertura
        coverage_stats = ModuleCoverage.objects.aggregate(
            avg=Avg('coverage_percent'),
            total=Count('id'),
            covered=Count('id', filter=Q(coverage_percent__gte=80)),
        )
        
        # Obtener módulos con mejor/peor cobertura
        best_coverage = ModuleCoverage.objects.order_by('-coverage_percent')[:5]
        worst_coverage = ModuleCoverage.objects.filter(
            coverage_percent__lt=80
        ).order_by('coverage_percent')[:5]
        
        context = {
            'test_stats': stats,
            'coverage_stats': {
                'avg': coverage_stats['avg'] or 0,
                'total': coverage_stats['total'] or 0,
                'covered': coverage_stats['covered'] or 0,
            },
            'latest_runs': test_runs[:5],
            'best_coverage': best_coverage,
            'worst_coverage': worst_coverage,
            'page_title': 'Dashboard de Pruebas',
        }
        
        return render(request, self.template_name, context)


class CoverageReportView(LoginRequiredMixin, View):
    """Vista para mostrar informes de cobertura de pruebas."""
    template_name = 'core_testing/coverage_report.html'
    
    def get(self, request: HttpRequest) -> HttpResponse:
        """Muestra un informe de cobertura de pruebas."""
        # Obtener estadísticas generales
        coverage_stats = ModuleCoverage.objects.aggregate(
            avg=Avg('coverage_percent'),
            min=Min('coverage_percent'),
            max=Max('coverage_percent'),
            total=Count('id'),
            covered=Count('id', filter=Q(coverage_percent__gte=80)),
        )
        
        # Obtener tendencia de cobertura (últimos 7 días)
        trend_data = ModuleCoverage.objects.filter(
            last_updated__gte=timezone.now() - timezone.timedelta(days=7)
        ).values('last_updated__date').annotate(
            avg_coverage=Avg('coverage_percent')
        ).order_by('last_updated__date')
        
        # Obtener módulos con mejor y peor cobertura
        best_coverage = ModuleCoverage.objects.order_by('-coverage_percent')[:10]
        worst_coverage = ModuleCoverage.objects.order_by('coverage_percent')[:10]
        
        context = {
            'coverage_stats': coverage_stats,
            'best_coverage': best_coverage,
            'worst_coverage': worst_coverage,
            'trend_data': list(trend_data),
        }
        
        return render(request, self.template_name, context)
