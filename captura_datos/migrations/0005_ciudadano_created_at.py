# Generated by Django 4.2.6 on 2024-01-12 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('captura_datos', '0004_alter_ciudadano_img'),
    ]

    operations = [
        migrations.AddField(
            model_name='ciudadano',
            name='created_At',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
