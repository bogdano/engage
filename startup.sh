#!/bin/sh
python manage.py migrate
sqlite3 /data/db.sqlite3 'PRAGMA journal_mode=WAL;'
sqlite3 /data/db.sqlite3 'PRAGMA synchronous=1;'
python manage.py collectstatic --noinput
gunicorn --bind :8000 --workers 2 engage.wsgi

