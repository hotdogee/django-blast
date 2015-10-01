# Django settings for i5k project.
from os import path
PROJECT_ROOT = path.dirname(path.abspath(path.dirname(__file__)))

DEBUG = True
# deprecated in Django 1.8
#TEMPLATE_DEBUG = DEBUG
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# template settings for Django 1.8
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            path.join(PROJECT_ROOT, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'social.apps.django_app.context_processors.backends',
                'social.apps.django_app.context_processors.login_redirect',
                'app.context_processors.is_login_enabled',
                'app.context_processors.is_analytics_enabled',
            ],           
        },
    },
]

ALLOWED_HOSTS = (
    'localhost',
)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'django_i5k',
    'USER': 'django',
    'PASSWORD': 'django1234',
    'HOST': 'localhost',
    'PORT': '5432',
    }
}



LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = '/home'

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = path.join(PROJECT_ROOT, 'media').replace('\\','/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = path.join(PROJECT_ROOT, 'static').replace('\\','/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'pipeline.finders.PipelineFinder',
    'pipeline.finders.CachedFileFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n(bd1f1c%e8=_xad02x5qtfn%wg2pi492e$8_erx+d)!tpeoim'

# List of callables that know how to import templates from various sources.
# deprecated in Django 1.8
#TEMPLATE_LOADERS = (
#    'django.template.loaders.filesystem.Loader',
#    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
#)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'axes.middleware.FailedLoginMiddleware',
    'app.middleware.SocialAuthExceptionMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'i5k.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'i5k.wsgi.application'

# deprecated in Django 1.8
#TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#    path.join(PROJECT_ROOT, 'templates'),
#)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'axes',
    'rest_framework',
    'rest_framework_swagger',
    'pipeline',
    'app',
    'blast',
    # 'userprofile',
    # Uncomment the next line to enable the admin:
    'suit', # Optional, Creative Commons Attribution-NonCommercial 3.0 license
    'filebrowser',
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'social.apps.django_app.default',
    'captcha',
    'dashboard',
    #'webapollo',
    'proxy',
    'data',
    'hmmer',
    'clustal',
    #'webapollo_sso',
    #'restaurants',
)

# deprecated in Django 1.8
#from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
#TEMPLATE_CONTEXT_PROCESSORS = TCP + (
#    'django.core.context_processors.request',
#    'social.apps.django_app.context_processors.backends',
#    'social.apps.django_app.context_processors.login_redirect',
#)

FILEBROWSER_SUIT_TEMPLATE = True
FILEBROWSER_DIRECTORY = ''
FILEBROWSER_VERSIONS_BASEDIR = '_versions/'
FILEBROWSER_MAX_UPLOAD_SIZE = 10737418240 # 10GB
FILEBROWSER_EXTENSIONS = {
    'Folder': [''],
    #'Image': ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff'],
    'Document': ['.pdf', '.doc', '.rtf', '.txt', '.xls', '.csv', '.docx'],
    #'Video': ['.mov', '.wmv', '.mpeg', '.mpg', '.avi', '.rm'],
    #'Audio': ['.mp3', '.mp4', '.wav', '.aiff', '.midi', '.m4p'],
    'FASTA': ['.fa', '.faa', '.fna', '.fasta', '.cds', '.pep'],
    'FASTQ': ['.fq', '.fastq'],
    'SAM': ['.sam', '.bam'],
    'WIG': ['.wig', '.bw', '.bigwig'],
    'JSON': ['.json'],
    'GFF': ['.gff', '.gff3']
}
FILEBROWSER_SELECT_FORMATS = {
    'file': ['Folder', 'Image', 'Document', 'Video', 'Audio', 'FASTA', 'FASTQ', 'SAM', 'WIG', 'JSON', 'GFF'],
    #'image': ['Image'],
    'document': ['Document'],
    #'media': ['Video','Audio'],
    'FASTA': ['FASTA'],
    'FASTQ': ['FASTQ'],
    'SAM': ['SAM'],
    'WIG': ['WIG'],
    'JSON': ['JSON'],
    'GFF': ['GFF'],
}
FILEBROWSER_VERSIONS = {
    'admin_thumbnail': {'verbose_name': 'Admin Thumbnail', 'width': 60, 'height': 60, 'opts': 'crop'},
    'thumbnail': {'verbose_name': 'Thumbnail (1 col)', 'width': 60, 'height': 60, 'opts': 'crop'},
    'small': {'verbose_name': 'Small (2 col)', 'width': 140, 'height': '', 'opts': ''},
    'medium': {'verbose_name': 'Medium (4col )', 'width': 300, 'height': '', 'opts': ''},
    'big': {'verbose_name': 'Big (6 col)', 'width': 460, 'height': '', 'opts': ''},
    'large': {'verbose_name': 'Large (8 col)', 'width': 680, 'height': '', 'opts': ''},
}

