#!/bin/sh
set -e

echo ">>> Waiting for PostgreSQL (db:5432)..."
until python -c "
import socket, sys
s = socket.socket()
s.settimeout(2)
try:
    s.connect(('db', 5432))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "    PostgreSQL not ready yet..."
  sleep 2
done
echo ">>> PostgreSQL is ready."

echo ">>> Waiting for Redis (redis:6379)..."
until python -c "
import socket, sys
s = socket.socket()
s.settimeout(2)
try:
    s.connect(('redis', 6379))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
  echo "    Redis not ready yet..."
  sleep 2
done
echo ">>> Redis is ready."

echo ">>> Running database migrations..."
python manage.py migrate --noinput

echo ">>> Collecting static files..."
python manage.py collectstatic --noinput

echo ">>> Starting gunicorn on 0.0.0.0:8000 ..."
exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  config.wsgi:application
