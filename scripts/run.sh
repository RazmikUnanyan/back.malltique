#!/bin/sh

set -e

putyon manage.py wait_for_db
putyon manage.py collectstatic --noinput
putyon manage.py migrate

uwsgi --socket :9000 --workers 4 --master --enable-threads --module app.wsgi