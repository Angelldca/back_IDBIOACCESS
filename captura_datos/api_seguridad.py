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
from .serializers import PermissionSerializer, GroupSerializer, UserSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import TokenError, AccessToken
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated,BasePermission, DjangoModelPermissions, DjangoObjectPermissions
from rest_framework.authentication import TokenAuthentication



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
       
        password = serializer.validated_data['password']
        hashed_password = make_password(password)
        serializer.validated_data['password'] = hashed_password
        super().perform_create(serializer)

    def perform_update(self, serializer):
        if 'password' in serializer.validated_data:
            password = serializer.validated_data['password']
            hashed_password = make_password(password)
            serializer.validated_data['password'] = hashed_password
        super().perform_update(serializer)



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

        # Asignar permisos al grupo
        for perm_id in permissions_data:
            try:
                permission = Permission.objects.get(id=perm_id)
                group.permissions.add(permission)
            except Permission.DoesNotExist:
                return Response({'error': f'Permission with id {perm_id} does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)




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