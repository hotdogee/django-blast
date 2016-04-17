Setup guide
===========

This setup guide is tested in Centos 7.0/6.5 and django 1.8.12

Environmnet 
-----------

Python 2.7.8
~~~~~~~~~~~~

Install necessary packages::

    yum groupinstall "Development tools"
    yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel 
    yum install readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel python-devel

Install python 2.7.8 from source::

    wget http://www.python.org/ftp/python/2.7.8/Python-2.7.8.tar.xz  
    xz -d Python-2.7.8.tar.xz  
    tar -xvf Python-2.7.8.tar  

    # Enter the directory:
    cd Python-2.7.8

    # Run the configure:
    ./configure --prefix=/usr/local

    # compile and install it:
    make  
    make altinstall

    # Checking Python version:
    [root@i5k ~]# python2.7 -V
    Python 2.7.8  

    export PATH="/usr/local/bin:$PATH"

Intall pip and virtualenv::

    wget https://bootstrap.pypa.io/ez_setup.py
    python2.7 ez_setup.py
    wget https://bootstrap.pypa.io/get-pip.py
    python2.7 get-pip.py
    pip2.7 install virtualenv

Build a separated virtualenv::

    # create a virtual environment called py2.7. 
    # Activate it by source py2.7/bin/activat

    # Make dir '/path/to/i5k/virtualenv' and switch in
    mkdir /path/to/i5k/virtualenv 
    cm /path/to/i5k/virtualenv
    /usr/bin/virtualenv py2.7 
    source py2.7/bin/activate

RabbitMQ 
~~~~~~~~

Install RabbitMQ Server::

    ## RHEL/CentOS 7 64-Bit ##
    wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm
    rpm -ivh epel-release-7-5.noarch.rpm

    #Install Erlang:
    yum install erlang

    #Install RabbitMQ server:
    yum install rabbitmq-server

    #To start the daemon by default when system boots, as an administrator run:
    #chkconfig rabbitmq-server on
    systemctl enable/disable rabbitmq-server

    #To start/stop server:
    #/sbin/service rabbitmq-server start/stop/restart/status
    systemctl start/stop/restart/status rabbitmq-server

Celery
~~~~~~

Tested on Celery 3.1.23

::

    pip install celery==3.1.23
    pip install django==1.8.12


* Copy init `celery`_ script  and `celerybeat`_ script to ``/etc/init.d/``

  .. _celery: https://github.com/celery/celery/blob/3.1/extra/generic-init.d/celeryd
  .. _celerybeat: https://github.com/celery/celery/blob/3.1/extra/generic-init.d/celerybeat

* Copy two configuration files (``/path/to/i5k/celeryd.sysconfig`` and ``celerybeat.sysconfig``) to ``/etc/default/``, modify ``CELERYD_CHDIR``, ``CELERYD_MULTI``, ``CELERYBEAT_CHDIR`` and ``CELERY_BIN`` with your project path. 
* Modify code in celeryd init script as following.

::

    # Change code in celeryd init script

    if [[ `dirname $0` == /etc/rc*.d ]]; then
        SCRIPT_FILE=$(readlink "$0")
    else
        SCRIPT_FILE="$0"
    fi

    # To

    if [[ -L "$0" ]]; then
        SCRIPT_FILE=$(readlink "$0")
    else
        SCRIPT_FILE="$0"
    fi

::

    # cp celeryd init script to /etc/init.d/
    # cp celerybeat init script to /etc/init.d/
    cp /path/to/i5k/celeryd.sysconfig /etc/default/celeryd
    cp /path/to/i5k/celerybeat.sysconfig /etc/default/celerybeat

    # set as daemon 
    chkconfig celeryd on
    chkconfig celerydbeat on

Memcached
~~~~~~~~~

Queue status can be provided by installing and activating memcached while query is submitted.
In ``settings.py``, change ``USE_CACHE=True``. reference


Install and activated memcached::

   yum install memcached

   # chkconfig memcached on
   # service memcached restart

   systemctl enable memcached 
   ststemctl start memcached

Configuration in ``setting.py``::

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
            'TIMEOUT': None, # never expire
        }
    }

Python Modules
--------------

django
~~~~~~

Install django 1.8.12

::

    pip intall django==1.8.12


**Authentication backend**

All authenticaion and authorization stuff such as login, password, permissions and users are handled by Django's default authentication backend. We use or extend Django's classes to build user-related functions in app/views.py, and put the url mappings in i5k/urls.py and HTML files in app/templates/app/\*.html. The data tables Auth -> Users and Auth -> Groups are built-in for storing user data.


