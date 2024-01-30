from rest_framework import routers
from .api import CiudadanoViewSet, CiudadanoListCreateView, CiudadanoImageProcessView


router = routers.DefaultRouter()
router.register('api/ciudadano', CiudadanoViewSet, 'ciudadano' )
router.register('api/ciudadanos', CiudadanoListCreateView, 'ciudadanos_list' )
router.register('api/img', CiudadanoImageProcessView,'ciudadanos_img' )

urlpatterns = router.urls