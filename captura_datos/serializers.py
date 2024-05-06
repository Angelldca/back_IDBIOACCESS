from rest_framework import serializers
from .models import Dciudadanobash, Dimagenfacial, Dciudadano, Nestado
from django.contrib.auth.models import Group, Permission, User
from django.contrib.admin.models import LogEntry
from datetime import datetime, date
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.contenttypes.models import ContentType



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


class LogEntrySerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField()
    user_username = serializers.SerializerMethodField()
    action_description = serializers.SerializerMethodField()
    #permissions = PermissionSerializer(many=True)
    class Meta:
        model = LogEntry
        fields = '__all__'

    def get_content_type_name(self, obj):
        content_type = ContentType.objects.get_for_id(obj.content_type_id)
        return content_type.model
    def get_user_username(self, obj):
        user = User.objects.get(pk=obj.user_id)
        return user.username
    def get_action_description(self, obj):
        if obj.action_flag == 1:
           
            return "Creado"
        elif obj.action_flag == 2:
            change_message = obj.get_change_message()
            return change_message
        else:
            return "Eliminado"

class GroupSerializer(serializers.ModelSerializer):
    #permissions = PermissionSerializer(many=True)
    class Meta:
        model = Group
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    user_permissions = serializers.SerializerMethodField(read_only=False)
    groups = serializers.SerializerMethodField(read_only=False)
    class Meta:
        model = User
        fields = '__all__'
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Excluir el campo de contraseña si se está listando
        if self.context['request'].method == 'GET':
            del data['password']
        return data
    def get_user_permissions(self, obj):
        if self.context['request'].method == 'GET':
            user_permissions = obj.user_permissions.all()
            return PermissionSerializer(user_permissions, many=True).data
        return obj.user_permissions.values_list('id', flat=True)

    def get_groups(self, obj):
        if self.context['request'].method == 'GET':
            groups = obj.groups.all()
            return GroupSerializer(groups, many=True).data
        return obj.groups.values_list('id', flat=True)

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