# Django Suit configuration example
SUIT_CONFIG = {
    # header
    'ADMIN_NAME': 'i5k Admin',
    # 'HEADER_DATE_FORMAT': 'l, j. F Y',
    # 'HEADER_TIME_FORMAT': 'H:i',

    # forms
    # 'SHOW_REQUIRED_ASTERISK': True,  # Default True
    # 'CONFIRM_UNSAVED_CHANGES': True, # Default True

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    #'MENU_ICONS': {
    #    'blast': 'icon-leaf',
    #    'auth': 'icon-lock',
    #},
    'MENU_OPEN_FIRST_CHILD': False, # Default True
    'MENU_EXCLUDE': (),
    'MENU': (
        {'app': 'blast', 'label': 'BLAST', 'icon':'icon-leaf', 'models': (
            {'model': 'blastqueryrecord'},
            {'model': 'organism'},
            {'model': 'sequencetype'},
            {'model': 'blastdb'},
            {'model': 'jbrowsesetting'},
            {'model': 'sequence'},
        )},
        {'app': 'hmmer', 'label': 'Hmmer', 'icon':'icon-leaf', 'models': (
            {'model': 'hmmerdb'},
        )},
        {'app': 'default', 'label': 'Social Auth', 'icon':'icon-leaf', 'models': (
            {'model': 'usersocialauth'},
            {'model': 'nonce'},
            {'model': 'association'},
        )},
        {'app': 'webapollo', 'label': 'Web Apollo', 'icon':'icon-leaf', 'models': (
            {'model': 'species', 'label': 'Species'},
            {'label': 'Management', 'url': '/webapp/webapollo/admin/manage'},
            {'model': 'speciespassword', 'label': '[Read Only] Passwords'},
            {'model': 'registration', 'label': '[Read Only] Registrations'},
        )},
        {'app': 'data', 'label': 'Data', 'icon':'icon-leaf', 'models': (
            {'model': 'file'},
            {'model': 'item'},
            {'model': 'accession'},
        )},
        # auth and axes
        {'label': 'Auth', 'icon':'icon-lock', 'models': (
            {'model': 'auth.user'},
            {'model': 'auth.group'},
            {'model': 'axes.accessattempt'},
            {'model': 'axes.accesslog'},
        )},
        {'label': 'File Browser', 'icon':'icon-hdd', 'url': 'fb_browse'},

    ),

    # misc
    # 'LIST_PER_PAGE': 15
}

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Celery Settings
from kombu import Exchange, Queue
CELERY_DEFAULT_QUEUE = 'i5k'
CELERY_DEFAULT_EXCHANGE = 'i5k'
CELERY_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_DEFAULT_ROUTING_KEY = 'i5k'
CELERY_QUEUES = ( 
    Queue('i5k', Exchange('i5k'), routing_key='i5k'),
)
BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'amqp://'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT=['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_DISABLE_RATE_LIMITS = True
#CELERY_ENABLE_UTC = True

# Use virtual environment or not
USE_VIRTUALENV = False
VIRTUALENV_ROOT = 'virtualenv/py2.7'

USE_CACHE = False
# memcached
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': None, # never expire
    }
}

# django-axes
AXES_LOGIN_FAILURE_LIMIT = 3
AXES_LOCK_OUT_AT_FAILURE = True
AXES_USE_USER_AGENT = True
AXES_COOLOFF_TIME = 1 # 1 hour
AXES_LOGGER = 'axes.watch_login'
AXES_LOCKOUT_TEMPLATE = 'app/login_lockout.html'
AXES_LOCKOUT_URL = None
AXES_VERBOSE = True

