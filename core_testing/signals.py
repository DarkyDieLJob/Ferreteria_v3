"""
Signals para la aplicación core_testing.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import TestRun, TestCase, ModuleCoverage

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=TestRun)
def test_run_pre_save(sender, instance, **kwargs):
    """
    Señal pre-save para el modelo TestRun.
    Genera un nombre por defecto para nuevas ejecuciones de prueba.
    """
    if not instance.name and not instance.pk:
        from django.utils import timezone
        instance.name = f"Ejecución de Pruebas - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Ensure status is valid
    valid_statuses = dict(TestRun.Status.choices)
    if instance.status not in valid_statuses:
        instance.status = 'error'
        logger.warning(f"Invalid status '{instance.status}' for TestRun {instance.id if instance.id else 'new'}, setting to 'error'")

@receiver(post_save, sender=TestRun)
def test_run_post_save(sender, instance, created, **kwargs):
    """
    Señal post-save para el modelo TestRun.
    Registra la creación o actualización de una ejecución de pruebas.
    """
    if created:
        logger.info(f"Nueva ejecución de pruebas creada: {instance.id} - {instance.name}")
    else:
        logger.debug(f"Ejecución de pruebas actualizada: {instance.id} - {instance.status}")
    if instance.status == 'completed' and hasattr(instance, 'coverage_data'):
        instance.coverage_data.refresh_from_db()

@receiver(post_save, sender=TestCase)
def test_case_post_save(sender, instance, created, **kwargs):
    """
    Señal post-save para el modelo TestCase.
    Actualiza las estadísticas de TestRun cuando se guarda un caso de prueba.
    """
    test_run = instance.test_run
    if test_run:
        # Actualizar estadísticas de la ejecución
        test_run.total_tests = test_run.test_cases.count()
        test_run.tests_passed = test_run.test_cases.filter(status='passed').count()
        test_run.tests_failed = test_run.test_cases.filter(status='failed').count()
        test_run.tests_error = test_run.test_cases.filter(status='error').count()
        test_run.tests_skipped = test_run.test_cases.filter(status='skipped').count()
        
        # Calcular duración total
        from django.db.models import Sum
        total_duration = test_run.test_cases.aggregate(
            total=Sum('duration')
        )['total'] or 0
        test_run.duration = total_duration
        
        # Actualizar estado general
        if test_run.tests_failed > 0 or test_run.tests_error > 0:
            test_run.status = TestRun.Status.FAILED
        elif test_run.tests_skipped == test_run.total_tests and test_run.total_tests > 0:
            test_run.status = TestRun.Status.SKIPPED
        elif test_run.tests_passed == test_run.total_tests and test_run.total_tests > 0:
            test_run.status = TestRun.Status.PASSED
            
        test_run.save(update_fields=['status', 'updated_at'])

@receiver(post_save, sender=ModuleCoverage)
def module_coverage_post_save(sender, instance, created, **kwargs):
    """
    Señal post-save para el modelo ModuleCoverage.
    Actualiza la cobertura en TestRun cuando se guarda un registro de cobertura.
    """
    if instance.test_run:
        # Actualizar la cobertura en TestRun si este módulo tiene una ejecución asociada
        test_run = instance.test_run
        
        # Calcular el promedio de cobertura para todos los módulos de esta ejecución
        from django.db.models import Avg
        avg_coverage = ModuleCoverage.objects.filter(
            test_run=test_run
        ).aggregate(
            avg_coverage=Avg('coverage_percent')
        )['avg_coverage'] or 0
        
        test_run.coverage_percent = avg_coverage
        test_run.save()
        
        logger.info(f"Cobertura actualizada para ejecución {test_run.id}: {avg_coverage:.2f}%")
