#!/bin/sh
set -e

echo "[entrypoint] Migraciones..."
python manage.py migrate --noinput

echo "[entrypoint] Archivos estáticos..."
python manage.py collectstatic --noinput

echo "[entrypoint] Gunicorn..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
