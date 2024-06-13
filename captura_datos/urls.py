from rest_framework import routers
from django.urls import path
from .api import CiudadanoViewCapturaBiograficos,CiudadanoImageProcessView, CiudadanosCSVCreateView, CiudadanoImageViewCapturaBiometricos, CiudadanoBashViewCapturaBiograficos
from .api_seguridad import PermissionViewSet, GroupViewSet, UserViewSet,LogEntryViewSet
from .api_gestion import CiudadanosSinSolapinList, CiudadanosConSolapinList, CiudadanosSolapinDesactivadoList, SolapinViewSet, TipoSolapinViewSet, CausaAnulacionViewSet, RegistroPagoViewSet
from .api_gestion import CiudadanoSolapinHistViewSet, NewSolapinHistViewSet, OperacionSolapinViewSet, TipoOperacionSolapinViewSet

router = routers.DefaultRouter()
router.register('api/ciudadanobash', CiudadanoBashViewCapturaBiograficos, 'ciudadanobash' )
router.register('api/ciudadano', CiudadanoViewCapturaBiograficos, 'ciudadano' )
router.register('api/img', CiudadanoImageViewCapturaBiometricos,'ciudadanos_img' )
router.register('api/img/validate', CiudadanoImageProcessView,'validate_img' )
router.register('api/ciudadanoscsv', CiudadanosCSVCreateView, 'ciudadanos_csv' )
router.register('api/seguridad/permiso', PermissionViewSet, 'permisos' )
router.register('api/seguridad/rol', GroupViewSet, 'roles' )
router.register('api/seguridad/user', UserViewSet, 'user' )
router.register('api/seguridad/trazas', LogEntryViewSet, 'trazas' )
router.register('api/ciudadanoss', CiudadanosSinSolapinList, 'ciudadanoss')
router.register('api/ciudadanocs', CiudadanosConSolapinList, 'ciudadanocs')
router.register('api/ciudadanoas', CiudadanosSolapinDesactivadoList, 'ciudadanoas')
router.register('api/solapin', SolapinViewSet, 'solapin')
router.register('api/tiposolapin', TipoSolapinViewSet, 'tiposolapin')
router.register('api/causaanulacion', CausaAnulacionViewSet, 'causaanulacion')
router.register('api/registropago', RegistroPagoViewSet, 'registropago')
router.register('api/ciudadanosolapinhist', CiudadanoSolapinHistViewSet, 'ciudadanosolapinhist')
router.register('api/newsolapinhist', NewSolapinHistViewSet, 'newsolapinhist')
router.register('api/operacionsolapin', OperacionSolapinViewSet, 'operacionsolapin')
router.register('api/tipooperacionsolapin', TipoOperacionSolapinViewSet, 'tipooperacionsolapin')

#router.register('api/segiridad/login', LoginAPIView, basename = 'login')



urlpatterns = router.urls