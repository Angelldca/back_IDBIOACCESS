from rest_framework.authentication import BaseAuthentication
from django_cas_ng.backends import CASBackend

class CASAuthentication(BaseAuthentication):
    def authenticate(self, request):
        cas_backend = CASBackend()
        user = cas_backend.authenticate(request)
        if user is None:
            return None
        return (user, None)