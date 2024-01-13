from PIL import Image
from io import BytesIO
class ImgProcess:
        # def __init__(self,img):
        #    self.img = img
            
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