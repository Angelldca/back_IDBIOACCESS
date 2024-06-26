"""
URL configuration for idbioaccess project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from captura_datos.api_seguridad import login, register, validateToken
import django_cas_ng.views
from captura_datos import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('captura_datos.urls')),
    path('api/seguridad/login/', login),
    path('api/seguridad/registrar/', register),
    path('api/seguridad/validatetoken/', validateToken),
    path('accounts/login/',views.CasLoginView.as_view(), name='logincas'),
    #path('accounts/login', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
    path('accounts/logout',django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
    
]

