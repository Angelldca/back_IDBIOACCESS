from rest_framework.authentication import BaseAuthentication
from django_cas_ng.backends import CASBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.http import HttpResponse
from rest_framework.response import Response
from django_cas_ng import views as cas_views


class CustomCASBackend(CASBackend):
 
    def authenticate(self, request, ticket, service):
        casResponse = cas_views.LoginView.as_view()(request)
        print(casResponse)

        return casResponse
        
        user = super().authenticate(request, ticket, service)
        if not user:
            #user = self.create_user(ticket)
            print(str(request))
            return  HttpResponse( {
            'user': request.user
        }) #HttpResponse({"msg" :"no hay usuario", "request ": request.user})

        print(user)
        print(ticket)
        print(service)
        return user

    def create_user(self, ticket):

        username = ticket.split('@')[0]  # Suponiendo que el ticket tiene el formato 'username@domain.com'
        user = get_user_model().objects.create_user(username=username)

        return user