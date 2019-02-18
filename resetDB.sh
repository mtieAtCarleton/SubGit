#!/bin/sh

# run this when you have changed the structure/
# added models to our code

rm db.sqlite3
venv/bin/python manage.py migrate --run-syncdb
