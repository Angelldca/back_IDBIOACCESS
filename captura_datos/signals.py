import json

from django.dispatch import receiver
from django_cas_ng.signals import cas_user_authenticated, cas_user_logout
from django.contrib.auth.models import Group, Permission, User
from .serializers import PermissionSerializer, GroupSerializer, UserSerializer, LoginSerializer
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse


@receiver(cas_user_authenticated)
def cas_user_authenticated_callback(sender, **kwargs):
    user = kwargs.get('user')

    # Verificar si el usuario existe en la base de datos
    if user:
        # Generar un token de actualización
        refresh = RefreshToken.for_user(user)

        # Obtener el token de acceso
        access_token = str(refresh.access_token)

        print("Usuario {} autenticado por CAS y token JWT generado".format(user.username))
        return JsonResponse({"token": access_token}, status=200)
    else:
        print("Usuario no encontrado en la base de datos")


@receiver(cas_user_logout)
def cas_user_logout_callback(sender, **kwargs):
    args = {}
    args.update(kwargs)
    print('''cas_user_logout_callback:
    user: %s
    session: %s
    ticket: %s
    ''' % (
        args.get('user'),
        args.get('session'),
        args.get('ticket')))