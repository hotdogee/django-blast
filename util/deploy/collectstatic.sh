#!/bin/bash

PROJ_PATH="/usr/local/i5k"

cd $PROJ_PATH
source virtualenv/py2.7/bin/activate
python manage.py collectstatic --noinput
deactivate

