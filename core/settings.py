import os
from datetime import timedelta
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
DOMAIN = env('DOMAIN')
SITE_NAME = ('Greenbox')
TOKEN_RENIEC = env('TOKEN_RENIEC')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS_DEV')

CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS_DEV')
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS_DEV')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_debug.log'),  # Ajusta el nombre del archivo según prefieras
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
# Application definition

SITE_ID = 1

DJANGO_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.sites', 'django.contrib.contenttypes',
               'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', ]

PROJECT_APPS = ['apps.user', 'apps.stakeholders', 'apps.category', 'apps.talent_hub', 'apps.logistic',
                'apps.agrisupply', 'apps.planning', 'apps.commercial', 'apps.maintenance', 'apps.production',
                'apps.quality_control', ]

THIRD_PARTY_APPS = ['rest_framework', 'simple_history', 'import_export', 'corsheaders', 'djoser',
                    'rest_framework_simplejwt', 'rest_framework_simplejwt.token_blacklist', 'storages',
                    'django_countries']

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + THIRD_PARTY_APPS

MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware', 'django.middleware.security.SecurityMiddleware',
              'whitenoise.middleware.WhiteNoiseMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware',
              'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware',
              'django.contrib.auth.middleware.AuthenticationMiddleware',
              'django.contrib.messages.middleware.MessageMiddleware',
              'django.middleware.clickjacking.XFrameOptionsMiddleware', ]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [os.path.join(BASE_DIR, 'build')],
              'APP_DIRS': True, 'OPTIONS': {
        'context_processors': ['django.template.context_processors.debug', 'django.template.context_processors.request',
                               'django.contrib.auth.context_processors.auth',
                               'django.contrib.messages.context_processors.messages', ], }, }, ]

WSGI_APPLICATION = 'core.wsgi.application'
# ASGI_APPLICATION = 'core.asgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql_psycopg2', 'NAME': 'backend', 'USER': 'postgres',
# 'PASSWORD': 'postgres', 'HOST': 'db', 'PORT': '5432', }}

DATABASES = {'default': env.db('DATABASE_URL', default='postgres:///e2e_db')}
DATABASES['default']['ATOMIC_REQUESTS'] = True

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher',
                    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
                    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
                    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
                    ]

AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
                            {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
                            {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
                            {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', }, ]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'es-PE'

TIME_ZONE = 'America/Lima'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Rest Framework
REST_FRAMEWORK = {'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
                  'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',)}

AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)

AUTH_USER_MODEL = 'user.UserAccount'

SIMPLE_JWT = {'AUTH_HEADER_TYPES': ('JWT',),
              'TOKEN_OBTAIN_PAIR': 'apps.user.serializers.CustomTokenObtainPairSerializer',
              'ACCESS_TOKEN_LIFETIME': timedelta(days=7), 'REFRESH_TOKEN_LIFETIME': timedelta(days=14),
              'ROTATE_REFRESFH_TOKENS': True, 'BLACKLIST_AFTER_ROTATION': True,
              'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',), }

DJOSER = {'LOGIN_FIELD': 'email', 'PASSWORD_RESET_CONFIRM_URL': 'password/reset/confirm/{uid}/{token}',
          'PASSWORD_RESET_CONFIRM_RETYPE': True, 'SET_PASSWORD_RETYPE': True,

          'SERIALIZERS': {'user_create': 'apps.user.serializers.UserSerializer',
                          'user': 'apps.user.serializers.UserSerializer',
                          'current_user': 'apps.user.serializers.UserSerializer',
                          'user_delete': 'djoser.serializers.UserDeleteSerializer', },
          # 'TEMPLATES': {"password_reset": "email/password_reset.html",}
          }

FILE_UPLOAD_PERMISSIONS = 0o644

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# SECURE_SSL_REDIRECT = False

# SMTP.com configuration
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env('EMAIL_PORT')

# Your SMTP.com sender account credentials
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# Use TLS when connecting to the SMTP server
EMAIL_USE_TLS = True

# Default "from" address for sending emails
DEFAULT_FROM_EMAIL = 'Greenbox <noreply@greenbox.com>'

# Default "from" address for sending emails

TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER')
TWILIO_DESTINATION_PHONE_NUMBER = env('TWILIO_DESTINATION_PHONE_NUMBER')

if not DEBUG:
    CSRF_COOKIE_DOMAIN = os.environ.get('CSRF_COOKIE_DOMAIN_DEPLOY')
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS_DEPLOY')
    CORS_ORIGIN_WHITELIST = env.list('CORS_ALLOWED_ORIGINS_DEPLOY')
    CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS_DEPLOY')

# aws settings


AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')

AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.us-east-2.amazonaws.com'
AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
AWS_DEFAULT_ACL = None

# s3 public media settings

PUBLIC_MEDIA_LOCATION = 'media'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{PUBLIC_MEDIA_LOCATION}/'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'build/static'),)
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
