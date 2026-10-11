"""Health check of the web container (see docker-compose.yml): does gunicorn answer?

The request uses a host name from DJANGO_ALLOWED_HOSTS, so that Django does
not reject it, and any response below 500 counts as healthy, including the
redirect to HTTPS of DJANGO_SECURE_SSL_REDIRECT. Standard library only.
"""
import http.client
import os
import sys

hosts = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip() not in ('', '*')]
host = hosts[0].lstrip('.') if hosts else 'localhost'
try:
    connection = http.client.HTTPConnection('127.0.0.1', 8000, timeout=5)
    # gunicorn trusts X-Forwarded-Proto from 127.0.0.1 (forwarded_allow_ips), so with
    # DJANGO_SECURE_SSL_REDIRECT the probe reaches the real view instead of the redirect
    connection.request('GET', '/blast/', headers={'Host': host, 'X-Forwarded-Proto': 'https'})
    status = connection.getresponse().status
except (OSError, http.client.HTTPException) as e:
    sys.exit('web: %s' % e)
if status >= 500:
    sys.exit('web: HTTP %d' % status)
