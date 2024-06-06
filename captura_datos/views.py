from django.shortcuts import render

# Create your views here.
from django.http import HttpRequest, HttpResponse
from rest_framework_simplejwt.tokens import TokenError, AccessToken, RefreshToken
from django.http import JsonResponse, HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django_cas_ng import views as cas_views

def index(request: HttpRequest): #-> HttpResponse:
        if request.user.is_authenticated:
            # Generar un token de actualización
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)
            user = request.user
            print(user)
            return JsonResponse({
                 "token": access_token,
                 "user": user,
                  }, status=200)
        else:
            return JsonResponse({"error": "Usuario no autenticado"}, status=401)
    

from django.conf import settings

class CasLoginView(cas_views.LoginView):
    def successful_login(self, request: HttpRequest, next_page: str) -> HttpResponse:
        """
        This method is called on successful login. Override this method for
        custom post-auth actions (i.e, to add a cookie with a token).


        :param request:
        :param next_page:
        :return:
        """
        try:
            user = User.objects.get(username=f'{request.user.username}')
        except User.DoesNotExist:
            user = request.user


        refresh = RefreshToken.for_user(request.user)
        access_token = str(refresh.access_token)
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


        new_next_page = next_page
        new_next_page = settings.CAS_REDIRECT_URL + '/' + access_token


        return HttpResponseRedirect(new_next_page)
    





    