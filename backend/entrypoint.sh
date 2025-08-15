#!/bin/sh
set -euo pipefail

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

# Запуск через uvicorn ASGI
exec uvicorn config.asgi:application --host 0.0.0.0 --port 8000
