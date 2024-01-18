from .models import Ciudadano
from rest_framework import viewsets, permissions, generics, status
from .serializers import CiudadanoSerializer
from .imgProcess import ImgProcess
from rest_framework.response import Response
from io import TextIOWrapper
from io import BytesIO
from copy import copy
import csv
import cv2

class CiudadanoViewSet(viewsets.ModelViewSet):
    queryset = Ciudadano.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CiudadanoSerializer
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
'''
    def perform_update(self, serializer):
        #lógica aquí antes de la actualización
        request = self.request
        if 'img' in request.data:
            img_data = request.data.get('img')
            img_data_copia = copy(img_data)
            img_bytes = img_data.read()
            img_data_copia = copy(img_bytes)
            imgMediaPipe = self.imgP.blob_to_image(img_bytes)
            isValid = self.imgP.validarImg(imgMediaPipe)
            if isValid:
                print(isValid)
                serializer.instance.img = img_data_copia
                #super(CiudadanoViewSet, self).perform_update(serializer)
                serializer.save()
                return Response({'detail': 'Actualización exitosa.'}, status=status.HTTP_200_OK)
            else :
                mensaje = "La imagen no cumple con los requisitos específicos."
                return Response({'detail': mensaje}, status=status.HTTP_400_BAD_REQUEST)
'''


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