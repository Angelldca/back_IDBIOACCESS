from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny
from django.contrib.auth.hashers import make_password 
from rest_framework.response import Response
from rest_framework.decorators import api_view, action
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group, Permission, User
from .serializers import PermissionSerializer, GroupSerializer, UserSerializer, LoginSerializer,LogEntrySerializer
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from rest_framework_simplejwt.tokens import TokenError, AccessToken, RefreshToken
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated,BasePermission, DjangoModelPermissions, DjangoObjectPermissions
from rest_framework.authentication import TokenAuthentication
from django.http import HttpResponse
from datetime import datetime
from django.utils import timezone
import csv
import copy


class CustomModelPermissions(DjangoModelPermissions):
    message = 'Usuario no autorizado'
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes=[IsAuthenticated,CustomModelPermissions]
    serializer_class = UserSerializer
    pagination_class = None

    def perform_create(self, serializer):
       if 'password' in serializer.validated_data:
            password = serializer.validated_data['password']
            hashed_password = make_password(password)
            serializer.validated_data['password'] = hashed_password
       serializer.save()
       user = serializer.instance
       LogEntry.objects.create(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(User).pk,  # Obtener el ContentType para el modelo Group
            object_id=user.id,
            object_repr=str(user.username),
            action_time=timezone.now(),
            action_flag=1
        )
       super().perform_create(serializer)

    def perform_update(self, serializer):
        if 'password' in serializer.validated_data:
            password = serializer.validated_data['password']
            hashed_password = make_password(password)
            serializer.validated_data['password'] = hashed_password
        grupos = self.request.data.get('groups', None)
        permisos = self.request.data.get('user_permissions', None)

        if grupos is not None:
            serializer.instance.groups.set(grupos)
        if permisos is not None:
            serializer.instance.user_permissions.set(permisos)
        user = serializer.instance
        LogEntry.objects.create(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(User).pk,  # Obtener el ContentType para el modelo Group
            object_id=user.id,
            object_repr=str(user.username),
            action_time=timezone.now(),
            change_message="Modificado",
            action_flag=2
        )
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        #user = serializer.instance
        user = instance
        # Eliminamos el objeto
        super().perform_destroy(instance)
        LogEntry.objects.create(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(User).pk,
            object_id=user.id,
            object_repr=str(user.username),
            action_time=timezone.now(),
            action_flag=3
        )
        #super().perform_delete(serializer)


    @action(detail=False, methods=["get"], name="user_autenticados",url_path='user_autenticados')
    def user_autenticados(self, request, pk=None):
        
         # Filtrar ciudadanos por el rango de fechas
        users = User.objects.all()
        for usuario in users:
            if(usuario.last_login):
             usuario.last_login = usuario.last_login.strftime('%d-%m-%Y %H:%M:%S')
         
        self.queryset =users
          
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], name="user_autenticados_csv",url_path='user_autenticados_csv')
    def user_autenticados_csv(self,request,pk= None):
        
        users = User.objects.all()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="ciudadanos_creados_por_fecha.csv"'

        
        writer = csv.writer(response)

        
        writer.writerow(['id', 'first_name','last_name','email', 'username',
         'fecha de inicio de seccion'])

 
        for usuario in users:
            fecha_login = None
            if(usuario.last_login):
             fecha_login = usuario.last_login.strftime('%d-%m-%Y %H:%M:%S')
            writer.writerow([usuario.id, usuario.first_name,usuario.last_name,usuario.email,
            usuario.username, fecha_login])

        return response

class PermissionViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated,CustomModelPermissions]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = None
#@authentication_classes([TokenAuthentication])
class GroupViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated,CustomModelPermissions]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        permissions_data = request.data.pop('permissions', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()

        LogEntry.objects.create(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(Group).pk,  # Obtener el ContentType para el modelo Group
            object_id=group.id,
            object_repr=str(group.name),
            action_time=timezone.now(),
            action_flag=1
        )

        # Asignar permisos al grupo
        for perm_id in permissions_data:
            try:
                permission = Permission.objects.get(id=perm_id)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                return Response({'error': f'Permission with id {perm_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def perform_update(self,serializer):
        group = serializer.instance
        LogEntry.objects.create(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(Group).pk,  # Obtener el ContentType para el modelo Group
            object_id=group.id,
            object_repr=str(group.name),
            action_time=timezone.now(),
            change_message="Modificado",
            action_flag=2
        )
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        group = instance

        # Eliminamos el objeto
        super().perform_destroy(instance)
        #group = self.get_object()
        LogEntry.objects.create(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(Group).pk,
            object_id=group.id,
            object_repr=str(group.name),
            action_time=timezone.now(),
            action_flag=3
        )
        #super().perform_delete(serializer)


class LogEntryViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated,CustomModelPermissions]
    queryset = LogEntry.objects.all()
    serializer_class = LogEntrySerializer
    pagination_class = None

    @action(detail=False, methods=["get"], name="historial_usuario",url_path='historial_usuario')
    def historial_usuario(self, request, pk=None):
        
        userid = request.query_params.get('userid', None)
        if userid is None:
            return Response({"error": "Debes proporcionar un nombre de usuario"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            return Response({"error": "El usuario no existe"}, status=status.HTTP_404_NOT_FOUND)
        
        log_entries = LogEntry.objects.filter(user=user)
        for log in log_entries:
            if(log.action_time):
             log.action_time = log.action_time.strftime('%d-%m-%Y %H:%M:%S')

        serializer = self.get_serializer(log_entries, many=True)
        return Response(serializer.data)
    
    #Exportar acciones realizadas por usuarios en csv
    @action(detail=False, methods=["get"], name="historial_usuario_csv",url_path='historial_usuario_csv')
    def historial_usuario_csv(self,request,pk= None):
        
        userid = request.query_params.get('userid', None)
        if userid is None:
            return Response({"error": "Debes proporcionar un nombre de usuario"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=userid)
        except User.DoesNotExist:
            return Response({"error": "El usuario no existe"}, status=status.HTTP_404_NOT_FOUND)
        
        log_entries = LogEntry.objects.filter(user=user)
        serializer = self.get_serializer(log_entries, many=True)


        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="acciones por ciudadanos.csv"'

        
        writer = csv.writer(response)

        
        writer.writerow(['fecha','responsable', 'modelo modificado','elemento modificado','accion'])

 
        for log in serializer.data:
            fecha = None
            print(log['content_type_name'])
            if(log['action_time']):
             fecha = log['action_time'][:10] if log['action_time'] else ""
            writer.writerow([fecha, log['user_username'],log['content_type_name'],log['object_repr'],
            log['action_description'] ])

        return response
    

@api_view(['POST'])
def login(request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user_serializer = UserSerializer(user)
        user_info = {
                    'id': user.id,
                    'username': user.username,
                    'is_superuser': user.is_superuser,
                    'is_staff': user.is_staff,
                    'is_active': user.is_active,
                    # Obtener información completa de los roles y permisos
                    'roles': [],
                    'permissions': list(user.user_permissions.values_list('codename', flat=True))
                }
        for group in user.groups.all():
                    role_info = {
                        'id': group.id,
                        'name': group.name,
                        # Obtener los permisos asociados al rol
                        'permissions': list(group.permissions.values_list('codename', flat=True))
                    }
                    user_info['roles'].append(role_info)
        return Response({
            'user': user_info,
            'refresh': serializer.validated_data['refresh'],
            'token': serializer.validated_data['access']
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        # Crear un nuevo usuario
        user = User.objects.create_user(username=username, password=password)
        
        # Generar tokens JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def validateToken(request):
    token = request.data.get('token')
    
    if not token:
        return Response({'error': 'Se requiere un token en la solicitud.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        decoded_token = AccessToken(token)
        token_data = decoded_token.payload
        return Response(token_data, status=status.HTTP_200_OK)
    except TokenError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)