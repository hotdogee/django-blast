# Django settings for i5k project.
#
# Every deployment-specific value (secret key, database, broker, OAuth keys,
# e-mail, ...) is read from environment variables, optionally loaded from a
# ``.env`` file in the project root. See README.md ("Configuration") and
# .env.example for the full list.
import os
import socket

import environ
from celery.schedules import crontab
from django.core.exceptions import ImproperlyConfigured
from kombu import Exchange, Queue

PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

env = environ.Env()
if os.path.isfile(os.path.join(PROJECT_ROOT, '.env')):
    environ.Env.read_env(os.path.join(PROJECT_ROOT, '.env'))

DEBUG = env.bool('DJANGO_DEBUG', default=False)

# Make this unique, and don't share it with anybody.
SECRET_KEY = env('DJANGO_SECRET_KEY', default='')
# or read it from a file, e.g. the one the docker image generates
SECRET_KEY_FILE = env('DJANGO_SECRET_KEY_FILE', default='')
if not SECRET_KEY and SECRET_KEY_FILE and os.path.isfile(SECRET_KEY_FILE):
    with open(SECRET_KEY_FILE) as f:
        SECRET_KEY = f.read().strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-development-only-key'
    else:
        raise ImproperlyConfigured('Set the DJANGO_SECRET_KEY environment variable, or DJANGO_SECRET_KEY_FILE to a file containing '
                                   'the key (or DJANGO_DEBUG=1 for development).')

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '[::1]'])
CSRF_TRUSTED_ORIGINS = env.list('DJANGO_CSRF_TRUSTED_ORIGINS', default=[])

# template settings
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'app.context_processors.is_login_enabled',
                'app.context_processors.is_analytics_enabled',
            ],
        },
    },
]

ADMINS = [('Admin', email) for email in env.list('DJANGO_ADMINS', default=[])]

MANAGERS = ADMINS

# DATABASE_URL examples:
#   postgres://django:password@127.0.0.1:5432/django_i5k
#   sqlite:////absolute/path/to/db.sqlite3
# PostgreSQL is recommended (the "data" app uses hstore fields).
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///' + os.path.join(PROJECT_ROOT, 'db.sqlite3').replace('\\', '/')),
}
DATABASES['default']['CONN_MAX_AGE'] = env.int('DATABASE_CONN_MAX_AGE', default=0)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# URL names or paths
LOGIN_URL = env('DJANGO_LOGIN_URL', default='login')
LOGIN_REDIRECT_URL = env('DJANGO_LOGIN_REDIRECT_URL', default='dashboard')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = env('DJANGO_TIME_ZONE', default='America/New_York')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files
# (BLAST databases under blast/db/ and BLAST results under blast/task/).
MEDIA_ROOT = env('DJANGO_MEDIA_ROOT', default=os.path.join(PROJECT_ROOT, 'media')).replace('\\', '/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
MEDIA_URL = env('DJANGO_MEDIA_URL', default='/media/')

# Serve MEDIA_ROOT through Django even when DEBUG is off. Handy for the docker
# setup and small installations; large sites should let the web server do it.
SERVE_MEDIA = env.bool('DJANGO_SERVE_MEDIA', default=DEBUG)

# Absolute path to the directory static files should be collected to.
STATIC_ROOT = env('DJANGO_STATIC_ROOT', default=os.path.join(PROJECT_ROOT, 'static')).replace('\\', '/')

# URL prefix for static files.
STATIC_URL = env('DJANGO_STATIC_URL', default='/static/')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
)

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': env('DJANGO_STATICFILES_STORAGE', default='whitenoise.storage.CompressedStaticFilesStorage'),
    },
}

FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'app.middleware.SocialAuthExceptionMiddleware',
    # AxesMiddleware should be the last middleware in the list.
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'i5k.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'i5k.wsgi.application'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'axes',
    'rest_framework',
    'django_filters',
    'drf_spectacular',
    'app',
    'blast',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'social_django',
    'captcha',
    'dashboard',
    'webapollo',
    'proxy',
    'data',
]

