"""
Django settings for sgea project.
"""

from pathlib import Path
import os
from decouple import config # Importar aqui para uso na seção de e-mail

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings 
# --------------------------------------------------------------------------

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-jxmcqg)h2tf#o3nbp^^!vla_st14j$uk!sd+%*whxiy)i1z_xa'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition
# --------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'sgea_app',
    'rest_framework',
    'rest_framework.authtoken'
    # Incluir 'api' se você criou o app, mas não está listado aqui.
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sgea.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'sgea.wsgi.application'


# Database
# --------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation & User Model
# --------------------------------------------------------------------------

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

# Configuração do Modelo de Usuário Customizado
AUTH_USER_MODEL = 'sgea_app.Usuario'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Internationalization, Time Zones, e Localização
# --------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Habilita o uso de formatos de data/hora localizados nos formulários
USE_L10N = True 
DATE_INPUT_FORMATS = [
    '%d/%m/%Y', # DD/MM/AAAA (padrão brasileiro)
    '%Y-%m-%d', # AAAA-MM-DD (padrão ISO)
]


# Static Files (CSS, JS) e Media Files (Uploads)
# --------------------------------------------------------------------------

STATIC_URL = 'static/'

# Configurações para Upload de Mídia (Imagens do Banner)
MEDIA_URL = '/media/'

# ** CORREÇÃO DE PATHLIB **
# Usamos o objeto BASE_DIR (que é um Pathlib.Path) e o operador /
MEDIA_ROOT = BASE_DIR / 'media'


# Authentication & Redirection
# --------------------------------------------------------------------------

LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'


# REST Framework Configuration (API)
# --------------------------------------------------------------------------

REST_FRAMEWORK = {
    # Autenticação obrigatória
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Configuração do Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'eventos': '20/day',
        'inscricoes': '50/day',
    },
}

# E-mail Configuration
# --------------------------------------------------------------------------
# E-mail inventado para a funcionalidade

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "nao-responder@sgea.com"