from rest_framework import serializers
from .models import Ciudadano


class CiudadanoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ciudadano
        fields = ['id', 'nombre', 'apellidos', 'dni','solapin',
        'expediente','fecha_nacimiento','edad','rol_institucional','area','img','entidad', 'created_At']
        read_only_fields = ['created_At',]

