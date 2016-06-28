Setup guide
===========

This setup guide is tested in Centos 6.7 and django 1.8.12

Note: The following variables may be used in path names; substitute as appropriate:: 

   <user>      :  the name of the user doing a set up. 
   <user-home> :  the user's home directory, e.g., /home/<user>
   <app-home>  :  the root directory of the i5K application, e.g., /app/local/i5k
   <virt-env>  :  the root directory of the virtualenv this set up creates. 
   <git-home>  :  the directory containing the django-blast git repository, e.g. <user-home>/git

Project Applications 
--------------------

Clone or refresh the django-blast project::

    cd <git-home>
    git clone https://github.com/NAL-i5K/django-blast
    
    # Or if the django-blast repository exists:
    cd <git-home>
    git fetch

Yum
---

Update list of packages::

    sudo yum -y update
    
Python 2.7.8
------------

Install necessary packages::

    sudo yum -y groupinstall "Development tools"
    sudo yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel 
    sudo yum -y install readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel python-devel

Install python 2.7.8 from source::

    wget http://www.python.org/ftp/python/2.7.8/Python-2.7.8.tar.xz  
    tar -xf Python-2.7.8.tar  
    
    # Configure as a shared library:
    cd Python-2.7.8
    ./configure --prefix=/usr/local --enable-unicode=ucs4 --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"

    # Compile and install:
    make  
    sudo make altinstall
    
    # Update PATH:
    export PATH="/usr/local/bin:$PATH"
    
    # Checking Python version (output should be: Python 2.7.8):
    python2.7 -V
    
Install pip and virtualenv::

    wget https://bootstrap.pypa.io/ez_setup.py
    sudo /usr/local/bin/python2.7 ez_setup.py
    
    wget https://bootstrap.pypa.io/get-pip.py
    sudo /usr/local/bin/python2.7 get-pip.py
    
    sudo /usr/local/bin/pip2.7 install virtualenv

Build a separate virtualenv::

    # Make root dir for virtualenv and cd into it:
    mkdir <virt-env>
    cd <virt-env> 
    
    # Create a virtual environment called py2.7 and activate:
    virtualenv py2.7 
    source py2.7/bin/activate
    
    # Install the project in the virtual environment:
    cd <app-home> 
    cp -pr <app-home> <virt-env> 
    
Python Modules and Packages
---------------------------

Install additional Python packages::

    cd <virt-env>
     
    # Cut, paste and run the following bash script.
    # If any installation fails script halts:  
    for package in                         \
        "django==1.8.12"                   \
        "markdown==2.6.6"                  \
        "cssmin==0.2.0"                    \
        "django-pipeline==1.6.8"           \
        "djangorestframework==2.3.4"       \
        "django-rest-swagger==0.3.5"       \
        "django-suit==0.2.18"              \
        "django-axes"                      \
        "docutils==0.12"                   \
        "jsmin==2.0.11"                    \
        "pycrypto==2.6.1"                  \
        "python-memcached==1.57"           \
        "python-social-auth==0.2.16"       \
        "requests-oauthlib==0.6.1"         \
        "wsgiref==0.1.2"                   \
        "pillow==2.2.2"                    \
        "django-simple-captcha==0.4.5"
    do
        echo -e "\nInstalling $package..."
        if ! yes | pip install $package ; then 
            echo -e "\nInstallation of package $package FAILED"
            break
        fi
    done
    
RabbitMQ
--------

Install RabbitMQ Server::

    # Install RHEL/CentOS 7 64-Bit Extra Packages for Enterprise Linux (Epel): 
    wget https://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    sudo rpm -ivh epel-release-7-5.noarch.rpm

    # Install Erlang:
    sudo yum -y install erlang

    # Install RabbitMQ server:
    sudo yum -y install rabbitmq-server

    # To start the daemon by default when system boots run:
    sudo chkconfig rabbitmq-server on

    # Start the server:
    sudo /sbin/service rabbitmq-server start
    
Celery
------

Install celery in the virtualenv and configure::

    cd <virt-env>
    pip install celery==3.1.23

    # Copy files:
    sudo cp <app-home>/celeryd /etc/init.d
    sudo cp <app-home>/celerybeat /etc/init.d
    sudo cp <app-home>/celeryd.sysconfig /etc/default/celeryd
    sudo cp <app-home>/celerybeat.sysconfig /etc/default/celerybeat
    
    # Sudo edit '/etc/default/celeryd' as follows: 
    CELERYD_CHDIR="<virt-env>"
    CELERYD_MULTI="<vert-env>/py2.7/bin/celery multi"
    
    # Sudo edit '/etc/default/celerybeat' as follows:
    CELERYBEAT_CHDIR="<app-home>"
    CELERY_BIN="<virt-env>/py2.7/bin/celery"

    # Set as daemon:
    sudo chkconfig celeryd on
    sudo chkconfig celerydbeat on

Memcached
---------

Install and activate memcached::

   sudo yum -y install memcached

   # Set to start at boot time: 
   sudo chkconfig memcached on 

Database
--------

Install PostgreSQL::

    # Add line to yum repository: 
    echo 'exclude=postgresql*' | sudo tee -a /etc/yum.repos.d/CentOS-Base.repo

    # Install the PostgreSQL Global Development Group (PGDG) RPM file:
    sudo yum -y localinstall http://yum.postgresql.org/9.5/redhat/rhel-6-x86_64/pgdg-centos95-9.5-2.noarch.rpm
    
    # Install PostgreSQL 9.5:
    sudo yum -y install postgresql95-server postgresql95-contrib postgresql95-devel
    
    # Initialize (uses default data directory: /var/lib/pgsql):
    sudo service postgresql-9.5 initdb   
    
    # Startup at boot:
    sudo chkconfig postgresql-9.5 on
    
    # Control:
    # sudo service <name> <command>
    # 
    # where <command> can be:
    #  
    #     start   : start the database.
    #     stop    : stop the database.
    #     restart : stop/start the database; used to read changes to core configuration files.
    #     reload  : reload pg_hba.conf file while keeping database running. 
    
    # Start:
    sudo service postgresql-9.5 start

    #
    #  (To remove everything: sudo yum erase postgresql95*)
    #
    
    # Create django database and user:
    sudo su - postgres
    psql
    
    # At the prompt 'postgres=#' enter:
    create database django;
    create user django;
    grant all on database django to django;
    
    # Connect to django database:
    \c django
    
    # Create extension hstore:
    create extension hstore;

    # Config in pg_hba.conf:
    cd <virt-env> 
    export PATH=/usr/pgsql-9.5/bin:$PATH
    pip install psycopg2==2.6

 
Migrate Schema to to PostgreSQL
------------------------------- 

Run migrate::

    cd <virt-env>
    python manage.py migrate

Run on Apache HTTP Server  - TBD
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


