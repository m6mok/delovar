from pathlib import Path

from django.urls import reverse_lazy


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-n07hbkldddpvblp8=4#e8o2r6#gwxq%g&hohmx0c^do96jo6ag'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main.apps.MainConfig',
    'user.apps.UserConfig'
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

WSGI_APPLICATION = 'delovar.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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

STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = reverse_lazy('main:index')

AUTH_USER_MODEL = 'user.CustomUser'


SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_NAME = 'session'

SESSION_COOKIE_AGE = 86400  # 1 day

SESSION_SAVE_EVERY_REQUEST = True  # Обновление сессии при каждом запросе

SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Сессия сохраняется после закрытия браузера


FILES_NAME = MEDIA_ROOT / 'files'


API_ACCESS_TOKEN = 'bw2dnkohQJp3ib-GoefPi9/deczuxPPYDrIb85g0uxmpy7al4odokpvHi63OAoWkGCGKbzjp/Gm=BlheX7Y2eruwLOftp4QrMpvsfLfF7l7dJ9GWCLNZBlFi=uHaeFQqHsrgG6nEA8u85E6gKGr7hEswfmWhdGO=Ct!hgm/g1-ANK!v0XCu/TpimRo=S54YFjWaum5?586BHd9T/OhvV3Tym01Ln5HhSmAQjRMYlBdjy=Fo1FHIyFqNEhJlD39xw'
API_URL = 'http://195.140.146.223:5000/api/v1/'
API_URL_DOCUMENT = API_URL + 'document/'
API_URL_CHECK = API_URL + 'check/'

API_DEFAULT_SETTINGS = {
    "timeout_page": 5,
    "timing_page": 5,
    "timeout_movement": .5,
    "timing_movement": .5
}
API_MOVEMENT_RECEIPT = {'movements': 'receipt'}
API_MOVEMENT_STATEMENT_DISTRICT = {'movements': 'statement_district'}
API_MOVEMENT_STATEMENT_MAGISTRATE = {'movements': 'statement_magistrate'}
API_MOVEMENT_LAWSUIT = {'movements': 'lawsuit'}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
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