# rest_framework
REST_FRAMEWORK = {
    # Use hyperlinked styles by default.
    # Only used if the `serializer_class` attribute is not set on a view.
    #'DEFAULT_MODEL_SERIALIZER_CLASS':
    #    'rest_framework.serializers.HyperlinkedModelSerializer',

    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    #'PAGINATE_BY': 100,
    #'PAGINATE_BY_PARAM': 'page_size',  # Allow client to override, using `?page_size=xxx`.
    'PAGE_SIZE': 10,
}

# django-pipeline
STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_CSS_COMPRESSOR = 'pipeline.compressors.cssmin.CSSMinCompressor'
PIPELINE_CSSMIN_BINARY = 'cssmin'
PIPELINE_JS_COMPRESSOR = 'pipeline.compressors.slimit.JSMinCompressor'

PIPELINE_CSS = {
    'app-layout': {
        'source_filenames': (
            'app/content/site.css',
            'app/content/bootstrap.min.css',
        ),
        'output_filename': 'app/content/app-layout.min.css',
    },
    'blast-results': {
        'source_filenames': (
            'blast/css/codemirror.css',
            'blast/css/xq-light.css',
            'blast/css/kendo.common-bootstrap.core.css',
            'blast/css/kendo.bootstrap.min.css',
            'blast/css/jquery-ui.min.css',
            'blast/dataTables/css/jquery.dataTables.min.css',
            'blast/dataTables/css/dataTables.scroller.min.css',
            'blast/dataTables/css/dataTables.colReorder.min.css',
            'blast/dataTables/css/dataTables.bootstrap.css',
            'blast/css/bootstrap-select.min.css',
            'blast/css/bootstrap-switch.min.css',
            'blast/css/blast-results.css',
        ),
        'output_filename': 'blast/css/blast-results.min.css',
    },
}

PIPELINE_JS = {
    'app-layout': {
        'source_filenames': (
            'app/scripts/jquery-1.11.1.min.js',
            'app/scripts/bootstrap.js',
            'app/scripts/respond.js',
        ),
        'output_filename': 'app/scripts/app-layout.min.js',
    },
    'blast-results': {
        'source_filenames': (
            'blast/scripts/chroma.min.js',
            'blast/scripts/codemirror-compressed.js',
            'blast/scripts/kendo-hotdogee.js',
            'blast/scripts/jquery-ui.min.js',
            'blast/scripts/dragscrollable.js',
            'blast/dataTables/js/jquery.dataTables-hotdogee.js',
            'blast/dataTables/js/dataTables.scroller.js',
            'blast/dataTables/js/dataTables.colReorder.min.js',
            'blast/dataTables/js/dataTables.tableTools.min.js',
            'blast/dataTables/js/dataTables.bootstrap.js',
            'blast/scripts/underscore-min.js',
            'blast/scripts/backbone-min.js',
            'blast/scripts/scribl.1.1.5-hotdogee.js',
            'blast/scripts/bootstrap-select-hotdogee.js',
            'blast/scripts/bootstrap-switch.min.js',
            'blast/scripts/blast-results.js',
        ),
        'output_filename': 'blast/scripts/blast-results.min.js',
    },
}

# social login settings
AUTHENTICATION_BACKENDS = (
    'social.backends.google.GoogleOAuth2',
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details'
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
SOCIAL_AUTH_FACEBOOK_KEY = ''
SOCIAL_AUTH_FACEBOOK_SECRET = ''
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']

# captcha 
CAPTCHA_LETTER_ROTATION = None
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)

# Email backend
EMAIL_HOST = 'localhost'
EMAIL_PORT = '1025'
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

import socket
try:
    HOSTNAME = socket.gethostname()
except:
    HOSTNAME = 'localhost'

LOGIN_ENABLED = True
ANALYTICS_ENABLED = False

# Use settings for production
USE_PROD_SETTINGS = False
if USE_PROD_SETTINGS:
    from settings_prod import *
