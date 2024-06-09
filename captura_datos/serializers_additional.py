from rest_framework import serializers
from .models import Dsolapin, Dciudadanosolapin, Ntiposolapin

class SolapinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dsolapin
        fields = '__all__'

class CiudadanoSolapinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dciudadanosolapin
        fields = '__all__'

class CodigobarraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dsolapin
        fields = ['codigobarra']

class NumerosolapinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dsolapin
        fields = ['numerosolapin']

class SerialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dsolapin
        fields = ['serial']
        
class TipoSolapinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ntiposolapin
        fields = '__all__'