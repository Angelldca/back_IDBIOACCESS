# Generated by Django 4.2.6 on 2024-01-11 23:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('captura_datos', '0002_ciudadano_prueba_alter_ciudadano_dni_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ciudadano',
            old_name='prueba',
            new_name='entidad',
        ),
    ]
