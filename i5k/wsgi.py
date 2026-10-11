"""
WSGI config for i5k project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments (gunicorn, mod_wsgi, wfastcgi). It exposes
a module-level variable named ``application``.

When deploying with mod_wsgi, point ``python-home`` at the virtual environment
instead of activating it from this file.
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "i5k.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
