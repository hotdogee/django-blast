# django-blast: web application and Celery worker image.
# Used by docker-compose.yml; see README.md "Quick start with Docker".
FROM python:3.13-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# NCBI BLAST+ from Debian (the copies bundled in blast/bin_* are not used)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ncbi-blast+ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

COPY . .
RUN DJANGO_SECRET_KEY=build-only python manage.py collectstatic --noinput --verbosity 0 \
    && useradd --uid 1000 --home-dir /app --no-create-home --shell /usr/sbin/nologin django \
    && mkdir -p /data/media \
    && chown -R django /data

ENV DJANGO_MEDIA_ROOT=/data/media \
    BLAST_BIN_DIR=/usr/bin

USER django
VOLUME /data
EXPOSE 8000
ENTRYPOINT ["sh", "/app/docker/entrypoint.sh"]
CMD ["gunicorn", "i5k.wsgi", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "300", "--access-logfile", "-", "--no-control-socket"]