# Security settings, mostly relevant when served over HTTPS behind a proxy.
# `python manage.py check --deploy` reports what is still missing.
if env.bool('DJANGO_SECURE_PROXY_SSL_HEADER', default=False):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=False)
SESSION_COOKIE_SECURE = env.bool('DJANGO_SESSION_COOKIE_SECURE', default=False)
CSRF_COOKIE_SECURE = env.bool('DJANGO_CSRF_COOKIE_SECURE', default=False)
SECURE_HSTS_SECONDS = env.int('DJANGO_SECURE_HSTS_SECONDS', default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', default=False)
SECURE_HSTS_PRELOAD = env.bool('DJANGO_SECURE_HSTS_PRELOAD', default=False)
# The BLAST page used to be embedded in other pages of the i5k site.
X_FRAME_OPTIONS = env('DJANGO_X_FRAME_OPTIONS', default='SAMEORIGIN')

# Media path fields (BLAST database FASTA files, data files)
MEDIA_FILE_EXTENSIONS = {
    'FASTA': ['.fa', '.faa', '.fna', '.fasta', '.cds', '.pep'],
    'FASTQ': ['.fq', '.fastq'],
    'SAM': ['.sam', '.bam'],
    'WIG': ['.wig', '.bw', '.bigwig'],
    'JSON': ['.json'],
    'GFF': ['.gff', '.gff3'],
}
MEDIA_UPLOAD_MAX_SIZE = env.int('DJANGO_MEDIA_UPLOAD_MAX_SIZE', default=10737418240)  # 10GB

# Logging: errors are mailed to ADMINS when DEBUG=False, and everything at
# INFO and above from the BLAST app goes to the console (docker logs).
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'root': {
        'handlers': ['console'],
        'level': env('DJANGO_LOG_LEVEL', default='WARNING'),
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'blast': {
            'level': 'INFO',
        },
    }
}

# Celery Settings (read by i5k/celery.py with the CELERY_ namespace)
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='amqp://')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=None)
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_TASK_ALWAYS_EAGER', default=False)
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_DEFAULT_QUEUE = 'i5k'
CELERY_TASK_DEFAULT_EXCHANGE = 'i5k'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'i5k'
CELERY_TASK_QUEUES = (
    Queue('i5k', Exchange('i5k'), routing_key='i5k'),
)
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_WORKER_DISABLE_RATE_LIMITS = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BEAT_SCHEDULE = {
    'remove-expired-blast-files': {
        'task': 'blast.tasks.remove_files',
        'schedule': crontab(hour='0', minute='10'),  # daily, shortly after midnight
    },
}

# BLAST+
# Directory containing the BLAST+ executables. When empty, executables are
# looked up on PATH, falling back to the copies bundled in blast/bin_linux or
# blast/bin_win.
BLAST_BIN_DIR = env('BLAST_BIN_DIR', default='')
BLAST_NUM_THREADS = env.int('BLAST_NUM_THREADS', default=4)
# Results older than this are reported as expired.
BLAST_RESULT_RETENTION_DAYS = env.int('BLAST_RESULT_RETENTION_DAYS', default=7)
# Let the daily celery beat job delete expired result directories.
BLAST_REMOVE_EXPIRED_FILES = env.bool('BLAST_REMOVE_EXPIRED_FILES', default=False)

# Shows the position of a job in the queue on the results page. Needs a cache
# shared by the web and worker processes (memcached or redis).
USE_CACHE = env.bool('USE_CACHE', default=False)
# CACHE_URL examples: pymemcache://127.0.0.1:11211, redis://127.0.0.1:6379/1
CACHES = {
    'default': env.cache('CACHE_URL', default='locmemcache://'),
}
CACHES['default'].setdefault('TIMEOUT', None)  # never expire

# django-axes
AXES_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = 1  # 1 hour
AXES_LOCKOUT_PARAMETERS = [['ip_address', 'user_agent']]
AXES_LOCKOUT_TEMPLATE = 'app/login_lockout.html'
AXES_VERBOSE = True

# rest_framework
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# drf-spectacular (OpenAPI schema and Swagger UI at /blast/api-docs/)
SPECTACULAR_SETTINGS = {
    'TITLE': 'i5k BLAST API',
    'DESCRIPTION': 'Read-only access to organisms, BLAST databases, sequences and BLAST tasks.',
    'VERSION': '2.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# social login settings
AUTHENTICATION_BACKENDS = (
    'axes.backends.AxesStandaloneBackend',
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details'
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY', default='')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env('SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET', default='')
SOCIAL_AUTH_FACEBOOK_KEY = env('SOCIAL_AUTH_FACEBOOK_KEY', default='')
SOCIAL_AUTH_FACEBOOK_SECRET = env('SOCIAL_AUTH_FACEBOOK_SECRET', default='')
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

# captcha
CAPTCHA_LETTER_ROTATION = None
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)

# Email backend
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=1025)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

try:
    HOSTNAME = socket.gethostname()
except Exception:
    HOSTNAME = 'localhost'
# Scheme and host for the links in e-mails, e.g. https://i5k.nal.usda.gov
# (without the URL prefix the site is served at: the links already have it)
SITE_URL = env('DJANGO_SITE_URL', default='http://' + HOSTNAME).rstrip('/')

LOGIN_ENABLED = env.bool('LOGIN_ENABLED', default=True)
ANALYTICS_ENABLED = env.bool('ANALYTICS_ENABLED', default=False)

# Web Apollo single sign-on cookies are set for this domain.
WEBAPOLLO_COOKIE_DOMAIN = env('WEBAPOLLO_COOKIE_DOMAIN', default='.nal.usda.gov')

# Optional site-specific overrides that are not tracked by git.
try:
    from .settings_local import *  # noqa: F401,F403
except ImportError:
    pass
