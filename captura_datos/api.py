from .models import Ciudadano
from rest_framework import viewsets, permissions
from .serializers import CiudadanoSerializer
from .imgProcess import ImgProcess
class CiudadanoViewSet(viewsets.ModelViewSet):
    queryset = Ciudadano.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = CiudadanoSerializer




    
    def perform_update(self, serializer):
        #lógica aquí antes de la actualización
        request = self.request

        # Acceder a los datos de la imagen
        img_data = request.data.get('img')
        #img_proces = ImgProcess.recortar_imagen(img_data,600,600)
        
        # Leer los bytes de la imagen
        img_bytes = img_data.read()   #ImgProcess.convertir_a_bytea(img_proces)    #img_proces.read()

        # Actualizar el campo 'img' en el objeto Ciudadano con los bytes de la imagen
        serializer.instance.img = img_bytes
        # Llamada al método perform_update del padre para realizar la actualización
        super(CiudadanoViewSet, self).perform_update(serializer)