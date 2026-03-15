from django.db import models


class ReportControlEntry(models.Model):
    name = models.CharField(max_length=255)
    drive_file_id = models.CharField(max_length=128, unique=True)
    mime_type = models.CharField(max_length=128, blank=True, default='')
    folder_id = models.CharField(max_length=128, blank=True, default='')

    allowed = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)

    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)

    last_processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["folder_id"]),
            models.Index(fields=["allowed", "processed"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.drive_file_id})"
