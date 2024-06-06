from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Ciudadano
from .api import CiudadanoViewSet, CiudadanoListCreateView, CiudadanoImageProcessView
import base64

class ciudadanoTest(TestCase):
    def setUp(self):
        # Configuración inicial para las pruebas
        self.client = APIClient()
        self.ciudadano_url = reverse('ciudadano-list')
        self.ciudadano_data = {  
            "id": 17,
            "nombre": "Maibel",
            "apellidos": "Izquierdo",
            "dni": "85441203076",
            "solapin": "E547664",
            "expediente": 545431,
            "fecha_nacimiento": "1998-11-20",
            "edad": 64,
            "rol_institucional": "Trabajador",
            "area": "Comedor",
            "img": 'null',
            "entidad": "UCI",
            "created_At": "2024-01-20"}
        self.ciudadanoVacio_data = {  
            "id":"" ,
            "nombre": "",
            "apellidos": "",
            "dni": "",
            "solapin": "",
            "expediente":"" ,
            "fecha_nacimiento": "",
            "edad": "",
            "rol_institucional": "Trabajador",
            "area": "Comedor",
            "img": 'null',
            "entidad": "UCI",
            "created_At": "2024-01-20"}
    def test_actualizarImg_ciudadano(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = response.data['id']

        # Actualizar img
        updated_data = {'img': base64.b64encode(b'\x89JPEG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x01\x00\x00\x00\xc2\x04\xdb\x8e\x00\x00\x00\x0aIDATx\x9c\xed\xcd\xbd\x6b\x13\x41\x10\x87\xdf\xd1\xdd\xfd\xb5\xff\xbe\x8dR\xabx0\x00\x00\x00\x00IEND\xaeB`\x82')}
        response = self.client.put(reverse('ciudadano-list', args=[ciudadano_id]), updated_data, format='json')

        #self.assertEqual(response.status_code, status.HTTP_200)   
    def test_actualizarCamposValidos_ciudadano(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = response.data['id']
        updated_data = {'nombre':"Ciudadano Actualizado",'apellidos':"de la Caridad",'dni':98112345688}
        response = self.client.put(self.ciudadano_url+str(ciudadano_id)+'/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Ciudadano.objects.get(id=ciudadano_id).nombre, 'Ciudadano Actualizado')

    def test_actualizarCamposVacios_ciudadano(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = response.data['id']
        updated_data = {'nombre':None,'apellidos':"de la Caridad",'dni':''}
        response = self.client.put(self.ciudadano_url+str(ciudadano_id)+'/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizarCamposInvalidos_ciudadano(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = response.data['id']
        updated_data = {'nombre':'angel','apellidos':3434,'dni':'fdfdfdfdfdui'}
        response = self.client.put(self.ciudadano_url+str(ciudadano_id)+'/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizarSinDatos_ciudadano(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = response.data['id']
        updated_data = {}
        response = self.client.put(self.ciudadano_url+str(ciudadano_id)+'/', updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    def test_crear_ciudadano(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_crear_ciudadanoExistente(self):
        
        self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')

    def test_crear_ciudadano_campos_vacios(self):

        response = self.client.post(self.ciudadano_url, self.ciudadanoVacio_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_eliminar_ciudadanoValido(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = response.data['id']
        

        # Elimina el ciudadano
        response = self.client.delete(self.ciudadano_url+str(ciudadano_id)+'/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Ciudadano.objects.count(), 0)

    def test_eliminar_ciudadanoInexistente(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = 5
        

        # Elimina el ciudadano
        response = self.client.delete(self.ciudadano_url+str(ciudadano_id)+'/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_ciudadanoSinImg(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_validarImg(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_list_Fecha(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_historial_Img(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_importar_ciudadano(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_descargar_planilla(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')


    def test_eliminar_ciudadanoInexistente(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = 5
        

        # Elimina el ciudadano
        response = self.client.delete(self.ciudadano_url+str(ciudadano_id)+'/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_ciudadanoSinImg(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_validarImg(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_list_Fecha(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_historial_Img(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_importar_ciudadano(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_descargar_planilla(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')


    def test_eliminar_ciudadanoInexistente1(self):
        # Crea un ciudadano
        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        ciudadano_id = 5
        

        # Elimina el ciudadano
        response = self.client.delete(self.ciudadano_url+str(ciudadano_id)+'/')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_ciudadanoSinImg1(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_validarImg1(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_list_Fecha1(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_historial_Img1(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_importar_ciudadano1(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')
    def test_descargar_planilla1(self):

        response = self.client.post(self.ciudadano_url, self.ciudadano_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ciudadano.objects.count(), 1)
        self.assertEqual(Ciudadano.objects.get().nombre, 'Maibel')