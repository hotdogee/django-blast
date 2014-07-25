!/bin/bash
find /usr/local/django_web/rabbitmq/files/ -type d -mtime +15 -exec rm -rf {} \;
find /usr/local/blast_dev/web/TmpGifs/ -type f -name *.gif -mtime +15 -exec rm -f {} \;
