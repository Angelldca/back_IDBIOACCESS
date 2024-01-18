from sklearn.ensemble import VotingClassifier
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
from PIL import Image
from io import BytesIO
import joblib
import cv2
import pandas as pd
import numpy as np
class ImgProcess:
        def __init__(self):
            self.model_path = 'captura_datos/face_landmarker.task'
            self.base_options = python.BaseOptions(model_asset_path=self.model_path)
            self.options = vision.FaceLandmarkerOptions(base_options=self.base_options,
                                                       output_face_blendshapes=True,
                                                       output_facial_transformation_matrixes=True,
                                                       num_faces=1)
            self.detector = vision.FaceLandmarker.create_from_options(self.options)


        def recortar_imagen(imagen, ancho_deseado, largo_deseado):
            # Abrir la imagen utilizando Pillow
            img = Image.open(imagen)
    
            # Calcular las dimensiones del recorte
            ancho_actual, largo_actual = img.size
            nuevo_ancho = min(ancho_actual, ancho_deseado)
            nuevo_largo = min(largo_actual, largo_deseado)
    
            # Calcular las coordenadas para el recorte centrado
            izquierda = (ancho_actual - nuevo_ancho) / 2
            arriba = (largo_actual - nuevo_largo) / 2
            derecha = (ancho_actual + nuevo_ancho) / 2
            abajo = (largo_actual + nuevo_largo) / 2
    
            # Realizar el recorte
            img_recortada = img.crop((izquierda, arriba, derecha, abajo))
    
            # Guardar o procesar la imagen recortada según sea necesario
    
            return img_recortada

        def convertir_a_bytea(imagen_pillow):
            # Crear un objeto BytesIO para almacenar los bytes de la imagen
            stream = BytesIO()
            
            # Guardar la imagen de Pillow en el stream
            imagen_pillow.save(stream, format='PNG')  # Ajusta el formato según tu necesidad
        
            # Obtener los bytes de la imagen
            bytes_imagen = stream.getvalue()
        
            return bytes_imagen
        def getDataFace(self,image_request):
            # STEP 3: Load the input image.
            image = image_request  #mp.Image.create_from_file(image_request) #"test/v4.jpg"
            
            # STEP 4: Detect face landmarks from the input image.
            detection_result =  self.detector.detect(image)
            col = {}
            if detection_result.face_landmarks:
                lista_result = detection_result.face_blendshapes[0]
                for i,result in enumerate(lista_result):
                    col[result.category_name] = result.score
            return col

        def validarImg(self,image_request):
            #voting = VotingClassifier()
            voting = joblib.load('captura_datos/votin_classifier_model.pkl')
            col = self.getDataFace(image_request)
            if bool(col):
                df = pd.DataFrame([col])
                prediccion = voting.predict(df)
                print(prediccion[0])
                if prediccion[0] == 0:
                    return False
                else : return True
            else : return False


        def blob_to_image(self,blob):
            
            
            # Decodificar el blob a una imagen
            img_array = np.frombuffer(blob, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
            # Convertir la imagen a formato RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_rgb = img_rgb.astype(np.uint8)
            # Crear un objeto Image de MediaPipe
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
            return image