**django-axe**

* `django-axes`_ is a very simple way for you to keep track of failed login attempts, both for the Django admin and for the rest of your site.
* User login fail log could be viewed in Admin page (Axe -> Lockout status).  Change ``Failed logins`` field or delete record for unlock this account. ``AXES_LOGIN_FAILURE_LIMIT``, the number of login attempts allowed before a record is created for the failed logins. Default 3.

.. _django-axes: https://pypi.python.org/pypi/django-axes


django-pipeline
~~~~~~~~~~~~~~~

Install `django-pipeline`_ 

    .. _django-pipeline : https://django-pipeline.readthedocs.org/en/latest/installation.html

::

    pip install django-pipeline==1.6.8

Configuration in ``setting.py``::
    
    INSTALLED_APPS = (
        'pipeline',
    )

    STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'pipeline.finders.PipelineFinder',
        'pipeline.finders.CachedFileFinder',
    )


Django REST framework
~~~~~~~~~~~~~~~~~~~~~

Install rest framework (rest framework is still ongoing)

::

    pip install djangorestframework==3.3.3
    pip install django-rest-swagger==0.3.5

Django Suit
~~~~~~~~~~~

Install `django suit`_ 

    .. _django suit: http://django-suit.readthedocs.org/en/develop/

::

    pip install django-suit==0.2.18

Configuration in ``setting.py``::

    INSTALLED_APPS = (
        'suit',
        'django.contrib.admin',
    )

    TEMPLATES = [
        {
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.request',
                ],
            },
        }
    ]

filebrowsers
~~~~~~~~~~~~

python-social-auth
~~~~~~~~~~~~~~~~~~

Install social-auth relatives

::

    pip install requests-oauthlib==0.6.1
    pip install python-social-auth==0.2.16

Supported by `python-social-auth`_ package. You will need a google account and a facebook account to setup your app and get the keys and secrets for the app. Then fill the following section in 'settings_prod.py'. Refer to this instruction for detailed settings.

    .. _python-social-auth: https://github.com/omab/python-social-auth

::

    # social login settings
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''
    SOCIAL_AUTH_FACEBOOK_KEY = ''
    SOCIAL_AUTH_FACEBOOK_SECRET = ''

Tables and data under Social Auth are automatically generated. Social Auth -> User social auths stores mappings between users OAuth data and their Django user accounts.

Some notes about current python-social-auth settings:

* Social and local accounts are corresponded by email address. Different social accounts with the same email would be mapped to the same local user in Django.
* User can register a local account through our registration form, or the system would create a new one for the user who first logs in with his/her social account. Only the former can update their account information (the later can only update their institutions), change their password and request for password reset.

Database
--------

Using PostgreSQL as Database Backend:: 

    # install PostgresSQL

    postgres=# create user django; 
    postgres=# create database django;
    postgres=# grant all on database django to django;
    # connect to database django
    postgres=# \c django 
    # create extension hstore
    postgres=# create extension hstore;

    # config in pg_hba.conf
    pip install psycopg2==2.6

* Install PostgreSQL ( `postgresql reference`_ )

  .. _postgresql reference: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-centos-7
* Create the user and database for this application
* Allowing connection from the database user by setting your ``/var/lib/pgsql/9.x/data/pg_hba.conf``
* Install pip package psycopg2. Path of pg_config binary may need to be exported. 

::

    pip install psycopg2==2.6
    export PATH=/usr/pgsql-9.x/bin:"$PATH"

Migration db schema to PostgreSQL 

::

    python manage.py migrate

Others
~~~~~~

Install necessary modules

::

    pip install -r /path/to/i5k/requirements.txt

Run on Apache HTTP Server
-------------------------

Install Apache HTTP Server and development tools ( `install reference`_ )

  .. _install reference: http://modwsgi.readthedocs.org/en/latest/user-guides/quick-installation-guide.html

::

    yum install httpd-devel

    # set as daemon
    systemctl enable httpd

    wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.4.23.tar.gz 
    tar -zxf 4.4.23.tar.gz
    cd mod_wsgi-4.4.23/  
    ./configure --with-apxs=/usr/sbin/apxs 
    make
    make install

Use Django with Apache and mod_wsgi ( `configuration reference`_ )

  .. _configuration reference: https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/modwsgi/

::

    LoadModule wsgi_module modules/mod_wsgi.so


Continuous integration
----------------------
Jenkins
~~~~~~~
