#!/bin/sh
# Container entrypoint: prepare the environment, then run the command
# (gunicorn by default, or a celery worker / beat).
set -e

# Generate a persistent secret key on the data volume unless one is given.
# settings.py reads it from DJANGO_SECRET_KEY_FILE, so that commands run with
# `docker compose exec` use it too.
if [ -z "$DJANGO_SECRET_KEY" ]; then
    key_file=${DJANGO_SECRET_KEY_FILE:-/data/secret_key}
    if [ ! -s "$key_file" ]; then
        python -c 'import secrets; print(secrets.token_urlsafe(50))' > "$key_file"
        chmod 600 "$key_file"
    fi
    DJANGO_SECRET_KEY_FILE=$key_file
    export DJANGO_SECRET_KEY_FILE
fi

if [ "${DJANGO_MIGRATE:-0}" = "1" ]; then
    python manage.py migrate --noinput
fi

# Optional admin account, e.g. for a demo instance.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
User = get_user_model()
name = os.environ['DJANGO_SUPERUSER_USERNAME']
if not User.objects.filter(username=name).exists():
    User.objects.create_superuser(name, os.environ.get('DJANGO_SUPERUSER_EMAIL', ''), os.environ['DJANGO_SUPERUSER_PASSWORD'])
    print('Created superuser', name)
"
fi

if [ "${DJANGO_LOAD_SAMPLE_DATA:-0}" = "1" ]; then
    python manage.py load_sample_data
fi

exec "$@"
