from .models import Dciudadano, Dciudadanosolapin
from .serializers import CiudadanoSerializer
from rest_framework import viewsets
from django.db.models import Q

class CiudadanosSinSolapinList(viewsets.ModelViewSet):
    serializer_class = CiudadanoSerializer

    def get_queryset(self):
        return Dciudadano.objects.filter(
            ~Q(idciudadano__in=Dciudadanosolapin.objects.values('idciudadano'))
        )

class CiudadanosConSolapinList(viewsets.ModelViewSet):
    serializer_class = CiudadanoSerializer

    def get_queryset(self):
        return Dciudadano.objects.filter(
            idciudadano__in=Dciudadanosolapin.objects.values('idciudadano')
        )