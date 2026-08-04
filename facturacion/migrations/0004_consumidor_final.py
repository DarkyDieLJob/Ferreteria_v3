from django.db import migrations


def crear_consumidor_final(apps, schema_editor):
    Cliente = apps.get_model("facturacion", "Cliente")
    Cliente.objects.update_or_create(
        pk=1,
        defaults={
            "razon_social": "Consumidor Final",
            "cuit_dni": "0",
            "responsabilidad_iva": "C",
            "tipo_documento": " ",
        },
    )


def noop_reverse(apps, schema_editor):
    # No revertimos para evitar borrar un cliente usado por transacciones existentes.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("facturacion", "0003_remove_articulovendido_descripcion_sin_registro_and_more"),
    ]

    operations = [
        migrations.RunPython(crear_consumidor_final, noop_reverse),
    ]
