from pathlib import Path
import dj_database_url
import json
import os


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = not not os.getenv('DEBUG')
ALLOWED_HOSTS = ['*']
DOMAIN = os.getenv('DOMAIN', 'morningcreative.co')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sitemaps',
    'taggit',
    'markdownx',
    'easy_thumbnails',
    'bootstrap5',
    'anymail',
    'watson',
    'django_rq',
    'morningcreative.seo',
    'morningcreative.theme',
    'morningcreative.miditags',
    'morningcreative.oembed',
    'morningcreative.mail',
    'morningcreative.analytics',
    'morningcreative.monetisation',
    'morningcreative.newsletter',
    'morningcreative.podcast',
    'morningcreative.prompts',
    'morningcreative.pages'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'morningcreative.newsletter.middleware.subscriber_middleware'
]

ROOT_URLCONF = 'morningcreative.urls'
CORS_ORIGIN_ALLOW_ALL = True
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL
    }
}

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
                'morningcreative.context_processors.main'
            ]
        }
    }
]

ASGI_APPLICATION = 'morningcreative.asgi.application'
WSGI_APPLICATION = 'morningcreative.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///%s' % os.path.join(BASE_DIR, 'db.sqlite')
    )
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'
    }
}

if not DEBUG:
    CACHES['default'] = {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': '127.0.0.1:11211'
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'  # NOQA
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'  # NOQA
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'  # NOQA
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'  # NOQA
    }
]


LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MARKDOWN_STYLES = {
    'default': {
        'extensions': (
            'markdown.extensions.smarty',
            'fenced_code',
            'codehilite'
        )
    }
}

STATIC_URL = os.getenv('STATIC_URL') or '/static/'
STATIC_ROOT = os.getenv('STATIC_ROOT') or os.path.join(BASE_DIR, 'static')
MEDIA_URL = os.getenv('MEDIA_URL') or '/media/'
MEDIA_ROOT = os.getenv('MEDIA_ROOT') or os.path.join(BASE_DIR, 'media')
AUDIO_ELEMENETS_ROOT = os.getenv('AUDIO_ELEMENETS_ROOT') or os.path.join(BASE_DIR, 'audio')  # NOQA

if not DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'  # NOQA
    STATIC_URL = os.getenv('STATIC_URL') or '/static/'
else:
    STATICFILES_STORAGE = 'morningcreative.storage.LocalNetworkStorage'
    STATIC_URL = '/static/'

COUNTRIES = json.load(
    open(
        os.path.join(os.path.dirname(__file__), 'fixtures', 'countries.json'),
        'rb'
    )
)

MARKDOWNX_URLS_PATH = '/admin/markdownx/markdownify/'
MARKDOWNX_UPLOAD_URLS_PATH = '/admin/markdownx/upload/'
MARKDOWNX_MARKDOWN_EXTENSIONS = MARKDOWN_STYLES['default']['extensions']
MARKDOWNX_IMAGE_MAX_SIZE = {
    'size': (1418, 0),
    'quality': 90
}

MARKDOWNX_MEDIA_PATH = 'uploads/'

ANYMAIL = {
    'MAILERSEND_API_TOKEN': os.getenv('MAILERSEND_API_KEY'),
    'MAILERSEND_SENDER_DOMAIN': 'out.hellosteadman.com'
}

EMAIL_BACKEND = 'anymail.backends.mailersend.EmailBackend'
DEFAULT_FROM_NAME = 'Mark Steadman'
DEFAULT_FROM_EMAIL = 'noreply@out.hellosteadman.com'

IPINFO_API_URL = 'https://ipinfo.io/%s'
IPINFO_API_KEY = os.getenv('IPINFO_API_KEY')
SCREENSHOT_API_KEY = os.getenv('SCREENSHOT_API_KEY')
