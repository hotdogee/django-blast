DEBUG = True
TEMPLATE_DEBUG = DEBUG

USE_CACHE = True

with open('/path/to/secret_key.txt') as f:
    SECRET_KEY = f.read().strip()

ALLOWED_HOSTS = (
    '.example.com',
)

MEDIA_URL = '/url/to/media/'
STATIC_URL = '/url/to/static/'
LOGIN_URL = '/url/to/login/'
LOGIN_REDIRECT_URL = '/url/to/user/'

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': '',
    'USER': '',
    'PASSWORD': '',
    'HOST': '127.0.0.1',
    'PORT': '5432',
    }
}
