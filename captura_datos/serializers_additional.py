from rest_framework import serializers
from .models import Dsolapin, Dciudadanosolapin, Dregistropago, Ntiposolapin, Ncausaanulacion
from .models import Dciudadanosolapinhist, Dnewsolapinhistorico, Doperacionsolapin, Ntipooperacionsolapin
 
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
        
class CausaAnulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ncausaanulacion
        fields = '__all__'
        
class RegistroPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dregistropago
        fields = '__all__'
        
class CiudadanoSolapinHistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dciudadanosolapinhist
        fields = '__all__'
        
class NewSolapinHistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dnewsolapinhistorico
        fields = '__all__'
        
class OperacionSolapinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doperacionsolapin
        fields = '__all__'

class TipoOperacionSolapinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ntipooperacionsolapin
        fields = '__all__'