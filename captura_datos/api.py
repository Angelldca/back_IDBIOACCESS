from .models import Dciudadanobash, Dimagenfacial, Dciudadano, Nestado, Dhuellaciudadano
from django.contrib.admin.models import LogEntry
from django.db.models import Subquery
from rest_framework import viewsets, permissions, generics, status
from rest_framework.views import APIView
from django.db.utils import DataError
from django.http import HttpResponse
from rest_framework.decorators import action
from django.db import connection
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication
from .api_seguridad import CustomModelPermissions
from .serializers import CiudadanoSerializer, CiudadanoBashSerializer, CiudadanoImageSerializer
from rest_framework.pagination import PageNumberPagination
from .imgProcess import ImgProcess
from rest_framework.response import Response
from datetime import datetime, timedelta
from django.utils import timezone
from io import TextIOWrapper
from io import BytesIO
import io
import pytz
from copy import copy
import numpy as np
import base64
import csv
import cv2
import uuid
import os
from django.db.models import Q
class CiudadanoPagination(PageNumberPagination):
     page_size_query_param = 10  # Número de elementos por páginas
     page_size =6



class CiudadanoBashViewCapturaBiograficos(viewsets.ModelViewSet):
    queryset =Dciudadanobash.objects.all()
    permission_classes = [IsAuthenticated, CustomModelPermissions]
    serializer_class = CiudadanoBashSerializer
    pagination_class = CiudadanoPagination
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #self.imgP = ImgProcess()

    def create(self, request):
        id_persona = uuid.uuid4()
        id_persona_str = str(id_persona).replace("-", "")
        request.data['idpersona'] = id_persona_str
        request.data['idestado'] = 3
        request.data['fecha_registro_modificacion'] = timezone.now()
        #request.data['area'] = timezone.now()
        idexpediente = request.data['idexpediente']
        carnetidentidad = request.data['carnetidentidad']
        
        ciudadano_existente = Dciudadanobash.objects.filter(
               idexpediente=idexpediente
           ).first() or Dciudadano.objects.filter(
               carnetidentidad=carnetidentidad
           ).first()
        if ciudadano_existente:
            return Response("El ciudadano ya existe", status=status.HTTP_400_BAD_REQUEST)
        serializer = CiudadanoBashSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        ciudadano_bash = serializer.instance
        #self.request.data['fecha_registro_modificacion'] = timezone.now().date()
        #serializer = CiudadanoBashSerializer(ciudadano_bash, data=self.request.data)
        self.request.data['idestado'] = 1
        
        serializer.save(data=self.request.data ,fecha_registro_modificacion=timezone.now())
        if serializer.is_valid():
            
            ciudadano = Dciudadano.objects.filter(
            idpersona=ciudadano_bash.idpersona
            ).exists()
            if ciudadano:
                ciudadano = Dciudadano.objects.get(idpersona=ciudadano_bash.idpersona)
                ciudadano.area = serializer.validated_data.get('identificadorarea')
                ciudadano.roluniversitario = serializer.validated_data.get('identificadorroluni')
                ciudadano.fecha = timezone.now().date()
                ciudadano.idpersona = serializer.validated_data.get('idpersona')
                ciudadano.carnetidentidad = serializer.validated_data.get('carnetidentidad')
                ciudadano.primernombre = serializer.validated_data.get('primernombre')
                ciudadano.segundonombre = serializer.validated_data.get('segundonombre')
                ciudadano.primerapellido = serializer.validated_data.get('primerapellido')
                ciudadano.segundoapellido = serializer.validated_data.get('segundoapellido')
                ciudadano.provincia = serializer.validated_data.get('provincia')
                ciudadano.municipio = serializer.validated_data.get('municipio')
                ciudadano.sexo = serializer.validated_data.get('sexo')
                ciudadano.residente = serializer.validated_data.get('residente')
                ciudadano.fechanacimiento = serializer.validated_data.get('fechanacimiento')
                ciudadano.save()

            
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        
        atributo_valores = request.GET.dict()
        
        nuevo_diccionario = {clave: valor for clave, valor in atributo_valores.items() if clave != 'page'}
        query = Q()
        self.queryset = Dciudadanobash.objects.all().exclude(idestado=2).order_by('fecha_registro_modificacion')
        for atributo, valor in atributo_valores.items():
            print(atributo, valor)
            if atributo != 'page_size' and atributo != 'page':
                
                if(atributo == 'nombre_apellidos'):

                    palabras = valor.split()
                    for palabra in palabras:
                        self.queryset = self.queryset.filter(primernombre__icontains = palabra) | self.queryset.filter(segundonombre__icontains = palabra) | self.queryset.filter(primerapellido__icontains=palabra)| self.queryset.filter(segundoapellido__icontains=palabra)
                    page = self.paginate_queryset(self.queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)
                else:
                    query |= Q(**{f'{atributo}': valor})
                    
       
        if nuevo_diccionario:      
            self.queryset = self.queryset.filter(query) #self.queryset  Ciudadano.objects.filter(query)
            
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=["get"], name="ciudadanosbash_sin_img",url_path='ciudadanosbash_sin_img')
    def list_sin_imagen(self, request, *args, **kwargs):
        consulta_sql = """
        SELECT * FROM public.dciudadanobash 
        LEFT JOIN public.dciudadano ON public.dciudadano.idpersona = public.dciudadanobash.idpersona 
        WHERE public.dciudadano.idpersona IS NULL;
        """
        ciudadanos_bash_sin_ciudadano = Dciudadanobash.objects.raw(consulta_sql)
        ids = [ciudadano.idpersona for ciudadano in ciudadanos_bash_sin_ciudadano]

        self.queryset = Dciudadanobash.objects.filter(idpersona__in=ids).order_by('fecha_registro_modificacion')
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)


        #marcar ciudadanos inactivos
    @action(detail=True, methods=['post'], name='make_estado_delete', url_path='make_estado_delete')
    def make_estado_delete(self, request, pk=None):
        ciudadano = get_object_or_404(Dciudadanobash, pk=pk)
        estado_nuevo = Nestado.objects.get(idestado=2)
        ciudadano.idestado = estado_nuevo
        ciudadano.save()
        object_repr = f"{ciudadano.primernombre or ''} {ciudadano.segundonombre or ''} {ciudadano.primerapellido or ''} {ciudadano.segundoapellido or ''}"

        LogEntry.objects.create(
            user_id=self.request.user.id,
            content_type_id=ContentType.objects.get_for_model(Dciudadanobash).pk,
            object_id=ciudadano.idpersona,
            object_repr= object_repr,
            action_time=timezone.now(),
            action_flag=3,
            change_message="Eliminar: "+ request.data['descripcion']
        )
        
        return Response({'message': 'Estado del ciudadano cambiado satisfactoriamente'}, status=status.HTTP_200_OK)
