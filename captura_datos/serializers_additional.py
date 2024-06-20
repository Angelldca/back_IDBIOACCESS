from rest_framework import serializers
from .models import Dsolapin, Dciudadano, Dciudadanosolapin, Dregistropago, Ntiposolapin, Ncausaanulacion
from .models import Dciudadanosolapinhist, Dnewsolapinhistorico, Doperacionsolapin, Ntipooperacionsolapin
from .api import CiudadanoSerializer
from django.contrib.auth.models import User

class UserSerializerViewOnly(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
 
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
    datossolapin = serializers.SerializerMethodField()
    datosciudadano = serializers.SerializerMethodField()
    datosusuario = serializers.SerializerMethodField()
    class Meta:
        model = Dregistropago
        fields = '__all__'
        
    def get_datossolapin(self, obj):
        datossolapin = Dsolapin.objects.filter(idsolapin=obj.idsolapin.idsolapin).first()
        if datossolapin:
            return SolapinSerializer(datossolapin).data
        return None
    
    def get_datosciudadano(self, obj):
        datosciudadano = Dciudadano.objects.filter(idciudadano=obj.idciudadano.idciudadano).first()
        if datosciudadano:
            return CiudadanoSerializer(datosciudadano).data
        return None
    
    def get_datosusuario(self, obj):
        datosusuario = User.objects.get(id=obj.idusuario)
        if datosusuario:
            return UserSerializerViewOnly(datosusuario).data
        return None
        
class CiudadanoSolapinHistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dciudadanosolapinhist
        fields = '__all__'
        
class NewSolapinHistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dnewsolapinhistorico
        fields = '__all__'
        
class OperacionSolapinSerializer(serializers.ModelSerializer):
    datosusuario = serializers.SerializerMethodField()
    class Meta:
        model = Doperacionsolapin
        fields = '__all__'
        
    def get_datosusuario(self, obj):
        datosusuario = User.objects.get(id=obj.idusuario.idusuario)
        if datosusuario:
            return UserSerializerViewOnly(datosusuario).data
        return None

class TipoOperacionSolapinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ntipooperacionsolapin
        fields = '__all__'