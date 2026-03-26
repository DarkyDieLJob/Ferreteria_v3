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


class WeeklySalesSnapshot(models.Model):
    week_start = models.DateField()
    week_end = models.DateField()

    proveedor = models.ForeignKey(
        'bdd.Proveedor', on_delete=models.CASCADE, null=True, blank=True
    )
    item = models.ForeignKey(
        'bdd.Item', on_delete=models.CASCADE, null=True, blank=True
    )

    # Operador (usuario) que realizó la venta; útil para filtros/auditoría en dashboard
    vendedor = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True
    )
    vendedor_username = models.CharField(max_length=150, null=True, blank=True)

    is_sin_registro = models.BooleanField(default=False)

    cantidad_vendida = models.FloatField(default=0.0)
    total_estimado = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["week_start", "week_end"]),
            models.Index(fields=["proveedor"]),
            models.Index(fields=["item"]),
            models.Index(fields=["vendedor"]),
        ]
        unique_together = (
            (
                "week_start",
                "week_end",
                "proveedor",
                "item",
                "is_sin_registro",
            ),
        )

    def __str__(self) -> str:
        prov = self.proveedor.text_display if self.proveedor else ("Sin registro" if self.is_sin_registro else "-")
        it = str(self.item) if self.item else ("Sin item" if self.is_sin_registro else "-")
        vend = self.vendedor_username or (self.vendedor.username if self.vendedor else "-")
        return f"{self.week_start}..{self.week_end} | {prov} | {it} | vend={vend} | qty={self.cantidad_vendida}"
