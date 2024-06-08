from .models import Dciudadano, Dciudadanosolapin, Dsolapin
from .serializers import CiudadanoSerializer
from .serializers_additional import SolapinSerializer, CiudadanoSolapinSerializer, CodigobarraSerializer, NumerosolapinSerializer, SerialSerializer
from rest_framework import viewsets, status, filters
from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import Cast, Substr
from django.db.models import IntegerField
from django.db import transaction

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
        

class SolapinViewSet(viewsets.ModelViewSet):
    serializer_class = SolapinSerializer
    queryset = Dsolapin.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['numerosolapin']
    
    # Gestion Solapines
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def create_solapin(self, request):
        data = request.data
        try:
            # Validar si el ciudadano ya existe
            ciudadano = Dciudadano.objects.get(idciudadano=data.get('idciudadano'))

            # Crear el solapin
            solapin_serializer = SolapinSerializer(data=data)
            if solapin_serializer.is_valid():
                solapin = solapin_serializer.save()
                
                # Asociar el solapin al ciudadano
                Dciudadanosolapin.objects.create(
                    idciudadano=ciudadano,
                    idsolapin=solapin,
                    fecha=data.get('fecha')
                )
                
                return Response(solapin_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(solapin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Dciudadano.DoesNotExist:
            return Response({'error': 'Citizen not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    @transaction.atomic
    def delete_solapin(self, request, pk=None):
        try:
            # Obtener el solapin y la asociación con el ciudadano
            solapin = self.get_object()
            ciudadano_solapin = Dciudadanosolapin.objects.get(idsolapin=solapin)
            
            # Eliminar la relación y el solapin
            ciudadano_solapin.delete()
            solapin.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Dciudadanosolapin.DoesNotExist:
            return Response({'error': 'Association not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
    # Funciones Adicionales de Generacion de Solapin
    @action(detail=False, methods=['get'])
    def ultimo_codigobarra(self, request):
        solapin = Dsolapin.objects.annotate(
            numeric_codigobarra=Substr('codigobarra', 2)
        ).order_by('-numeric_codigobarra').first()
        if solapin:
            serializer = CodigobarraSerializer(solapin)
            return Response(serializer.data)
        return Response({'error': 'No data found'}, status=404)

    @action(detail=False, methods=['get'])
    def ultimo_numerosolapin(self, request):
        solapin = Dsolapin.objects.annotate(
            numeric_numerosolapin=Substr('numerosolapin', 2)
        ).order_by('-numeric_numerosolapin').first()
        if solapin:
            serializer = NumerosolapinSerializer(solapin)
            return Response(serializer.data)
        return Response({'error': 'No data found'}, status=404)

    @action(detail=False, methods=['get'])
    def ultimo_serial(self, request):
        solapin = Dsolapin.objects.exclude(serial__isnull=True).annotate(
            numeric_serial=Cast('serial', IntegerField())
        ).order_by('-numeric_serial').first()
        if solapin:
            serializer = SerialSerializer(solapin)
            return Response(serializer.data)
        return Response({'error': 'No data found'}, status=404)
