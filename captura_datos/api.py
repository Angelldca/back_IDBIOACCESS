from .models import Ciudadano
from rest_framework import viewsets, permissions, generics, status
from django.db import connection
from .serializers import CiudadanoSerializer
from rest_framework.pagination import PageNumberPagination
from .imgProcess import ImgProcess
from rest_framework.response import Response
from io import TextIOWrapper
from io import BytesIO
from copy import copy
import csv
import cv2
from django.db.models import Q


class CiudadanoPagination(PageNumberPagination):
     page_size_query_param = 10  # Número de elementos por páginas
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
            img_data_copia = copy(img_data)
            img_bytes = img_data.read()
            img_data_copia = copy(img_bytes)
            imgMediaPipe = self.imgP.blob_to_image(img_bytes)
            isValid = self.imgP.validarImg(imgMediaPipe)
            if isValid:
                print(isValid)
                instance.img = img_data_copia
                #super(CiudadanoViewSet, self).perform_update(serializer)
                instance.save()
                serializer = self.get_serializer(instance)
                return Response({'data':serializer.data,'detail': 'Actualización exitosa.'}, status=status.HTTP_200_OK)
            else :
                mensaje = "La imagen no cumple con los requisitos específicos."
                return Response({'detail': mensaje}, status=status.HTTP_400_BAD_REQUEST)
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