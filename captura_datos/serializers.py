from rest_framework import serializers
from .models import Dciudadanobash, Dimagenfacial, Dciudadano, Nestado
from datetime import datetime, date

class CustomDateField(serializers.ReadOnlyField):
    def to_representation(self, value):
        if value == date.max:  # Si es 'infinity'
            return None  # O cualquier otro valor predeterminado que desees
        if isinstance(value, datetime):
            return value.date()
        return super().to_representation(value)

class CiudadanoImageSerializer(serializers.ModelSerializer):
    fecha = CustomDateField()
    fecha_actualizacion = CustomDateField()
    class Meta:
        model = Dimagenfacial
        fields = '__all__'


class CiudadanoSerializer(serializers.ModelSerializer):
    imagen = serializers.SerializerMethodField()
    fecha = CustomDateField()
    fechanacimiento = CustomDateField()
    class Meta:
        model = Dciudadano
        fields = '__all__'
    def get_imagen(self, obj):
        imagen_facial = Dimagenfacial.objects.filter(idciudadano=obj.idciudadano).first()
        if imagen_facial:
            return CiudadanoImageSerializer(imagen_facial).data
        return None

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nestado
        fields = '__all__'
class CiudadanoBashSerializer(serializers.ModelSerializer):
    idestado = EstadoSerializer()
    class Meta:
        model = Dciudadanobash
        fields = '__all__'
   




