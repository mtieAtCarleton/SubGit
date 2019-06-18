#!/bin/sh

# run this when you have changed the structure/
# added models to our code

rm db.sqlite3
venv/bin/python manage.py makemigrations
venv/bin/python manage.py migrate --run-syncdb
venv/bin/python cleanup.py $username
venv/bin/python setup_courses.py
