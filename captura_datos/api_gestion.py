from .models import Dciudadano, Dciudadanobash, Dciudadanosolapin, Dsolapin, Dregistropago, Ntiposolapin, Ncausaanulacion
from .models import Dciudadanosolapinhist, Dnewsolapinhistorico, Doperacionsolapin, Ntipooperacionsolapin
from .serializers import CiudadanoSerializer, CiudadanoBashSerializer
from .serializers_additional import RegistroPagoSerializer, SolapinSerializer, TipoSolapinSerializer, CausaAnulacionSerializer, CodigobarraSerializer, NumerosolapinSerializer, SerialSerializer
from .serializers_additional import CiudadanoSolapinHistSerializer, NewSolapinHistSerializer, OperacionSolapinSerializer, TipoOperacionSolapinSerializer
from rest_framework import viewsets, status, filters
from django.db.models import Q, IntegerField, Count
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models.functions import Cast, Substr
from django.db import transaction
from .api import CiudadanoPagination

################### LISTADO DE CIUDADANOS SIN SOLAPIN #########################################
class CiudadanosSinSolapinList(viewsets.ModelViewSet):
    serializer_class = CiudadanoSerializer
    pagination_class = CiudadanoPagination
    def get_queryset(self):
        return Dciudadano.objects.filter(
            ~Q(idciudadano__in=Dciudadanosolapin.objects.values('idciudadano'))
        )

    def list(self, request, *args, **kwargs):
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        atributo_valores = request.GET.dict()
        query = Q()

        self.queryset = self.get_queryset()

        for atributo, valor in atributo_valores.items():
            if atributo != 'page_size' and atributo != 'page':
                if atributo == 'nombre_apellidos':
                    palabras = valor.split()
                    for palabra in palabras:
                        query |= (
                            Q(primernombre__icontains=palabra) |
                            Q(segundonombre__icontains=palabra) |
                            Q(primerapellido__icontains=palabra) |
                            Q(segundoapellido__icontains=palabra)
                        )
                else:
                    query |= Q(**{f'{atributo}__icontains': valor})
        
        if query:
            self.queryset = self.queryset.filter(query)
        
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)


########################## LISTADO DE CIUDADANOS CON SOLAPIN ####################################
class CiudadanosConSolapinList(viewsets.ModelViewSet):
    serializer_class = CiudadanoSerializer
    pagination_class = CiudadanoPagination

    def get_queryset(self):
        return Dciudadano.objects.filter(
            idciudadano__in=Dciudadanosolapin.objects.values('idciudadano')
        )

    def list(self, request, *args, **kwargs):
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        atributo_valores = request.GET.dict()
        query = Q()

        self.queryset = self.get_queryset()

        for atributo, valor in atributo_valores.items():
            if atributo != 'page_size' and atributo != 'page':
                if atributo == 'nombre_apellidos':
                    palabras = valor.split()
                    for palabra in palabras:
                        query |= (
                            Q(primernombre__icontains=palabra) |
                            Q(segundonombre__icontains=palabra) |
                            Q(primerapellido__icontains=palabra) |
                            Q(segundoapellido__icontains=palabra)
                        )
                else:
                    query |= Q(**{f'{atributo}__icontains': valor})
        
        if query:
            self.queryset = self.queryset.filter(query)
        
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

######################### LISTADO DE CIUDADANOS CON SOLAPIN DESACTIVADO ###################
class CiudadanosSolapinDesactivadoList(viewsets.ModelViewSet):
    serializer_class = CiudadanoSerializer
    pagination_class = CiudadanoPagination

    def get_queryset(self):
        # Filtrar los ciudadanos cuyo solapín asociado tiene el estado 0
        solapines_estado_cero = Dsolapin.objects.filter(estado=0).values('idsolapin')
        return Dciudadano.objects.filter(
            idciudadano__in=Dciudadanosolapin.objects.filter(idsolapin__in=solapines_estado_cero).values('idciudadano')
        )

    def list(self, request, *args, **kwargs):
        # Mantener la lógica de paginación existente
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        atributo_valores = request.GET.dict()
        query = Q()

        self.queryset = self.get_queryset()

        # Mantener la lógica de filtrado existente
        for atributo, valor in atributo_valores.items():
            if atributo != 'page_size' and atributo != 'page':
                if atributo == 'nombre_apellidos':
                    palabras = valor.split()
                    for palabra in palabras:
                        query |= (
                            Q(primernombre__icontains=palabra) |
                            Q(segundonombre__icontains=palabra) |
                            Q(primerapellido__icontains=palabra) |
                            Q(segundoapellido__icontains=palabra)
                        )
                else:
                    query |= Q(**{f'{atributo}__icontains': valor})
        
        if query:
            self.queryset = self.queryset.filter(query)
        
        # Paginación y respuesta
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)


