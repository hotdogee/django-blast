"""Settings for the test suite.

    pytest                                      # uses this module, see pyproject.toml
    python manage.py test --settings=i5k.settings_test

Set DATABASE_URL to run the tests against PostgreSQL instead of SQLite.
"""
import os
import tempfile

os.environ.setdefault('DJANGO_SECRET_KEY', 'test-secret-key-not-for-production')
os.environ.setdefault('CELERY_TASK_ALWAYS_EAGER', '1')

from .settings import *  # noqa: E402,F401,F403
from .settings import STORAGES

DEBUG = False
STORAGES['staticfiles'] = {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
MEDIA_ROOT = tempfile.mkdtemp(prefix='django-blast-test-media-')
SERVE_MEDIA = True
CELERY_BROKER_URL = 'memory://'
CELERY_TASK_ALWAYS_EAGER = True
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'TIMEOUT': None}}
CAPTCHA_TEST_MODE = True
BLAST_NUM_THREADS = 1
