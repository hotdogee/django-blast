#!/bin/bash

# for production only:
# 1. add analytics code for layout.html (see i5k branch)
# 2. add proxy to installed_app and urls.py

GIT_PATH="/usr/local/test1/django-blast"
PROJ_PATH="/usr/local/i5k"
PROJ_TRAINING_PATH="/usr/local/i5k-training"
USER_NAME="jun-wei.lin"

cd $GIT_PATH
sudo -u $USER_NAME git pull origin master
rsync -av * $PROJ_PATH --exclude "blast/tests.py" --exclude "i5k/settings_prod.py" --exclude "celeryd.sysconfig" --exclude "i5k.conf" --exclude "db" --exclude "app/static/app/scripts/analytics.js"
cd $PROJ_PATH
#chmod 666 db.sqlite3
chmod 777 media
chmod -R 777 media/blast/task
source virtualenv/py2.7/bin/activate

# change (?:blast)* to (?:blast)+ for training site (and dont affect production site meanwhile)
cd $PROJ_PATH/blast/static/blast/scripts
cat blast-results.js | sed -r 's/\(\?\:blast\)\*/\(\?\:blast\)\+/g' > blast-results2.js
mv blast-results2.js blast-results.js

cd $PROJ_PATH
#python manage.py migrate
python manage.py collectstatic --noinput
#python manage.py migrate
#python manage.py loaddata organism.json
#python manage.py loaddata sequencetype.json
#python manage.py loaddata blastdb.json
#python manage.py loaddata jbrowsesetting-stage.json

cd $PROJ_PATH/i5k
cat settings.py | sed -r 's/USE_VIRTUALENV = False/USE_VIRTUALENV = True/g;s/USE_PROD_SETTINGS = False/USE_PROD_SETTINGS = True/g;' > settings2.py
mv settings2.py settings.py
deactivate

# for production training site
echo "--- update training site ---"
cd $PROJ_PATH
rsync -av * $PROJ_TRAINING_PATH --exclude "media" --exclude "virtualenv" --exclude "i5k" --exclude "manage.py" --exclude "celeryd.sysconfig" --exclude "celerybeat.sysconfig" --exclude "db"
rsync -av i5k/* $PROJ_TRAINING_PATH/i5k-training --exclude "celery.py" --exclude "wsgi.py" --exclude "settings_prod.py"
cd $PROJ_TRAINING_PATH/i5k-training
cat settings.py | sed -r 's/i5k/i5k-training/g;' > settings2.py
mv settings2.py settings.py
cd $PROJ_TRAINING_PATH/blast
cat tasks.py | sed -r 's/task_list_cache/task_list_cache_training/g' > tasks2.py
mv tasks2.py tasks.py
cd $PROJ_TRAINING_PATH/blast
cat views.py | sed -r 's/task_list_cache/task_list_cache_training/g' > views2.py
mv views2.py views.py

/etc/init.d/memcached restart
/etc/init.d/celeryd restart
/etc/init.d/celeryd-training restart
/etc/init.d/celerybeat restart
/etc/init.d/httpd restart
