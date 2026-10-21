FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings \
    PORT=8000

WORKDIR /app

# System deps: libpq for psycopg2, libjpeg/zlib for Pillow (image uploads)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev libjpeg-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Project code
COPY . .

# Entrypoint waits for DB/Redis, runs migrations + collectstatic, then starts gunicorn.
ENTRYPOINT ["/app/entrypoint.sh"]
