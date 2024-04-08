from rest_framework import routers
from .api import CiudadanoViewCapturaBiograficos, CiudadanosCSVCreateView, CiudadanoImageViewCapturaBiometricos, CiudadanoBashViewCapturaBiograficos


router = routers.DefaultRouter()
router.register('api/ciudadanobash', CiudadanoBashViewCapturaBiograficos, 'ciudadanobash' )
router.register('api/ciudadano', CiudadanoViewCapturaBiograficos, 'ciudadano' )
router.register('api/img', CiudadanoImageViewCapturaBiometricos,'ciudadanos_img' )
router.register('api/ciudadanoscsv', CiudadanosCSVCreateView, 'ciudadanos_csv' )

urlpatterns = router.urls