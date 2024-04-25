from rest_framework import serializers
from .models import Dciudadanobash, Dimagenfacial, Dciudadano, Nestado
from django.contrib.auth.models import Group, Permission, User
from datetime import datetime, date
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
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
   
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'



class GroupSerializer(serializers.ModelSerializer):
    #permissions = PermissionSerializer(many=True)
    class Meta:
        model = Group
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Excluir el campo de contraseña si se está listando
        if self.context['request'].method == 'GET':
            del data['password']
        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError('No se encontró ningún usuario con estas credenciales')

        return {
            'user': user,
            'refresh': str(RefreshToken.for_user(user)),
            'access': str(RefreshToken.for_user(user).access_token),
        }

