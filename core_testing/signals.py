"""
Signals for the core_testing application.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import TestRun, TestCase, TestCoverage

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=TestRun)
def test_run_pre_save(sender, instance, **kwargs):
    """
    Pre-save signal handler for TestRun model.
    """
    if not instance.name and not instance.pk:
        # Generate a default name for new test runs
        from django.utils import timezone
        instance.name = f"Test Run - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
    
    # Ensure status is valid
    if instance.status not in dict(TestRun.STATUS_CHOICES):
        instance.status = 'error'
        logger.warning(f"Invalid status for TestRun {instance.id}, setting to 'error'")

@receiver(post_save, sender=TestRun)
def test_run_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal handler for TestRun model.
    """
    if created:
        logger.info(f"New TestRun created: {instance}")
    
    # Update related models if needed
    if instance.status == 'completed' and hasattr(instance, 'coverage_data'):
        instance.coverage_data.refresh_from_db()

@receiver(post_save, sender=TestCase)
def test_case_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal handler for TestCase model.
    """
    if created:
        logger.debug(f"New TestCase saved: {instance}")
    
    # Update parent TestRun status if this test case failed
    if instance.status in ['failed', 'error']:
        test_run = instance.test_run
        if test_run.status != 'failed':  # Only update if not already failed
            test_run.status = 'failed'
            test_run.save(update_fields=['status', 'updated_at'])

@receiver(post_save, sender=TestCoverage)
def test_coverage_post_save(sender, instance, created, **kwargs):
    """
    Post-save signal handler for TestCoverage model.
    """
    if created:
        logger.info(f"New TestCoverage saved for TestRun {instance.test_run_id}")
    
    # Update the related TestRun with coverage percentage
    test_run = instance.test_run
    if test_run.coverage_percent != instance.percent_covered:
        test_run.coverage_percent = instance.percent_covered
        test_run.save(update_fields=['coverage_percent', 'updated_at'])
