from os import getenv as os_getenv
from pathlib import Path

from django.urls import reverse_lazy


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = os_getenv('DJANGO_SECRET_KEY', 'secret_key')

DEBUG = os_getenv('DJANGO_DEBUG', '1') != '0'

ALLOWED_HOSTS = os_getenv('DJANGO_ALLOWED_HOSTS', '*').split()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cleanup.apps.CleanupConfig',
    'main',
    'user',
    'core'
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

ROOT_URLCONF = 'delovar.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.functions.year'
            ],
        },
    },
]

ASGI_APPLICATION = 'delovar.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': os_getenv('DATABASE_ENGINE'),
        'NAME': os_getenv('DATABASE_NAME'),
        'USER': os_getenv('DATABASE_USER'),
        'PASSWORD': os_getenv('DATABASE_PASSWORD'),
        'HOST': os_getenv('DATABASE_HOST'),
        'PORT': os_getenv('DATABASE_PORT'),
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{os_getenv('REDIS_HOST')}:{os_getenv('REDIS_PORT')}/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


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


LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_ROOT = BASE_DIR / '..' / 'static'
STATIC_URL = '/static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / '..' / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = reverse_lazy('main:index')
AUTH_USER_MODEL = 'user.CustomUser'


SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'session'
SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_SAVE_EVERY_REQUEST = True  # Обновление сессии при каждом запросе
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Сессия сохраняется после закрытия браузера


FILES_NAME = MEDIA_ROOT / 'files'
CLEANUP_KEEP_CLEAN = 90


API_ACCESS_TOKEN = os_getenv('API_ACCESS_TOKEN')
API_URL = os_getenv('API_URL', 'http://example.com')

API_URL_UPLOAD = API_URL + 'upload/'
API_URL_DOWNLOAD = API_URL + 'download/'
API_URL_CHECK = API_URL + 'check/'
API_URL_ERROR_LIST = API_URL + 'error_list/'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / '.log',
        },
        'stream': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'stream'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
