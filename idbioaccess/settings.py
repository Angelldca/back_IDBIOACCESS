"""
Django settings for idbioaccess project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#SECRET_KEY = 'django-insecure-^bw)!@6*)3tkzgo9y^#!!hf_xx8k!+zulz^z#ue(xswp86%6!%'
SECRET_KEY = os.environ.get('SECRET_KEY', default='your secret key')

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
DEBUG = 'RENDER' not in os.environ

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition

INSTALLED_APPS = [
    #'CORS_ORIGIN_ALLOW_ALL = True',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'captura_datos',
    'rest_framework',
    'corsheaders',
    'django_cas_ng',
    'django_extensions',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_cas_ng.middleware.CASMiddleware'
]

ROOT_URLCONF = 'idbioaccess.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'idbioaccess.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        # Replace this value with your local database's connection string.
        default='postgresql://postgres:Angel4167*@localhost:5432/db_prueba',
        conn_max_age=600
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-es'

#TIME_ZONE = 'UTC'
TIME_ZONE = 'America/Havana'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'
if not DEBUG:
    # Tell Django to copy static assets into a path called `staticfiles` (this is specific to Render)
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    # Enable the WhiteNoise storage backend, which compresses static files to reduce disk use
    # and renames the files with unique names for each version to support long-term caching
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


ALLOWED_HOSTS = ['127.0.0.1',
 'localhost','192.168.230.177', '192.168.230.207',
  '192.168.230.207','192.168.230.*',
 '10.140.253.208']
CORS_ALLOWED_ORIGINS = [
    "https://api.domain.com",          # Dominio principal
    "http://localhost:8080",           # Localhost con puerto 8080
    "http://127.0.0.1:8000",           # Localhost con puerto 8000
    "http://192.168.137.60:8000",      # IP del servidor en red local
    "https://192.168.137.60:8000",     # Acceso con HTTPS en red local (si se usa HTTPS)
    "http://192.168.137.60:4200",      # Angular en red local puerto 4200
    "http://0.0.0.0:8000",             # Todos los hosts en el puerto 8000 para desarrollo
    "https://0.0.0.0:8000",
       # servidor Django
    'https://192.168.230.*',
]
CORS_ORIGIN_ALLOW_ALL = True



CORS_ALLOW_HEADERS = [
'accept',
'accept-encoding',
'authorization',
'content-type',
'dnt',
'origin',
'user-agent',
'x-csrftoken',
'x-requested-with',
]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,  # Número de elementos por página
    'DEFAULT_AUTHENTICATION_CLASSES': (    
        
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    
}
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
    
)

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),  # Tiempo de vida del token de acceso
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),     # Tiempo de vida del token de actualización
}

CAS_SERVER_URL = 'https://soa-cas.uci.cu/cas/'
CAS_VERSION = '3'
CAS_REDIRECT_URL =  'http://localhost:4200/cas'
CAS_LOGOUT_COMPLETELY = True
CAS_IGNORE_REFERER = True
CAS_APPLY_ATTRIBUTES_TO_USER=True
CAS_CREATE_USER=True
CAS_LOCAL_NAME_FIELD =True
CAS_ALLOW_ALL_USERS= True
CAS_ADMIN_PREFIX = 'False'
###localhost:8000/accounts/login

