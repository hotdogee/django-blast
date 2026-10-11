# django-blast

[![CI](https://github.com/hotdogee/django-blast/actions/workflows/ci.yml/badge.svg)](https://github.com/hotdogee/django-blast/actions/workflows/ci.yml)
[![License: Public Domain](https://img.shields.io/badge/license-public%20domain-blue.svg)](LICENSE)
![Python 3.12 | 3.13 | 3.14](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue.svg)
![Django 5.2 LTS](https://img.shields.io/badge/django-5.2%20LTS-0C4B33.svg)

An [NCBI BLAST+](https://blast.ncbi.nlm.nih.gov/doc/blast-help/downloadblastdata.html) web service with a
[Django](https://www.djangoproject.com/) back end and an interactive HTML5 results viewer. It was built for the
[i5k Workspace@NAL](https://i5k.nal.usda.gov/) at the USDA National Agricultural Library, where it ran at
https://i5k.nal.usda.gov/webapp/blast/, and links BLAST hits to [JBrowse](https://jbrowse.org/) and
[Web Apollo](https://genomearchitect.readthedocs.io/) for genome annotation.

The successor of this project is [genomics-workspace](https://github.com/NAL-i5K/genomics-workspace), see
[Related projects](#related-projects).

- [Features](#features)
- [Screenshots](#screenshots)
- [Quick start with Docker](#quick-start-with-docker)
- [Manual installation](#manual-installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [REST API](#rest-api)
- [Development and tests](#development-and-tests)
- [Upgrading an existing installation](#upgrading-an-existing-installation)
- [Related projects](#related-projects)
- [History and credits](#history-and-credits)

## Features

### Backend

- Implemented in [Python](https://www.python.org/) with [Django](https://www.djangoproject.com/).
- Supports current [NCBI BLAST+ executables](https://blast.ncbi.nlm.nih.gov/doc/blast-help/downloadblastdata.html)
  (blastn, tblastn, tblastx, blastp, blastx).
- Task queue with [Celery](https://docs.celeryq.dev/), using [RabbitMQ](https://www.rabbitmq.com/) or
  [Redis](https://redis.io/) as the broker.
- Generates all BLAST output formats for download: Text, CSV, TSV, XML, ASN.1.
- Converts BLAST output to GFF3 by grouping contiguous HSPs with identical query sequence, subject sequence, strand
  direction and an overlap length less than 6 between neighbouring HSPs under the same match. Every HSP carries its
  bit score, e-value, percent identity and a color from the results page's color key.
- Retrieve previous results with a unique URL for every task.
- BLAST databases are managed in the Django admin: upload or pick a FASTA file, run makeblastdb (its output is kept
  in a log file), index the sequences for the FASTA viewer, and see when a database needs to be rebuilt.
- Opens BLAST hits in JBrowse / Web Apollo with the hit highlighted and the BLAST results as an extra track.
- Read-only REST API with an OpenAPI schema.
- User accounts with registration, Google and Facebook login, and Web Apollo access management.
- Runs on Linux and Windows, or with Docker.

### Frontend - Results

The results page is an interactive data viewer, query and subject coverage graphs on the top are drawn dynamically on
the HTML5 canvas for every high scoring pair (HSP), tabular output from BLAST+ is displayed in a sortable and
searchable table on the bottom right, pairwise text output is displayed on the bottom left panel.

- Fullscreen design dynamically scales to any screen size
- Dynamically draws a unique query coverage graph and a subject coverage graph for every high scoring pair(HSP) on
  HTML5 canvas.
- Interactive graph updates the page as the user mouse over each aligned segment.
- Graph zoom level and line height are first calculated according to the data and screen size, but can be easily
  adjusted to user's preference using the sliders on the left and right sides of each graph.
- Interactive results table updates the page as the user:
  - Mouse over each row.
  - Changes the sorting column.
  - Filters the table using the search box.
- Tested on the latest versions of Chrome, Firefox, IE (in 2014).
  - On Windows: Chrome (ver. 36.0), Firefox (ver. 31.0), IE (ver. 11)

## Screenshots

BLAST Results

![BLAST Results](https://raw.githubusercontent.com/hotdogee/django-blast/doc/doc/images/blast-results-dynamic.gif)

![BLAST Results](https://raw.githubusercontent.com/hotdogee/django-blast/doc/doc/images/blast-results-20140729.jpg)

## Quick start with Docker

[docker-compose.yml](docker-compose.yml) runs the web application (gunicorn), a Celery worker and beat,
PostgreSQL and Redis. NCBI BLAST+ is installed in the image, and two small sample databases are created on the first
start: the i5k *Anoplophora glabripennis* proteins and a few of its transcripts. Docker Compose 2.24 or later is
required.

```sh
git clone https://github.com/hotdogee/django-blast.git
cd django-blast
docker compose up --build
```

Open http://localhost:8000/blast/, choose *Anoplophora glabripennis*, paste a sequence (for example
`AGLA000012-RA` from [example/blastdb/AGLA_sample_transcripts.fna](example/blastdb/AGLA_sample_transcripts.fna) for a
blastx search of the proteins) and press *Search*.

To use the admin at http://localhost:8000/admin/, create an account:

```sh
docker compose exec web python manage.py createsuperuser
```

or set `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` before `docker compose up`. Other settings in
[Configuration](#configuration) go in a `.env` file next to `docker-compose.yml`; only the variables that
`docker-compose.yml` names (`DJANGO_DEBUG`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`,
`DJANGO_EMAIL_BACKEND`, `DJANGO_PORT`, `DJANGO_LOAD_SAMPLE_DATA`, `DJANGO_SUPERUSER_*`, `LOGIN_ENABLED`,
`CELERY_CONCURRENCY`, `BLAST_NUM_THREADS` and `POSTGRES_PASSWORD`) are also read from the shell. The database, broker,
cache, media serving and file locations are set by `docker-compose.yml` and can't be overridden. Note that a `.env` file made
for a manual installation in the same directory (e.g. with `DJANGO_DEBUG=1`) applies to the containers too.
A secret key is generated on the data volume unless `DJANGO_SECRET_KEY` is set. The PostgreSQL password
(`POSTGRES_PASSWORD`, default `django`) only protects the database on the internal compose network; change it, and use
HTTPS, before exposing an instance.

`python docker/smoke_test.py` submits a job to a running stack and checks the results, the same as CI does.

## Manual installation

Requirements: Python 3.12 - 3.14, NCBI BLAST+, a Celery broker (RabbitMQ or Redis) and preferably PostgreSQL 14 or
later (SQLite works for everything except the experimental `data` app).

```sh
python3 -m venv .venv
. .venv/bin/activate                 # Windows: .venv\Scripts\activate
pip install -r requirements.txt
sudo apt install ncbi-blast+         # or install BLAST+ from NCBI and set BLAST_BIN_DIR

cp .env.example .env                 # DJANGO_DEBUG=1 for development, see Configuration
python manage.py migrate
python manage.py createsuperuser
python manage.py load_sample_data    # optional sample databases
python manage.py runserver
```

BLAST jobs run in a Celery worker, started from the project directory:

```sh
celery -A i5k worker -Q i5k --loglevel=info      # Windows: add --pool=solo
celery -A i5k beat --loglevel=info               # optional, daily clean-up of expired results
```

For development without a broker, `CELERY_TASK_ALWAYS_EAGER=1` runs the jobs inside the web process.

In production, run `python manage.py collectstatic` and serve `i5k.wsgi:application` with gunicorn or mod_wsgi
(static files are served by [WhiteNoise](https://whitenoise.readthedocs.io/)). Let the web server serve `MEDIA_ROOT`
at `MEDIA_URL` (or set `DJANGO_SERVE_MEDIA=1`): it holds the downloadable results and the GFF3 files that JBrowse
loads, so it must allow cross-origin requests from the JBrowse host. The site can live below a URL prefix, e.g.
`WSGIScriptAlias /webapp /path/to/django-blast/i5k/wsgi.py`. WhiteNoise and `DJANGO_SERVE_MEDIA` only work when the site
is at the root of the host, so with a prefix let the web server serve `STATIC_ROOT` at `STATIC_URL` and `MEDIA_ROOT` at
`MEDIA_URL` (e.g. `Alias /static/` and `Alias /media/` as in [i5k.conf](i5k.conf)), and set `DJANGO_SITE_URL` to the
scheme and host only.

The deployment files from the original installation are kept for reference and need adjusting for Python 3 and
the new settings: [i5k.conf](i5k.conf) (Apache + mod_wsgi), [celeryd](celeryd), [celerybeat](celerybeat) and their
`*.sysconfig` files (SysV init scripts for CentOS), [util/deploy](util/deploy), and [web.config](web.config) with
[ptvs_virtualenv_proxy.py](ptvs_virtualenv_proxy.py) (IIS / Azure). The BLAST+ 2.2.29 executables bundled in
`blast/bin_linux` and `blast/bin_win` are used when no other BLAST+ is found; the Windows ones need the Visual C++
2010 OpenMP runtime (`VCOMP100.DLL`).

## Configuration

Settings are read from environment variables, or from a `.env` file in the project root
([.env.example](.env.example) lists them). Site-specific Python overrides can go in an untracked
`i5k/settings_local.py`.

| Variable | Default | |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | (required unless `DJANGO_DEBUG=1`) | Django secret key |
| `DJANGO_SECRET_KEY_FILE` | | File to read the secret key from when `DJANGO_SECRET_KEY` is empty (Docker: `/data/secret_key`) |
| `DJANGO_DEBUG` | `0` | Debug mode, for development only |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | Host names the site is served at |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | | e.g. `https://blast.example.org` behind a proxy |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | e.g. `postgres://user:password@host:5432/name` |
| `DATABASE_CONN_MAX_AGE` | `0` | Seconds to keep database connections open |
| `DJANGO_MEDIA_ROOT`, `DJANGO_MEDIA_URL` | `media/`, `/media/` | BLAST databases (`blast/db/`) and results (`blast/task/`) |
| `DJANGO_MEDIA_UPLOAD_MAX_SIZE` | `10737418240` (10 GB) | Largest FASTA file that can be uploaded in the admin, in bytes |
| `DJANGO_STATIC_ROOT`, `DJANGO_STATIC_URL` | `static/`, `/static/` | Collected static files |
| `DJANGO_STATICFILES_STORAGE` | `whitenoise.storage.CompressedStaticFilesStorage` | Storage class of the collected static files |
| `DJANGO_SERVE_MEDIA` | `DJANGO_DEBUG` | Serve `MEDIA_ROOT` through Django |
| `DJANGO_TIME_ZONE` | `America/New_York` | |
| `DJANGO_SITE_URL` | `http://<hostname>` | Scheme and host for the links in e-mails, e.g. `https://i5k.nal.usda.gov` (without the URL prefix) |
| `DJANGO_LOGIN_URL`, `DJANGO_LOGIN_REDIRECT_URL` | `login`, `dashboard` | URL names or paths of the login page and the page shown after login |
| `DJANGO_ADMINS` | | Comma separated e-mail addresses that receive error reports |
| `DJANGO_LOG_LEVEL` | `WARNING` | Level of the console log (the BLAST app always logs `INFO`) |
| `CELERY_BROKER_URL` | `amqp://` | e.g. `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | | Optional; the BLAST jobs don't use task results |
| `CELERY_TASK_ALWAYS_EAGER` | `0` | Run BLAST jobs in the web process |
| `BLAST_BIN_DIR` | | Directory with the BLAST+ executables (default: `PATH`, then `blast/bin_*`) |
| `BLAST_NUM_THREADS` | `4` | `-num_threads` of each BLAST job |
| `BLAST_RESULT_RETENTION_DAYS` | `7` | Results older than this are reported as expired |
| `BLAST_REMOVE_EXPIRED_FILES` | `0` | Let the daily beat job delete expired results |
| `USE_CACHE`, `CACHE_URL` | `0`, `locmemcache://` | Queue position on the results page; needs a shared cache such as `redis://localhost:6379/1` or `pymemcache://127.0.0.1:11211` |
| `LOGIN_ENABLED` | `1` | Show the login links |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY`, `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` | | Google login |
| `SOCIAL_AUTH_FACEBOOK_KEY`, `SOCIAL_AUTH_FACEBOOK_SECRET` | | Facebook login |
| `DJANGO_EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` | Docker: `django.core.mail.backends.console.EmailBackend` (e-mails are only logged) |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` | `localhost`, `1025` | Outgoing e-mail (SMTP) |
| `ANALYTICS_ENABLED` | `0` | NAL web analytics |
| `WEBAPOLLO_COOKIE_DOMAIN` | `.nal.usda.gov` | Domain of the Web Apollo single sign-on cookies |
| `DJANGO_SECURE_PROXY_SSL_HEADER`, `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`, `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`, `DJANGO_SECURE_HSTS_PRELOAD`, `DJANGO_X_FRAME_OPTIONS` | off, `SAMEORIGIN` | HTTPS hardening; `python manage.py check --deploy` reports what is missing |

## Usage

### BLAST databases

BLAST databases are managed in the admin (*Blast* section):

1. Add the **organism** (the NCBI taxonomy id and a description are looked up from the display name) and the
   **sequence types**; `python manage.py loaddata sequencetype` loads *Genome Assembly*, *Transcript* and *Protein*.
2. Add a **BLAST database**: select a FASTA file below `MEDIA_ROOT/blast/db/` or upload one, and give it a title.
   The optional **sequence ID prefix** is prepended to every sequence id (e.g. `Mdes_genome|`) to keep identical ids
   in different databases apart.
3. Select the database in the list and run the **Rebuild** action, which runs makeblastdb and fills the Sequences
   table used by the FASTA viewer. The *makeblastdb* and *index* steps are also available separately. The database's
   page shows whether the database files and the Sequences table are up to date with the FASTA file, and the log of
   the last makeblastdb run (also saved as `<fasta file>.makeblastdb.log`).

Databases that are *shown* and ready appear on the BLAST page, grouped by organism.

### JBrowse and Web Apollo

A **Jbrowse setting** links a BLAST database (usually a genome assembly) to the URL of a JBrowse or Web Apollo
instance that uses it as the reference. Every hit in that database then gets a button in the results table that opens
the genome browser around the hit, highlights the hit and adds the BLAST results as a *BLAST+ Results* track
(Web Apollo's draggable BLAST track, so hits can be dragged into the annotation), colored by bit score like the
results page. JBrowse loads the GFF3 file of the results from `MEDIA_URL`, so that URL must be reachable from the
user's browser.

## REST API

The read-only API lives under `/blast/api/` and can be browsed there. The OpenAPI schema is at
[`/blast/api/schema/`](http://localhost:8000/blast/api/schema/) and the Swagger UI at
[`/blast/api-docs/`](http://localhost:8000/blast/api-docs/) (generated by
[drf-spectacular](https://drf-spectacular.readthedocs.io/)).

| Endpoint | |
| --- | --- |
| `organism/`, `organism/{short_name}/` | Organisms |
| `seqtype/`, `seqtype/{dataset_type}/` | Sequence types |
| `blastdb/`, `blastdb/{title}/` | BLAST databases and their status |
| `blastdb/{title}/seq/`, `blastdb/{title}/seq/{id}/` | Sequences of one database |
| `seq/?id=&blast_db=&organism=` | Search sequences |
| `seq/{id}/` | A sequence by id; add `?blast_db={title}` when the id exists in several databases (otherwise HTTP 300 with the candidate URLs) |
| `task/{task_id}/` | Status of a BLAST job (listing all jobs and `user/` need a staff account) |

Add `?format=fasta` to the sequence endpoints for plain FASTA, e.g.
`/blast/api/blastdb/AGLA_new_ids.faa/seq/gnl%7CAnoplophora_glabripennis_protein_v0.5.3%7CAGLA000012-PA/?format=fasta`.

## Development and tests

```sh
pip install -r requirements-dev.txt
python -m pytest                     # settings: i5k/settings_test.py
```

The tests use SQLite unless `DATABASE_URL` is set; the `data` app tests need PostgreSQL. The end-to-end tests run
makeblastdb and real BLAST jobs (with Celery in eager mode) and are skipped when BLAST+ cannot be found;
`BLAST_TESTS_REQUIRED=1` turns the skip into a failure. `python manage.py test --settings=i5k.settings_test` works
too.

[CI](.github/workflows/ci.yml) runs Ruff (syntax errors and undefined names) and actionlint, the tests on Python
3.12, 3.13 and 3.14 with BLAST+ from Ubuntu, the tests and `check --deploy` on PostgreSQL, and builds the Docker image
and runs [docker/smoke_test.py](docker/smoke_test.py) against `docker compose`.
[Dependabot](.github/dependabot.yml) proposes dependency updates once a month.

## Upgrading an existing installation

The 2016 version ran on Python 2.7 and Django 1.8 with vendored copies of its dependencies. To upgrade:

1. Back up the database (`pg_dump`) and `MEDIA_ROOT`. Django 5.2 needs PostgreSQL 14 or later: upgrade an older
   server first (`pg_upgrade`, or restore the dump into a new server), keeping the `hstore` extension.
2. Move the settings to environment variables (see [Configuration](#configuration)) and use a new secret key.
3. Install the requirements on Python 3.12+ and run `python manage.py migrate`. Notes:
   - `blast.0007` removes the unique constraint on sequence ids, if the database has one (#19).
   - social-auth-app-django uses the same `social_auth_*` tables as python-social-auth but its own migration
     history: run `python manage.py migrate social_django --fake-initial` first (or drop the tables if social login
     is not used).
   - The vendored django-axes had no migrations, so its tables were created by `syncdb`. They only contain login
     attempts; drop `axes_accessattempt` and `axes_accesslog` before migrating so that django-axes 8 can create them.
   - Try the upgrade on a copy of the database first. These steps were tested on a PostgreSQL database created
     with the 2016 code.
4. Run `python manage.py collectstatic`.
5. Existing BLAST databases keep working (paths saved by the old file browser, such as `/media/blast/db/x.fa`, are
   understood). Their status in the admin is based on file times until they are rebuilt once.

## Related projects

- [genomics-workspace](https://github.com/NAL-i5K/genomics-workspace): the successor of django-blast, developed by
  the i5k Workspace@NAL. It contains the functionality of django-blast with many updates and additional features
  ([#24](https://github.com/hotdogee/django-blast/issues/24)).
- [gff3-py](https://github.com/hotdogee/gff3-py): the GFF3 parser and validator used by the `data` app.
- [JBrowse](https://jbrowse.org/) and [Apollo](https://github.com/GMOD/Apollo): the genome browser and annotation
  editor the BLAST results link to.

## History and credits

django-blast was developed in 2014 - 2016 for the [i5k Workspace@NAL](https://i5k.nal.usda.gov/) at the USDA
National Agricultural Library by Han Lin ([@hotdogee](https://github.com/hotdogee)), with Jun-Wei Lin
([@jwlin](https://github.com/jwlin)), who wrote the user accounts, dashboard and Web Apollo integration, and
Chien-Yueh Lee ([@chienyuehlee](https://github.com/chienyuehlee)), who worked on the BLAST search form and its
options. Thanks to
[@childers](https://github.com/childers) for the many bug reports and feature requests from running the i5k
Workspace, and to [@hsiaoyi0504](https://github.com/hsiaoyi0504) and [@mictadlo](https://github.com/mictadlo).
In 2026 the code was ported to Python 3 and Django 5.2, with Docker support and a test suite.

[NCBI BLAST+](https://blast.ncbi.nlm.nih.gov/) is developed by the National Center for Biotechnology Information.

This software is a United States Government Work and is in the public domain; see [LICENSE](LICENSE).
