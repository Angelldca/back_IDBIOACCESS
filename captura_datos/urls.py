from rest_framework import routers
from .api import CiudadanoViewSet, CiudadanoListCreateView


router = routers.DefaultRouter()
router.register('api/ciudadano', CiudadanoViewSet, 'ciudadano' )
router.register('api/ciudadanos', CiudadanoListCreateView, 'ciudadanos_list' )

urlpatterns = router.urls