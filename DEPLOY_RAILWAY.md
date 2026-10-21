# Railway Deployment Runbook — NyumbaHub

Technical runbook for deploying NyumbaHub to Railway with PostgreSQL, S3/R2 media storage, WhiteNoise static files, JWT authentication, and structured logging.

## Pre-deployment checklist

- Remove real credentials from `.env`. The file is gitignored; inject secrets through Railway Variables instead.
- Set `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and `CORS_ALLOWED_ORIGINS` to your real domains using `https://`.
- Use database-backed sessions (`SESSION_BACKEND=db`) by default, or Redis if you add a Railway Redis service.
- Set `USE_S3=True` with AWS S3 or Cloudflare R2 credentials. Railway's filesystem is ephemeral and local media uploads disappear on every redeploy.
- Switch M-Pesa to live credentials: `MPESA_ENVIRONMENT=production`, live Consumer Key/Secret/Shortcode/Passkey, and a public callback URL. Set `MPESA_AUTO_CONFIRM_SIMULATION=False`.
- Generate a strong `DJANGO_SECRET_KEY`. Do not reuse the development default.

## Create the Railway project

1. Log in to Railway.
2. Create a new project from the GitHub repo `billionbrian/nyumbahub-frontend`, branch `main`.
3. Set the root directory to `.` so `manage.py`, `requirements.txt`, `Dockerfile`, and `Procfile` are at the project root.

## Add Railway services

| Service | Purpose | Provides |
|---------|---------|----------|
| PostgreSQL | Production database | `DATABASE_URL` |
| Redis (optional) | Session cache | `REDIS_URL` |

Railway injects `DATABASE_URL` automatically once PostgreSQL is added.

## Set environment variables

Add all variables from `.env.example` in the Railway Variables tab:

```
DEBUG=False
DJANGO_SECRET_KEY=<strong-random-secret>
ALLOWED_HOSTS=<railway-domain>,<custom-domain>
CSRF_TRUSTED_ORIGINS=https://<railway-domain>,https://<custom-domain>
CORS_ALLOWED_ORIGINS=https://<railway-domain>,https://<custom-domain>
USE_S3=True
AWS_ACCESS_KEY_ID=<access-key>
AWS_SECRET_ACCESS_KEY=<secret-key>
AWS_STORAGE_BUCKET_NAME=<bucket-name>
AWS_S3_REGION_NAME=us-east-1
MPESA_ENVIRONMENT=production
MPESA_CONSUMER_KEY=<live-consumer-key>
MPESA_CONSUMER_SECRET=<live-consumer-secret>
MPESA_SHORTCODE=<live-paybill-or-till>
MPESA_PASSKEY=<live-passkey>
MPESA_CALLBACK_URL=https://<your-domain>/api/payments/callback/
MPESA_TIMEOUT=30
MPESA_FALLBACK_ON_TIMEOUT=False
MPESA_AUTO_CONFIRM_SIMULATION=False
SECURE_SSL_REDIRECT=True
LOG_LEVEL=INFO
SESSION_BACKEND=db
```

## Deploy

Railway builds the Docker image and:

1. Runs `release: python manage.py migrate --noinput` to apply migrations to PostgreSQL.
2. Runs `web: gunicorn ...` bound to `$PORT`.
3. Serves static files collected at build time.

The app is live at the Railway-generated domain. Add your custom domain in the Railway dashboard and point DNS there.

## Image storage (S3/R2)

With `USE_S3=True`, uploaded property images go directly to the object storage bucket. `MEDIA_URL` becomes the bucket or CDN URL. The API already returns absolute image URLs. On the frontend, add `loading="lazy"` to image tags or use an Intersection Observer for lazy loading.

## Logs

Django and gunicorn write to stdout/stderr. Railway captures these automatically. View logs in the Railway dashboard or with `railway logs`. Production log level is `INFO`.

## Security checklist

- `DEBUG=False`
- `SECRET_KEY` is strong and unique, from environment
- `ALLOWED_HOSTS` restricted to real domains
- `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` restricted to `https://` real domains
- `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`
- `SECURE_HSTS_SECONDS` set to one year
- `X_FRAME_OPTIONS=DENY`, `SECURE_CONTENT_TYPE_NOSNIFF=True`
- `BLACKLIST_AFTER_ROTATION=True` so refresh tokens are revoked on logout
- M-Pesa uses live credentials, not sandbox
- Duplicate mock `initiate_payment` removed from `properties/views.py`

## Local production test

```bash
cd /home/zayne/nyumbahub/nyumbahub-frontend
source /home/zayne/nyumbahub/venv/bin/activate
cp .env.example .env
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 config.wsgi:application
```

Then run `python manage.py check` and the test suite before pushing.
