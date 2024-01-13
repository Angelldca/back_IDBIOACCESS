from rest_framework import routers
from .api import CiudadanoViewSet


router = routers.DefaultRouter()
router.register('api/ciudadano', CiudadanoViewSet, 'ciudadano' )
router.register('api/img', CiudadanoViewSet, 'ciudadano' )

urlpatterns = router.urls