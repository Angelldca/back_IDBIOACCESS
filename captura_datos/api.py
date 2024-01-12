from .models import Ciudadano
from rest_framework import viewsets, permissions
from .serializers import CiudadanoSerializer

class CiudadanoViewSet(viewsets.ModelViewSet):
    queryset = Ciudadano.objects.all()
    permissions_classes = [permissions.AllowAny]
    serializer_class = CiudadanoSerializer