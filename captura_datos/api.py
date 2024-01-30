from .models import Ciudadano
from rest_framework import viewsets, permissions, generics, status
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.decorators import action
from django.db import connection
from .serializers import CiudadanoSerializer
from rest_framework.pagination import PageNumberPagination
from .imgProcess import ImgProcess
from rest_framework.response import Response
from io import TextIOWrapper
from io import BytesIO
from copy import copy
import numpy as np
import base64
import csv
import cv2
import os
from django.db.models import Q


class CiudadanoPagination(PageNumberPagination):
     page_size_query_param = 10  # Número de elementos por páginas
     page_size = 5
class CiudadanoViewSet(viewsets.ModelViewSet):
    queryset = Ciudadano.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CiudadanoSerializer
    pagination_class = CiudadanoPagination
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.imgP = ImgProcess()
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if 'img' in request.data:
            img_data = request.data.get('img')
            #imgMediaPipe = self.imgP.blob_to_image(img_data)
            print(type(img_data) , "imagen de la request")
            imagen_recortada = self.imgP.recortar_imagen(img_data,480)
            print(type(imagen_recortada), "imagen despues de recortada")
            instance.img = imagen_recortada
            instance.save()
            serializer = self.get_serializer(instance)
            return Response({'data':serializer.data,'detail': 'Actualización exitosa.'}, status=status.HTTP_200_OK)
        for key, value in request.data.items():
            if key not in ['img'] and value:
                setattr(instance, key, value)
            else: return Response({'detail': 'no se permiten campos vacios.'}, status=status.HTTP_400_BAD_REQUEST)
        instance.save()
        serializer = self.get_serializer(instance)
        return Response({'data': serializer.data,'detail': 'Actualización exitosa.'}, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        atributo_valores = request.GET.dict()
        
        nuevo_diccionario = {clave: valor for clave, valor in atributo_valores.items() if clave != 'page'}
        query = Q()
        for atributo, valor in atributo_valores.items():
            if atributo != 'page_size':
                
                if(atributo == 'nombre_apellidos'):
                    self.queryset = Ciudadano.objects.all()
                    palabras = valor.split()
                    for palabra in palabras:
                        self.queryset = self.queryset.filter(nombre__icontains=palabra) | self.queryset.filter(apellidos__icontains=palabra)
                    page = self.paginate_queryset(self.queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)
                else:
                    query |= Q(**{f'{atributo}': valor})
                    
       
        if nuevo_diccionario:       
            self.queryset = Ciudadano.objects.filter(query)
            
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"], name="ciudadanos_sinImg",url_path='ciudadanos_sin_img')
    def ciudadanos_sinImg(self, request, pk=None):
        self.paginator.page_size = request.GET.get('page_size', self.paginator.page_size)
        self.queryset = Ciudadano.objects.filter(img__isnull=True)
        atributo_valores = request.GET.dict()
        
        nuevo_diccionario = {clave: valor for clave, valor in atributo_valores.items() if clave != 'page'}
        query = Q()
        for atributo, valor in atributo_valores.items():
            if atributo != 'page_size':
                
                if(atributo == 'nombre_apellidos'):
                    self.queryset = Ciudadano.objects.filter(img__isnull=True)
                    palabras = valor.split()
                    for palabra in palabras:
                        self.queryset = self.queryset.filter(nombre__icontains=palabra) | self.queryset.filter(apellidos__icontains=palabra)
                    page = self.paginate_queryset(self.queryset)
                    if page is not None:
                        serializer = self.get_serializer(page, many=True)
                        return self.get_paginated_response(serializer.data)
                else:
                    query |= Q(**{f'{atributo}': valor})
                    
       
        if nuevo_diccionario:       
            self.queryset = Ciudadano.objects.filter(img__isnull=True).filter(query)
            
        page = self.paginate_queryset(self.queryset)
        if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        
        
        
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)


class CiudadanoListCreateView(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        file = request.data.get('planilla_ciudadanos', None)

        if file is None:
            return Response({'error': 'No se proporcionó ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Decodificar el contenido del archivo CSV
            data_file = TextIOWrapper(file.file, encoding=request.encoding)
            reader = csv.DictReader(data_file)
            ciudadanos_data = [row for row in reader]
            
        except Exception as e:
            return Response({'error': f'Error al leer el archivo CSV: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar los datos recibidos
        serializer = CiudadanoSerializer(data=ciudadanos_data, many=True)
        serializer.is_valid(raise_exception=True)

        # Crear los ciudadanos en la base de datos
        ciudadanos = serializer.save()

        # Puedes retornar la lista de ciudadanos creados si es necesario
        serializer_response = CiudadanoSerializer(ciudadanos, many=True)
        return Response(serializer_response.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], name="descargar_csv",url_path='descargar_csv')    
    def descargar_csv(self,request,pk= None):
    # Ruta del archivo CSV en tu proyecto
        ruta_csv = './captura_datos/planilla_ciudadanos.csv'  # Reemplaza esto con la ruta correcta
    
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

class CiudadanoImageProcessView(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    pagination_class = CiudadanoPagination
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.imgP = ImgProcess()

    def post(self, request, *args, **kwargs):
        #instance = self.get_object()
        if 'img' in request.data:
            img_data = request.data.get('img')
            imgBlob = self.imgP.blob_to_image(img_data)
            imgMediaPipe  = self.imgP.blob_ImageMediapipe(imgBlob)
            isValid = self.imgP.validarImg(imgMediaPipe)
            return Response({'data': isValid}, status=status.HTTP_200_OK)
        return Response({'error': f'No se proporcionó una imagen'}, status=status.HTTP_400_BAD_REQUEST)


    def list(self, request):
        ciudadanos = Ciudadano.objects.filter(img__isnull=True)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ciudadanos_sin_fotos.csv"'

        # Creamos el escritor CSV
        writer = csv.writer(response)

        # Escribimos la fila de encabezados
        writer.writerow(['ID', 'Nombre', 'Apellidos',
         'DNI', 'Solapin','Area','Rol Institucional',
         'Fecha de nacimiento','Edad','Expediente',])

        # Escribimos los datos de los ciudadanos
        for ciudadano in ciudadanos:
            writer.writerow([ciudadano.id, ciudadano.nombre, ciudadano.apellidos,
             ciudadano.dni,ciudadano.solapin,ciudadano.area,ciudadano.rol_institucional,
             ciudadano.fecha_nacimiento,ciudadano.edad,ciudadano.expediente ])  # Ajusta los campos según tus modelos

        return response
