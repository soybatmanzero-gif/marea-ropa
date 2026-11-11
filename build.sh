#!/usr/bin/env bash
# Render lo ejecuta cada vez que se publica el sitio.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py makemigrations tienda --no-input
python manage.py migrate --no-input
python manage.py seed
