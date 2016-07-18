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

    git clone https://github.com/NAL-i5K/django-blast
    
    # Or if the django-blast repository exists:
    cd <git-home>
    git fetch

Yum
---

Generate metadata cache::

    yum makecache
    
Python 2.7.8
------------

Install necessary packages::

    sudo yum -y groupinstall "Development tools"
    sudo yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel 
    sudo yum -y install readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel python-devel

Install python 2.7.8 from source::

    cd <user-home>
    wget http://www.python.org/ftp/python/2.7.8/Python-2.7.8.tar.xz  
    tar -xf Python-2.7.8.tar.xz
    
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

    # Cleanup if desired:
    cd ..
    rm -rf Python-2.7.8.tar.xz Python-2.7.8
    
Install pip and virtualenv::

    wget https://bootstrap.pypa.io/ez_setup.py
    sudo /usr/local/bin/python2.7 ez_setup.py
    
    wget https://bootstrap.pypa.io/get-pip.py
    sudo /usr/local/bin/python2.7 get-pip.py
    
    sudo /usr/local/bin/pip2.7 install virtualenv

Build a separate virtualenv::

    # Make root dir for virtualenv and cd into it:
    cd django-blast
    
    # Create a virtual environment called py2.7 and activate:
    virtualenv py2.7 
    source py2.7/bin/activate
    
    
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

    cd <user-home> 

    # Install RHEL/CentOS 6.8 64-Bit Extra Packages for Enterprise Linux (Epel). 
    # The 6.8 Epel caters for CentOS 6.*:
    wget https://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    sudo rpm -ivh epel-release-6-8.noarch.rpm

    # Install Erlang:
    sudo yum -y install erlang

    # Install RabbitMQ server:
    sudo yum -y install rabbitmq-server

    # To start the daemon by default when system boots run:
    sudo chkconfig rabbitmq-server on

    # Start the server:
    sudo /sbin/service rabbitmq-server start

    # Clean up:
    rm epel-release-6-8.noarch.rpm

    
Celery
------

Install celery in the virtualenv and configure::

    # At this point <virt-env> has all project files
    # including celery config files.
    cd <virt-env>
    pip install celery==3.1.23

    # Copy files:
    sudo cp celeryd /etc/init.d
    sudo cp celerybeat /etc/init.d
    sudo cp celeryd.sysconfig /etc/default/celeryd
    sudo cp celerybeat.sysconfig /etc/default/celerybeat
    
    # Sudo edit '/etc/default/celeryd' as follows: 
    CELERYD_CHDIR="<virt-env>"
    CELERYD_MULTI="<virt-env>/py2.7/bin/celery multi"
    
    # Sudo edit '/etc/default/celerybeat' as follows:
    CELERYBEAT_CHDIR="<virt-env>"
    CELERY_BIN="<virt-env>/py2.7/bin/celery"

    # Set as daemon:
    sudo chkconfig celeryd on
    sudo chkconfig celerybeat on

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
    sudo yum -y install http://yum.postgresql.org/9.5/redhat/rhel-6-x86_64/pgdg-centos95-9.5-2.noarch.rpm
    
    # Install PostgreSQL 9.5:
    sudo yum -y install postgresql95-server postgresql95-contrib postgresql95-devel
    
    # Initialize (uses default data directory: /var/lib/pgsql):
    sudo service postgresql-9.5 initdb   
    
    # Startup at boot:
    sudo chkconfig postgresql-9.5 on
    
    # Control:
    # sudo service postgresql-9.5 <command>
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

    # Exit psql and postgres user:
    \q
    exit

    # Config in pg_hba.conf:
    cd <virt-env> 
    export PATH=/usr/pgsql-9.5/bin:$PATH

    # Restart:
    sudo service postgresql-9.5 restart

    # Install pycopg2:
    pip install psycopg2==2.6

 
Migrate Schema to to PostgreSQL
------------------------------- 

Run migrate::

    cd <virt-env>
    python manage.py migrate

Apache
------

Please note: 
It is essential that tcp port 80 be open in your system. Sometimes the firewall may deny access to it.   
Check if iptables will drop input packets in the output of this command::
  
    sudo iptables -L 

If you see "INPUT" and "DROP" on the same line and no specific ACCEPT rule for tcp port 80
chances are web traffic will be blocked. Ask your sysadmin to open tcp ports 80 and 443 for
http and https. Alternatively, check this `iptables guide`_.   
  .. _iptables guide: https://www.digitalocean.com/community/tutorials/how-to-set-up-a-basic-iptables-firewall-on-centos-6

Install Apache and related modules::

    sudo yum -y install httpd httpd-devel mod_ssl

Give the system a fully qualified domain name (FQDN) if needed::

    # Find out the system IP addres with 'ifconfig'.
    # Assuming it is a VM created by Vagrant, this could be 10.0.2.15.
    # Sudo edit '/etc/hosts' and add an address and domain name entry. 
    # For example:
    10.0.2.15  virtualCentOS.local virtualCentOS

    # Sudo edit the file /etc/httpd/conf/httpd.conf,
    # and set the ServerName, for example: 
    ServerName virtualCentOS.local:80

    # Set to start httpd at boot:
    sudo chkconfig httpd on

    # Check this setting if you wish, with:
    sudo chkconfig --list httpd

    # Control:
    #    sudo apachectl <command> 
    # Where <command> can be:
    #     start         : Start httpd daemon.
    #     stop          : Stop httpd daemon.
    #     restart       : Restart httpd daemon, start it if not running. 
    #     status        : Brief status report.
    #     graceful      : Restart without aborting open connections. 
    #     graceful-stop : stop without aborting open connections.
    #
    # Start httpd daemon:
    sudo apachectl start

    # Test Apache:
    # If all is well. This command should produce copious 
    # HTML output and in the first few lines you should see: 
    #   '<title>Apache HTTP Server Test Page powered by CentOS</title>'
    curl localhost

    # You can also view the formatted Apache test page in your 
    # browser, e.g., firefox http://<setup-machine-ip-address>  