########################## VISTAS SOLAPIN #################################################
class SolapinViewSet(viewsets.ModelViewSet):
    serializer_class = SolapinSerializer
    queryset = Dsolapin.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['numerosolapin']
    
    ################ BUSCAR EL SOLAPIN ######################################################
    @action(detail=False, methods=['post'])
    def get_solapin_by_numero(self, request):
        numerosolapin = request.data.get('numerosolapin')
        try:
            solapin = Dsolapin.objects.get(numerosolapin=numerosolapin)
            serializer = self.get_serializer(solapin)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Dsolapin.DoesNotExist:
            return Response({'error': 'Solapin not found'}, status=status.HTTP_404_NOT_FOUND)
    ############################### CREAR SOLAPIN ###############################################
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def create_solapin(self, request):
        data = request.data
        try:
            # Validar si el ciudadano ya existe
            ciudadano = Dciudadano.objects.get(idciudadano=data.get('idciudadano'))
            ciudadanobash = Dciudadanobash.objects.filter(idpersona=ciudadano.idpersona.idpersona).first()
            
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
                      
                ciudadano.solapin = data['numerosolapin']
                ciudadano.save()
                ciudadanobash.solapin = data['numerosolapin']
                ciudadanobash.save()
                
                return Response(solapin_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(solapin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Dciudadano.DoesNotExist:
            return Response({'error': 'Ciudadano not found'}, status=status.HTTP_404_NOT_FOUND)
        except Dciudadanobash.DoesNotExist:
            return Response({'error': 'Ciudadano Bash not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    ############################# ELIMINAR SOLAPIN ############################################
    @action(detail=False, methods=['delete'])
    @transaction.atomic
    def delete_solapin(self, request):
        data = request.data
        try:
            solapin = Dsolapin.objects.get(numerosolapin=data.get('numerosolapin'))
            ciudadano_solapin = Dciudadanosolapin.objects.get(idsolapin=solapin)
            ciudadano = Dciudadano.objects.get(solapin=solapin.numerosolapin)
            ciudadanobash = Dciudadanobash.objects.filter(idpersona=ciudadano.idpersona.idpersona).first()
            
            ciudadano.solapin = None
            ciudadano.save()
            
            ciudadanobash.solapin = None
            ciudadanobash.save()
            
            ciudadano_solapin.delete()
            solapin.delete()
            
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Dsolapin.DoesNotExist:
            return Response({'error': 'Solapin not found'}, status=status.HTTP_404_NOT_FOUND)
        except Dciudadanosolapin.DoesNotExist:
            return Response({'error': 'Association not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    ########################### ACTUALIZAR SOLAPIN ############################################
    @action(detail=False, methods=['put'])
    @transaction.atomic
    def update_solapin(self, request):
        data = request.data
        try:
            solapin = Dsolapin.objects.get(numerosolapin=data.get('numerosolapin'))
            
            try:
                nuevo = data['nuevonumerosolapin']
            except Exception:
                nuevo = solapin.numerosolapin
                
            ciudadano_solapin = Dciudadanosolapin.objects.get(idsolapin=solapin.idsolapin)
            
            try:
                ciudadano = Dciudadano.objects.get(solapin=solapin.numerosolapin)
            except Dciudadano.DoesNotExist:
                try:
                    ciudadano = Dciudadano.objects.get(idciudadano=ciudadano_solapin.idciudadano)
                except Dciudadano.DoesNotExist:
                    return Response({'error': 'Solapin no encontrado para este ciudadano, imposible actualizar'}, status=status.HTTP_404_NOT_FOUND)
            
            try:
                ciudadanobash = Dciudadanobash.objects.filter(solapin=solapin.numerosolapin).first()  
            except Dciudadanobash.DoesNotExist:
                try:
                    ciudadanobash = Dciudadanobash.objects.filter(idpersona=ciudadano.idpersona.idpersona).first()
                except Dciudadanobash.DoesNotExist:
                    return Response({'error': 'Solapin no encontrado para este ciudadano bash, imposible actualizar'}, status=status.HTTP_404_NOT_FOUND)
            
            ciudadano.solapin = nuevo
            ciudadano.save()
            
            ciudadanobash.solapin = nuevo
            ciudadanobash.save()
            
            data['numerosolapin'] = nuevo

            solapin_serializer = SolapinSerializer(solapin, data=data, partial=True)
            if solapin_serializer.is_valid():
                solapin_serializer.save()
                
                return Response(solapin_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(solapin_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Dsolapin.DoesNotExist:
            return Response({'error': 'Solapin not found'}, status=status.HTTP_404_NOT_FOUND)
        except Dciudadano.DoesNotExist:
            return Response({'error': 'Ciudadano not found'}, status=status.HTTP_404_NOT_FOUND)
        except Dciudadanobash.DoesNotExist:
            return Response({'error': 'Ciudadano bash not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            transaction.set_rollback(True)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    ######################### FUNCIONES ADICIONALES ###############################################3
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
    
    @action(detail=False, methods=['get'])
    def get_solapin_count_by_serial(self, request):
        serial = request.query_params.get('serial')
        if not serial:
            return Response({'error': 'Serial is required'}, status=status.HTTP_400_BAD_REQUEST)
        count = Dsolapin.objects.filter(serial=serial).count()
        return Response({'count': count}, status=status.HTTP_200_OK)
    
class TipoSolapinViewSet (viewsets.ModelViewSet):
    pagination_class = None
    serializer_class = TipoSolapinSerializer
    def get_queryset(self):
        return Ntiposolapin.objects.all()
    
class CausaAnulacionViewSet (viewsets.ModelViewSet):
    pagination_class = None
    serializer_class = CausaAnulacionSerializer
    def get_queryset(self):
        return Ncausaanulacion.objects.all()
    
###################### REGISTRO PAGOS ###########################################33

class RegistroPagoViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Dregistropago.objects.all()
    serializer_class = RegistroPagoSerializer
    
class CiudadanoSolapinHistViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Dciudadanosolapinhist.objects.all()
    serializer_class = CiudadanoSolapinHistSerializer

class NewSolapinHistViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Dnewsolapinhistorico.objects.all()
    serializer_class = NewSolapinHistSerializer
    
class OperacionSolapinViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Doperacionsolapin.objects.all()
    serializer_class = OperacionSolapinSerializer
    
class TipoOperacionSolapinViewSet(viewsets.ModelViewSet):
    pagination_class = None
    queryset = Ntipooperacionsolapin.objects.all()
    serializer_class = TipoOperacionSolapinSerializer