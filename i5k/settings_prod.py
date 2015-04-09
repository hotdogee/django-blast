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
LOGIN_URL = '/url/to/login'
LOGIN_REDIRECT_URL = '/url/to/home'

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

# social login settings
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'YOURS_KEY'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'YOURS_SECRET'
SOCIAL_AUTH_FACEBOOK_KEY = 'YOURS_KEY'
SOCIAL_AUTH_FACEBOOK_SECRET = 'YOURS_SECRET'

# Email backend
EMAIL_HOST = 'localhost'
EMAIL_PORT = '1025'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
