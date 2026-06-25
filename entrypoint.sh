#!/bin/sh
set -e

echo "==> Waiting for database to be ready..."
python -c "
import os, time, psycopg

host = os.environ.get('DB_HOST', 'db')
port = int(os.environ.get('DB_PORT', '5432'))
dbname = os.environ.get('DB_NAME', 'db_lookatstore')
user = os.environ.get('DB_USER', 'postgres')
password = os.environ.get('DB_PASSWORD', '')

for attempt in range(30):
    try:
        conn = psycopg.connect(
            host=host, port=port, dbname=dbname,
            user=user, password=password, connect_timeout=3
        )
        conn.close()
        print(f'Database ready after {attempt + 1} attempt(s).')
        break
    except Exception as e:
        print(f'Attempt {attempt + 1}/30: {e}')
        time.sleep(2)
else:
    print('Could not connect to database after 30 attempts. Exiting.')
    exit(1)
"

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting Gunicorn..."
exec gunicorn lookatstore_inventory.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers ${GUNICORN_WORKERS:-3} \
    --timeout ${GUNICORN_TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile -
