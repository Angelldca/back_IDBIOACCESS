from django.db import models

# Create your models here.
class Ciudadano (models.Model):
    nombre = models.CharField(max_length = 200)
    apellidos = models.CharField(max_length = 200)
    dni = models.CharField(max_length = 11, unique=True)
    solapin = models.CharField(max_length = 7, unique=True)
    expediente=models.IntegerField()
    fecha_nacimiento = models.DateField()
    created_At = models.DateField(auto_now_add = True,null=True)  #DateTimeField
    edad = models.IntegerField()
    rol_institucional = models.CharField(max_length = 200)
    area = models.CharField(max_length = 200)
    img = models.BinaryField(null=True, blank=True)
    entidad = models.CharField(max_length = 200, null= True)