class CiudadanoViewCapturaBiograficos(viewsets.ModelViewSet):
    queryset = Dciudadano.objects.all()
    imagenFacial = Dimagenfacial.objects.all()
    permission_classes = [IsAuthenticated, CustomModelPermissions]
    serializer_class = CiudadanoSerializer
    pagination_class = CiudadanoPagination
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        #self.imgP = ImgProcess()
    def create(self, request):
        idexpediente = request.data['idexpediente']
        carnetidentidad = request.data['carnetidentidad']
        solapin = request.data['solapin']
        idpersona = request.data['idpersona']
        fechanacimiento = datetime.strptime(request.data['fechanacimiento'] , '%Y-%m-%d').date()
        
        if idexpediente or carnetidentidad or solapin or idpersona:
           
           ciudadano_existente = Dciudadano.objects.filter(
               idpersona=idpersona
           ).first() or Dciudadano.objects.filter(
               idexpediente=idexpediente
           ).first() or Dciudadano.objects.filter(
               carnetidentidad=carnetidentidad
           ).first()
           if ciudadano_existente:
                '''
                ciudadano = Dciudadano.objects.filter(
                idexpediente=idexpediente,
                carnetidentidad=carnetidentidad,
                solapin=solapin,
                idpersona=idpersona
                ).first()
                '''
                
                serializer = CiudadanoSerializer(ciudadano_existente)
                return Response(serializer.data, status=status.HTTP_200_OK)
           else:
              serializer = self.serializer_class(data=request.data)
              print("El ciudadano no existe")
              if serializer.is_valid():
                serializer.save(fecha=timezone.now().date(),fechanacimiento=fechanacimiento)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
              else: 
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "Faltan parámetros"}, status=status.HTTP_400_BAD_REQUEST)


    def perform_update(self, serializer):
        serializer.save(fecha=timezone.now().date())


    def list(self, request, *args, **kwargs):
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        
        atributo_valores = request.GET.dict()
        
        nuevo_diccionario = {clave: valor for clave, valor in atributo_valores.items() if clave != 'page'}
        query = Q()
        self.queryset = Dciudadano.objects.exclude(idpersona__idestado=2).order_by('fecha')
        for atributo, valor in atributo_valores.items():
            
            if atributo != 'page_size' and atributo != 'page':
                
                if(atributo == 'nombre_apellidos'):

                    palabras = valor.split()
                    for palabra in palabras:
                        self.queryset = self.queryset.filter(primernombre__icontains = palabra) | self.queryset.filter(segundonombre__icontains = palabra) | self.queryset.filter(primerapellido__icontains=palabra)| self.queryset.filter(segundoapellido__icontains=palabra)
                    page = self.paginate_queryset(self.queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)
                else:
                    query |= Q(**{f'{atributo}': valor})
                    
       
        if nuevo_diccionario:      
            self.queryset = self.queryset.filter(query) #self.queryset  Ciudadano.objects.filter(query)
            
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)
# Ciudadanos sin captura de imagen
    @action(detail=False, methods=["get"], name="ciudadanos_sin_img",url_path='ciudadanos_sin_img')
    def list_sin_imagen(self, request, *args, **kwargs):
        self.queryset = self.get_ciudadanos_sin_imagen()
        self.queryset = self.queryset.exclude(idpersona__idestado=2).order_by('fecha')
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        atributo_valores = request.GET.dict()
        nuevo_diccionario = {clave: valor for clave, valor in atributo_valores.items() if clave != 'page' }
        query = Q()
        for atributo, valor in atributo_valores.items():
            if atributo != 'page_size' and atributo != 'page' :
                
                if(atributo == 'nombre_apellidos'):
                    
                    palabras = valor.split()
                    for palabra in palabras:
                        self.queryset = self.queryset.filter(primernombre__icontains = palabra) | self.queryset.filter(segundonombre__icontains = palabra) | self.queryset.filter(primerapellido__icontains=palabra)| self.queryset.filter(segundoapellido__icontains=palabra)
                    page = self.paginate_queryset(self.queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)
                else:
                    query &= Q(**{f'{atributo}': valor})
                    
       
        if nuevo_diccionario:       
            self.queryset = self.queryset.filter(query)
            
            
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    def get_ciudadanos_sin_imagen(self):
        subquery = Dimagenfacial.objects.values('idciudadano')
        # Obtener queryset de ciudadanos sin imagen

        ciudadanos_sin_imagen = Dciudadano.objects.exclude(idciudadano__in=Subquery(subquery))
        #Dciudadano.objects.exclude(idciudadano__in=Subquery(subquery))
        return ciudadanos_sin_imagen
    # Ciudadanos sin captura de huella
    @action(detail=False, methods=["get"], name="ciudadanos_sin_huella",url_path='ciudadanos_sin_huella')
    def list_sin_huella(self, request, *args, **kwargs):
        self.queryset = self.get_ciudadanos_sin_huella()
        self.queryset = self.queryset.exclude(idpersona__idestado=2).order_by('fecha')
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        atributo_valores = request.GET.dict()
        nuevo_diccionario = {clave: valor for clave, valor in atributo_valores.items() if clave != 'page' }
        query = Q()
        for atributo, valor in atributo_valores.items():
            if atributo != 'page_size' and atributo != 'page' :
                
                if(atributo == 'nombre_apellidos'):
                    
                    palabras = valor.split()
                    for palabra in palabras:
                        self.queryset = self.queryset.filter(primernombre__icontains = palabra) | self.queryset.filter(segundonombre__icontains = palabra) | self.queryset.filter(primerapellido__icontains=palabra)| self.queryset.filter(segundoapellido__icontains=palabra)
                    page = self.paginate_queryset(self.queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)
                else:
                    query &= Q(**{f'{atributo}': valor})
                    
       
        if nuevo_diccionario:       
            self.queryset = self.queryset.filter(query)
            
            
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    def get_ciudadanos_sin_huella(self):
        subquery = Dhuellaciudadano.objects.values('idciudadano')
        # Obtener queryset de ciudadanos sin imagen

        ciudadanos_sin_imagen = Dciudadano.objects.exclude(idciudadano__in=Subquery(subquery))
        #Dciudadano.objects.exclude(idciudadano__in=Subquery(subquery))
        return ciudadanos_sin_imagen
    #Listar ciudadanos creados por fecha
    @action(detail=False, methods=["get"], name="ciudadanos_rangoFecha",url_path='ciudadanos_rangoFecha')
    def ciudadanos_rangoFecha(self, request, pk=None):
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        fecha_inicio_str = request.GET.get('fecha_inicio', '')
        fecha_fin_str = request.GET.get('fecha_fin', '')
        #######################
        if fecha_inicio_str is None or fecha_fin_str is None:
            return Response({'error': 'Formato de fecha incorrecto. Utilice el formato YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
        except ValueError:
                return Response({'error': 'Formato de fecha incorrecto. Utilice el formato YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
         
         # Filtrar ciudadanos por el rango de fechas
        tz = pytz.timezone('UTC')  # Puedes ajustar 'UTC' a la zona horaria que prefieras
        fecha_inicio = timezone.make_aware(fecha_inicio, tz)
        fecha_fin = timezone.make_aware(fecha_fin + timedelta(days=1), tz)
        self.queryset = self.queryset.exclude(idpersona__idestado=2).order_by('fecha')
        self.queryset = self.queryset.filter(fecha__range=(fecha_inicio, fecha_fin))
          
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    #Listar captura de imagen por fecha
    @action(detail=False, methods=["get"], name="ciudadanos_Img_rangoFecha",url_path='ciudadanos_Img_rangoFecha')
    def ciudadanos_Img_rangoFecha(self, request, pk=None):
        
        fecha_inicio_str = request.GET.get('fecha_inicio', '')
        fecha_fin_str = request.GET.get('fecha_fin', '')
        #######################
        if fecha_inicio_str is None or fecha_fin_str is None:
            return Response({'error': 'Formato de fecha incorrecto. Utilice el formato YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
        except ValueError:
                return Response({'error': 'Formato de fecha incorrecto. Utilice el formato YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
            # Filtrar ciudadanos por el rango de fechas
        tz = pytz.timezone('UTC')  
        fecha_inicio = timezone.make_aware(fecha_inicio, tz)
        fecha_fin = timezone.make_aware(fecha_fin + timedelta(days=1), tz)
        ciudadanos_con_imagen = Dimagenfacial.objects.filter(fecha_actualizacion__range=(fecha_inicio, fecha_fin)).values('idciudadano')
        self.queryset = Dciudadano.objects.filter(idciudadano__in=ciudadanos_con_imagen)
        self.queryset = self.queryset.exclude(idpersona__idestado=2).order_by('fecha')
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)
#Exportar registro csv de ciudadanos sin captura de imagen     

class CiudadanoImageViewCapturaBiometricos(viewsets.ModelViewSet):
    queryset = Dimagenfacial.objects.all()
    permission_classes = [IsAuthenticated, CustomModelPermissions]
    serializer_class = CiudadanoImageSerializer
    pagination_class = CiudadanoPagination
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.imgP = ImgProcess()
     #Crear imagen 
    def create(self, request, *args, **kwargs):
        foto_data = self.request.data.get('foto')
        idciudadano = request.data.get('idciudadano')
      
        imagen_recortada = self.imgP.recortar_imagen(foto_data,640, 480,300,400)
        imagen_facial = Dimagenfacial.objects.filter(idciudadano=idciudadano).first()
        fecha_actualizacion = timezone.now().date()
        if imagen_facial:
            
            imagen_facial.foto = imagen_recortada
            imagen_facial.fecha_actualizacion = fecha_actualizacion
            imagen_facial.save()
            serializer = self.get_serializer(imagen_facial)
            return Response({'detail': 'Imagen actualizada exitosamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                foto=imagen_recortada,
                fecha=fecha_actualizacion,
                fecha_actualizacion=fecha_actualizacion
            )
            return Response({'detail': 'Imagen creada exitosamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)

    #Actualizar imagen Ciudadanos   
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if 'foto' in request.data:
            img_data = request.data.get('foto')
            
            #imgMediaPipe = self.imgP.blob_to_image(img_data)
            imagen_recortada = self.imgP.recortar_imagen(img_data,640, 480,300,400)
            instance.foto = imagen_recortada
            instance.fecha_actualizacion = timezone.now().date()
            instance.save()
            serializer = self.get_serializer(instance)
            return Response({'data':serializer.data,'detail': 'Actualización exitosa.'}, status=status.HTTP_200_OK)
        for key, value in request.data.items():
            if key not in ['foto'] and value:
                setattr(instance, key, value)
            else: return Response({'detail': 'no se permiten campos vacios.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            instance.save()
            serializer = self.get_serializer(instance)
        except DataError as e:
            error_message = str(e)
            return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'data': serializer.data,'detail': 'Actualización exitosa.'}, status=status.HTTP_200_OK)


   
        
#########################


class CiudadanosCSVCreateView(viewsets.ViewSet):
    queryset = Dciudadano.objects.all()
    permission_classes = [IsAuthenticated, CustomModelPermissions]
    
#Importar lista de ciudadanos csv
    def create(self, request, *args, **kwargs): 
        file = request.data.get('planilla_ciudadanos', None)
        ciudadanos_data = []
        if file is None:
            return Response({'error': 'No se proporcionó ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decodificar el contenido del archivo CSV
            data_file = TextIOWrapper(file.file, encoding=request.encoding)
            reader = csv.DictReader(data_file)
            ciudadanos_data = [row for row in reader]
            
        except Exception as e:
            return Response({'error': f'Error al leer el archivo CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        
        nuevos_ciudadanos = []
        carnetidentidad_list = [ciudadano.get('carnetidentidad') for ciudadano in ciudadanos_data]
        idexpediente_list = [ciudadano.get('idexpediente') for ciudadano in ciudadanos_data]
        
        # Verificar duplicados dentro del mismo lote de datos enviados
        if len(carnetidentidad_list) != len(set(carnetidentidad_list)):
            return Response({'error': 'El registro contiene ciudadanos con carnet de identidad duplicados.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(idexpediente_list) != len(set(idexpediente_list)):
            return Response({'error': 'El registro contiene ciudadanos con expediente duplicados.'}, status=status.HTTP_400_BAD_REQUEST)
        # Validar y guardar los datos de los ciudadanos
        for ciudadano_data in ciudadanos_data:
            # Verificar si el ciudadano ya existe
            idexpediente = ciudadano_data.get('idexpediente')
            solapin = ciudadano_data.get('solapin')
            carnetidentidad = ciudadano_data.get('carnetidentidad')
    
            if not Dciudadanobash.objects.filter(idexpediente=idexpediente, carnetidentidad=carnetidentidad).exists():
                id_persona = uuid.uuid4()
                id_persona_str = str(id_persona).replace("-", "")
                ciudadano_data['idestado'] = 3
                ciudadano_data['fecha_registro_modificacion'] = timezone.now()
                ciudadano_data['idpersona'] = id_persona_str
                nuevos_ciudadanos.append(ciudadano_data)
            else :
                return Response({'error':"El ciudadano con dni: "+ carnetidentidad +"o expediente: "+idexpediente+ " ya existe"}, status=status.HTTP_400_BAD_REQUEST)
        # Validar los datos recibidos
        serializer = CiudadanoBashSerializer(data=nuevos_ciudadanos, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Crear los ciudadanos en la base de datos
        ciudadanos = serializer.save()
        serializer_response = CiudadanoBashSerializer(ciudadanos, many=True)
        return Response(serializer_response.data, status=status.HTTP_201_CREATED)
#descargar planilla para importar ciudadanos
    @action(detail=False, methods=["get"], name="descargar_csv",url_path='descargar_csv')    
    def descargar_csv(self,request,pk= None):
    # Ruta del archivo CSV en tu proyecto
        ruta_csv = './captura_datos/plantilla_ciudadanos.csv'  # Reemplaza esto con la ruta correcta
    
        # Comprueba si el archivo existe
        if os.path.exists(ruta_csv):
            # Configura la respuesta HTTP para la descarga del archivo CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="planilla_ciudadanos.csv"'
    
            # Lee el contenido del archivo CSV y escribe en la respuesta
            with open(ruta_csv, 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                for row in csv_reader:
                    response.write(','.join(row) + '\n')
    
            return response
        else:
            return HttpResponse("El archivo CSV no se encuentra.", status=404)
#descargar csv con lista de ciudadanos
    @action(detail=False, methods=["get"], name="ciudadanos_entidad_csv",url_path='ciudadanos_entidad_csv')
    def listCiudadanosEntidad(self,request,pk= None):
        
        ciudadanos = Dciudadano.objects.exclude(idpersona__idestado=2)
        response = HttpResponse(content_type ='text/csv')
        response['Content-Disposition'] = f'attachment; filename="ciudadanos_UCI.csv"'

        csv_buffer = io.StringIO()
        csv_writer = csv.DictWriter(csv_buffer, fieldnames=['ID', 'Primer Nombre','Segundo Nombre','Primer Apellido', 'Segundo Apellido',
         'DNI', 'Solapin','Area','Rol Institucional',
         'Fecha de nacimiento','Expediente','Provincia',
         'Municipio','Sexo','Residente'], extrasaction="ignore")
        csv_writer.writeheader()
        csv_writer = csv.writer(response)
        #writer = csv.writer(response)
       
        #writer.writerow()

   
        for ciudadano in ciudadanos:
            fecha_nacimiento = None
            if(ciudadano.fechanacimiento):
             fecha_nacimiento = ciudadano.fechanacimiento.strftime('%d-%m-%Y')
            csv_writer.writerow([ciudadano.idciudadano, ciudadano.primernombre,ciudadano.segundonombre,
            ciudadano.primerapellido, ciudadano.segundoapellido,
             ciudadano.carnetidentidad,ciudadano.solapin,ciudadano.area,ciudadano.roluniversitario,
             fecha_nacimiento,ciudadano.idexpediente,ciudadano.provincia,
             ciudadano.municipio,ciudadano.sexo,ciudadano.residente ])

        return response
#exportar Listar ciudadanos creados por fecha csv
    @action(detail=False, methods=["get"], name="ciudadanos_fecha_csv",url_path='ciudadanos_fecha_csv')
    def listCiudadanosFecha(self,request,pk= None):
        
        ciudadanos = Dciudadano.objects.exclude(idpersona__idestado=2)
        fecha_inicio_str = request.GET.get('fecha_inicio', '')
        fecha_fin_str = request.GET.get('fecha_fin', '')
        #######################
        if fecha_inicio_str and fecha_fin_str:
            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
                fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
            except ValueError:
                return Response({'error': 'Formato de fecha incorrecto. Utilice el formato YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
            # Filtrar ciudadanos por el rango de fechas
            tz = pytz.timezone('UTC')  
            fecha_inicio = timezone.make_aware(fecha_inicio, tz)
            fecha_fin = timezone.make_aware(fecha_fin + timedelta(days=1), tz)
            ciudadanos = ciudadanos.filter(fecha__range=(fecha_inicio, fecha_fin))

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="ciudadanos_creados_por_fecha.csv"'

        
        writer = csv.writer(response)

        
        writer.writerow(['ID', 'Primer Nombre','Segundo Nombre','Primer Apellido', 'Segundo Apellido',
         'DNI', 'Solapin','Area','Rol Institucional',
         'Fecha de nacimiento','Expediente','Provincia','Municipio','Sexo','Residente', 'fecha de creacion'])

 
        for ciudadano in ciudadanos:
            fecha_nacimiento = None
            fecha_creacion = None
            if(ciudadano.fechanacimiento):
             fecha_nacimiento = ciudadano.fechanacimiento.strftime('%d-%m-%Y')
            if(ciudadano.fecha):
             fecha_creacion = ciudadano.fecha.strftime('%d-%m-%Y')
            writer.writerow([ciudadano.idciudadano, ciudadano.primernombre,ciudadano.segundonombre,
            ciudadano.primerapellido, ciudadano.segundoapellido,
             ciudadano.carnetidentidad,ciudadano.solapin,ciudadano.area,ciudadano.roluniversitario,
             fecha_nacimiento,ciudadano.idexpediente,ciudadano.provincia,
             ciudadano.municipio,ciudadano.sexo,ciudadano.residente,fecha_creacion ])

        return response
#exportar Lista de fotos capturadas de ciudadanos por fecha csv
    @action(detail=False, methods=["get"], name="ciudadanos_fecha_foto_csv",url_path='ciudadanos_fecha_foto_csv')
    def listCiudadanos_fotos_Fecha(self,request,pk= None):
        fecha_inicio_str = request.GET.get('fecha_inicio', '')
        fecha_fin_str = request.GET.get('fecha_fin', '')
       
        #######################
        if fecha_inicio_str is None or fecha_fin_str is None:
            return Response({'error': 'Formato de fecha incorrecto. Utilice el formato YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
        
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')
        tz = pytz.timezone('UTC')  
        fecha_inicio = timezone.make_aware(fecha_inicio, tz)
        fecha_fin = timezone.make_aware(fecha_fin + timedelta(days=1), tz)
        ciudadanos_con_imagen = Dimagenfacial.objects.filter(fecha_actualizacion__range=(fecha_inicio, fecha_fin)).values('idciudadano')
        ciudadanos = Dciudadano.objects.filter(idciudadano__in=ciudadanos_con_imagen)
        ciudadanos = ciudadanos.exclude(idpersona__idestado=2)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="ciudadanos_fecha_foto_csv.csv"'


        writer = csv.writer(response)

    
        writer.writerow(['ID', 'Primer Nombre','Segundo Nombre','Primer Apellido', 'Segundo Apellido',
         'DNI', 'Solapin','Area','Rol Institucional',
         'Fecha de nacimiento','Expediente','Provincia','Municipio','Sexo','Residente', 'fecha de imagen'])

 
        for ciudadano in ciudadanos:
            fecha_nacimiento = None
            fecha_creacion = None
            if(ciudadano.fechanacimiento):
             fecha_nacimiento = ciudadano.fechanacimiento.strftime('%d-%m-%Y')
            if(ciudadano.fecha):
             fecha_creacion = ciudadano.fecha.strftime('%d-%m-%Y')
            imagen = Dimagenfacial.objects.filter(idciudadano=ciudadano.idciudadano).first()
            
            fecha_actualizacion_imagen = imagen.fecha_actualizacion.strftime('%d-%m-%Y')
            writer.writerow([ciudadano.idciudadano, ciudadano.primernombre,ciudadano.segundonombre,
            ciudadano.primerapellido, ciudadano.segundoapellido,
             ciudadano.carnetidentidad,ciudadano.solapin,ciudadano.area,ciudadano.roluniversitario,
             fecha_nacimiento,ciudadano.idexpediente,ciudadano.provincia,
             ciudadano.municipio,ciudadano.sexo,ciudadano.residente,fecha_actualizacion_imagen ])  # Ajusta los campos según tus modelos

        return response
#Descargar lista de ciudadanos sin captura de imagenes en csv
    @action(detail=False, methods=["get"], name="ciudadanossinimg_csv",url_path='ciudadanossinimg_csv')
    def ciudadanossinImg(self, request):
        ciudadanos_con_imagen = Dimagenfacial.objects.values_list('idciudadano', flat=True)
        ciudadanos = Dciudadano.objects.exclude(idciudadano__in=ciudadanos_con_imagen)
        ciudadanos = ciudadanos.exclude(idpersona__idestado=2).order_by('fecha')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ciudadanos_sin_fotos.csv"'

        # Creamos el escritor CSV
        writer = csv.writer(response)

 
        writer.writerow(['ID', 'Primer Nombre','Segundo Nombre','Primer Apellido', 'Segundo Apellido',
         'DNI', 'Solapin','Area','Rol Institucional',
         'Fecha de nacimiento','Expediente','Provincia','Municipio','Sexo','Residente'])

  
        for ciudadano in ciudadanos:
            fecha_nacimiento = None
            if(ciudadano.fechanacimiento):
             fecha_nacimiento = ciudadano.fechanacimiento.strftime('%d-%m-%Y')
            writer.writerow([ciudadano.idciudadano, ciudadano.primernombre,ciudadano.segundonombre,
            ciudadano.primerapellido, ciudadano.segundoapellido,
             ciudadano.carnetidentidad,ciudadano.solapin,ciudadano.area,ciudadano.roluniversitario,
             fecha_nacimiento,ciudadano.idexpediente,ciudadano.provincia,
             ciudadano.municipio,ciudadano.sexo,ciudadano.residente ])

        return response

    #Descargar lista de ciudadanos sin captura de huellas en csv
    @action(detail=False, methods=["get"], name="ciudadanossinhuellas_csv",url_path='ciudadanossinhuellas_csv')
    def ciudadanosSinHuellas(self, request):
        ciudadanos_con_huella = Dhuellaciudadano.objects.values_list('idciudadano', flat=True)
        ciudadanos = Dciudadano.objects.exclude(idciudadano__in=ciudadanos_con_huella)
        ciudadanos = ciudadanos.exclude(idpersona__idestado=2).order_by('fecha')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ciudadanos_sin_huella.csv"'

        # Creamos el escritor CSV
        writer = csv.writer(response)

 
        writer.writerow(['ID', 'Primer Nombre','Segundo Nombre','Primer Apellido', 'Segundo Apellido',
         'DNI', 'Solapin','Area','Rol Institucional',
         'Fecha de nacimiento','Expediente','Provincia','Municipio','Sexo','Residente'])

  
        for ciudadano in ciudadanos:
            fecha_nacimiento = None
            if(ciudadano.fechanacimiento):
             fecha_nacimiento = ciudadano.fechanacimiento.strftime('%d-%m-%Y')
            writer.writerow([ciudadano.idciudadano, ciudadano.primernombre,ciudadano.segundonombre,
            ciudadano.primerapellido, ciudadano.segundoapellido,
             ciudadano.carnetidentidad,ciudadano.solapin,ciudadano.area,ciudadano.roluniversitario,
             fecha_nacimiento,ciudadano.idexpediente,ciudadano.provincia,
             ciudadano.municipio,ciudadano.sexo,ciudadano.residente ])

        return response

#Vista de procesamiento de imagen

class CiudadanoImageProcessView(viewsets.ViewSet):
    queryset = Dimagenfacial.objects.all()
    permission_classes = [IsAuthenticated, CustomModelPermissions]
    pagination_class = CiudadanoPagination
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.imgP = ImgProcess()
#Validar Imagen
    @action(detail=False, methods=['post'],name="validateimg",url_path='validateimg')
    def validateImg (self, request, pk =None):
        #instance = self.get_object()
        if 'img' in request.data:
            img_data = request.data.get('img')
            imgBlob = self.imgP.blob_to_image(img_data)
            imgMediaPipe  = self.imgP.blob_ImageMediapipe(imgBlob)
            isValid = self.imgP.validarImg(imgMediaPipe)
            return Response({'data': isValid}, status=status.HTTP_200_OK)
        return Response({'error': f'No se proporcionó una imagen'}, status=status.HTTP_400_BAD_REQUEST)
    def list(self, request, *args, **kwargs):
        return Response({})
