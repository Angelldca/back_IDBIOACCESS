# Generated by Django 4.2.6 on 2024-01-11 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ciudadano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('apellidos', models.CharField(max_length=200)),
                ('dni', models.CharField(max_length=11)),
                ('solapin', models.CharField(max_length=7)),
                ('expediente', models.IntegerField()),
                ('fecha_nacimiento', models.DateField()),
                ('edad', models.IntegerField()),
                ('rol_institucional', models.CharField(max_length=200)),
                ('area', models.CharField(max_length=200)),
                ('img', models.CharField(max_length=200)),
            ],
        ),
    ]
