# Generated by Django 4.2.6 on 2024-01-12 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('captura_datos', '0003_rename_prueba_ciudadano_entidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ciudadano',
            name='img',
            field=models.BinaryField(blank=True, null=True),
        ),
    ]
