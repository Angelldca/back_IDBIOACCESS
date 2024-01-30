from sklearn.ensemble import VotingClassifier
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
from PIL import Image
from io import BytesIO
import joblib
import cv2
import base64
import pandas as pd
import numpy as np
import imutils
class ImgProcess:
        def __init__(self):
            self.model_path = 'captura_datos/face_landmarker.task'
            self.base_options = python.BaseOptions(model_asset_path=self.model_path)
            self.options = vision.FaceLandmarkerOptions(base_options=self.base_options,
                                                       output_face_blendshapes=True,
                                                       output_facial_transformation_matrixes=True,
                                                       num_faces=1)
            self.detector = vision.FaceLandmarker.create_from_options(self.options)
            self.voting = joblib.load('captura_datos/votin_classifier_model.pkl')

        
        def recortar_imagen(self,blob,ancho):
            img = self.blob_to_image(blob)
            print(type(img), "imagen antes de recortar")
            img_recortada = imutils.resize(img,height=ancho)
            img_data = self.convertir_a_bytea(img_recortada)
            #img_data = base64.b64decode(img_recortada.split(',')[1])
            return img_data

        def convertir_a_bytea(self,img):
            # Crear un objeto BytesIO para almacenar los bytes de la imagen
            imagen_pil = Image.fromarray(img)

            # Guardar la imagen en un búfer de bytes
            buffer = BytesIO()
            imagen_pil.save(buffer, format='JPEG')

            # Obtener los bytes de la imagen
            datos_bytes = buffer.getvalue()
            return datos_bytes
        def getDataFace(self,image_request):
            image = image_request
            # STEP 4: Detect face landmarks from the input image.
            detection_result =  self.detector.detect(image)
            col = {}
            if detection_result.face_landmarks:
                lista_result = detection_result.face_blendshapes[0]
                for i,result in enumerate(lista_result):
                    col[result.category_name] = result.score
            return col

        def validarImg(self,image_request):   #image mediapipe
            #voting = VotingClassifier()
            
            col = self.getDataFace(image_request)
            if bool(col):
                df = pd.DataFrame([col])
                prediccion = self.voting.predict(df)
                print(prediccion[0])
                if prediccion[0] == 0:
                    return False
                else : return True
            else : return False


        def blob_to_image(self,blob):
            # Decodificar el blob a una imagen
            print(type(blob))
            if( type(blob) is str):
                blob = base64.b64decode(blob.split(',')[1])
            img_array = np.frombuffer(blob, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
            # Convertir la imagen a formato RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_rgb = img_rgb.astype(np.uint8)
           
            
        
            return img_rgb

        def blob_ImageMediapipe(self,img_rgb):
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
             # Crear un objeto Image de MediaPipe
            return image

