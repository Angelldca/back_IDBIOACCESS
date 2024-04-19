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
from .serializers import PermissionSerializer, GroupSerializer, UserSerializer

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated,BasePermission, DjangoModelPermissions, DjangoObjectPermissions
from rest_framework.authentication import TokenAuthentication



import copy


class CustomModelPermissions(DjangoModelPermissions):
    message = 'Usuario no autorizado'
    def __init__(self):
        self.perms_map = copy.deepcopy(self.perms_map)
        self.perms_map['GET'] = ['%(app_label)s.view_%(model_name)s']


@authentication_classes([TokenAuthentication])
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


@authentication_classes([TokenAuthentication])
class PermissionViewSet(viewsets.ModelViewSet):
    permission_classes=[IsAuthenticated,CustomModelPermissions]
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    pagination_class = None
@authentication_classes([TokenAuthentication])
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

        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': {'id': user.id, 'username': user.username}})
        else:
            # Verificar si el usuario existe
            try:
                user = User.objects.get(username=username)
                # Si el usuario existe, pero la contraseña es incorrecta
                return Response({'error': 'La contraseña es incorrecta.'}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                # Si el usuario no existe en absoluto
                return Response({'error': 'El nombre de usuario no existe.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def register(request):
    serializer = UserSerializer(data = request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password'] 
        user = User.objects.create_user(username=username, password=password)
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data}, status= status.HTTP_201_CREATED)
    
    
    return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)