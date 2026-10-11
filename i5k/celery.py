import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'i5k.settings')

app = Celery('i5k')

# Read all CELERY_* settings from django.conf:settings.
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
