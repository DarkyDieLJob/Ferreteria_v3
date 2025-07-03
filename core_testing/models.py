"""
Models for the core_testing application.
"""
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class TestRun(models.Model):
    """Represents a single test run execution."""
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ]

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Test Run Information
    name = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='running'
    )
    duration = models.FloatField(
        help_text="Duration in seconds", 
        null=True, 
        blank=True
    )
    
    # Test Results
    total_tests = models.PositiveIntegerField(default=0)
    tests_passed = models.PositiveIntegerField(default=0)
    tests_failed = models.PositiveIntegerField(default=0)
    tests_skipped = models.PositiveIntegerField(default=0)
    tests_error = models.PositiveIntegerField(default=0)
    
    # Coverage Information
    coverage_percent = models.FloatField(
        null=True, 
        blank=True,
        help_text="Code coverage percentage"
    )
    
    # Version Control
    branch = models.CharField(max_length=100, blank=True)
    commit_hash = models.CharField(max_length=40, blank=True)
    
    # Relationships
    triggered_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_runs'
    )
    
    # Additional Data
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Test Run'
        verbose_name_plural = 'Test Runs'
    
    def __str__(self):
        return f"Test Run {self.id} - {self.get_status_display()} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def is_completed(self):
        """Check if the test run has completed."""
        return self.status in ['passed', 'failed', 'error']
    
    def update_from_pytest_json(self, json_data):
        """Update test run data from pytest-json report."""
        if not isinstance(json_data, dict):
            json_data = json.loads(json_data)
        
        # Update basic test results
        self.total_tests = json_data.get('summary', {}).get('total', 0)
        self.tests_passed = json_data.get('summary', {}).get('passed', 0)
        self.tests_failed = json_data.get('summary', {}).get('failed', 0)
        self.tests_skipped = json_data.get('summary', {}).get('skipped', 0)
        self.tests_error = json_data.get('summary', {}).get('error', 0)
        
        # Update status based on results
        if self.tests_failed > 0 or self.tests_error > 0:
            self.status = 'failed'
        else:
            self.status = 'passed'
        
        # Update duration if available
        duration = json_data.get('duration', 0)
        if duration:
            self.duration = duration
        
        self.save()
        return self


class TestCase(models.Model):
    """Represents an individual test case execution."""
    TEST_STATUS = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error'),
        ('skipped', 'Skipped'),
        ('xfailed', 'Expected Failure'),
        ('xpassed', 'Unexpected Pass'),
    ]
    
    # Relationships
    test_run = models.ForeignKey(
        TestRun,
        on_delete=models.CASCADE,
        related_name='test_cases'
    )
    
    # Test Information
    nodeid = models.CharField(max_length=1024)
    name = models.CharField(max_length=255)
    file = models.CharField(max_length=512)
    line = models.PositiveIntegerField()
    
    # Test Results
    status = models.CharField(max_length=10, choices=TEST_STATUS)
    duration = models.FloatField(help_text="Duration in seconds")
    
    # Error Details (if any)
    message = models.TextField(blank=True)
    traceback = models.TextField(blank=True)
    
    # Additional Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-test_run', 'file', 'name']
        verbose_name = 'Test Case'
        verbose_name_plural = 'Test Cases'
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class TestCoverage(models.Model):
    """Stores code coverage information for test runs."""
    test_run = models.OneToOneField(
        TestRun,
        on_delete=models.CASCADE,
        related_name='coverage_data'
    )
    
    # Coverage Summary
    total_statements = models.PositiveIntegerField()
    total_missing = models.PositiveIntegerField()
    percent_covered = models.FloatField()
    
    # Detailed Coverage Data
    file_coverage = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Test Coverage'
        verbose_name_plural = 'Test Coverages'
    
    def __str__(self):
        return f"Coverage for Test Run {self.test_run_id}: {self.percent_covered}%"
    
    def update_from_coverage_data(self, coverage_data):
        """Update coverage data from coverage.py JSON report."""
        if not isinstance(coverage_data, dict):
            coverage_data = json.loads(coverage_data)
        
        totals = coverage_data.get('totals', {})
        
        self.total_statements = totals.get('num_statements', 0)
        self.total_missing = totals.get('missing_lines', 0)
        self.percent_covered = totals.get('percent_covered', 0.0)
        
        # Store file-level coverage data
        self.file_coverage = {
            file_path: {
                'summary': {
                    'percent_covered': data['summary']['percent_covered'],
                    'missing_lines': data['summary']['missing_lines'],
                    'num_statements': data['summary']['num_statements'],
                },
                'executed_lines': data.get('executed_lines', []),
                'missing_lines': data.get('missing_lines', []),
                'excluded_lines': data.get('excluded_lines', []),
            }
            for file_path, data in coverage_data.get('files', {}).items()
        }
        
        self.save()
        return self
