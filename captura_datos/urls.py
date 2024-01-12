from rest_framework import routers
from .api import CiudadanoViewSet


router = routers.DefaultRouter()
router.register('api/ciudadano', CiudadanoViewSet, 'ciudadano' )

urlpatterns = router.urls