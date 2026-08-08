from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bdd', '0005_listado_planillas_error_columnas'),
    ]

    operations = [
        migrations.AddField(
            model_name='listado_planillas',
            name='file_hash',
            field=models.CharField(blank=True, default='', help_text='Hash MD5 del contenido del archivo para deteccion de duplicados', max_length=64, null=True),
        ),
    ]
