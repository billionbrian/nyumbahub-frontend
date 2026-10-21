# 🚂 Deploying NyumbaHub to Railway

Production-ready Django config for hosting NyumbaHub (TapInn) on Railway,
deployed from GitHub, with PostgreSQL, S3/R2 media storage, WhiteNoise
static files, JWT auth, and structured logging.

## 1. Pre-flight cleanup (do before first deploy)

- [ ] **Remove real credentials from `.env`**. Your local `.env` contains live
  Safaricom sandbox keys. It is gitignored, but never commit it. Inject secrets
  via Railway variables instead.
- [ ] **Decide domain.** Set `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and
  `CORS_ALLOWED_ORIGINS` to your real Railway/custom domain (with `https://`
  for CSRF/CORS origins).
- [ ] **Decide session store.** Default = database-backed sessions (PostgreSQL).
  For scale, add a Railway Redis service and set `SESSION_BACKEND=redis` +
  `REDIS_URL`, then uncomment `django-redis`/`redis` in `requirements.txt`.
- [ ] **Decide image storage.** Set `USE_S3=True` and provide AWS S3 or
  Cloudflare R2 credentials. Railway's filesystem is ephemeral — local
  `media/` uploads will disappear on every redeploy.
- [ ] **Remove dead duplicate code.** `properties/views.py` defines a mock
  `initiate_payment` (lines ~164–196) that is never wired to URLs and shadows
  the real Daraja implementation in `payments/views.py`. Remove it before
  production (see "Tightening" below).
- [ ] **Switch M-Pesa to live credentials.** `MPESA_ENVIRONMENT=production`,
  live Consumer Key/Secret/Shortcode/Passkey, and your public callback URL.
  Set `MPESA_AUTO_CONFIRM_SIMULATION=False` in production.
- [ ] **Generate a strong `DJANGO_SECRET_KEY`** (never reuse the dev default).

## 2. Create the Railway project

```bash
# Login to Railway
railway login

# Create a new project (or use the dashboard)
railway init nyumbahub

# Link the GitHub repo
#   In Railway dashboard: New Project → Deploy from GitHub repo →
#   select billionbrian/nyumbahub-frontend → main branch
#   Root directory: nyumbahub-frontend  (if repo root is /home/zayne/nyumbahub)
```

If the repo root is `/home/zayne/nyumbahub/nyumbahub-frontend`, point Railway at
that folder so `manage.py`, `requirements.txt`, `Dockerfile`, and `Procfile`
are at the project root.

## 3. Add Railway services

In the Railway dashboard, add these services and link them to the deploy:

| Service | Purpose | Provides env var |
|---------|---------|------------------|
| **PostgreSQL** | Production database | `DATABASE_URL` |
| **Redis** (optional) | Sessions cache at scale | `REDIS_URL` |

Railway injects `DATABASE_URL` automatically once PostgreSQL is added.

## 4. Set Railway environment variables

Add all variables from `.env.example` (replace the placeholder values) in the
Railway project **Variables** tab. Key ones:

```
DEBUG=False
DJANGO_SECRET_KEY=<strong-random-secret>
ALLOWED_HOSTS=<your-railway-domain>,<custom-domain>
CSRF_TRUSTED_ORIGINS=https://<your-domain>,https://<custom-domain>
CORS_ALLOWED_ORIGINS=https://<your-domain>,https://<custom-domain>
USE_S3=True
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...
AWS_S3_REGION_NAME=us-east-1
# AWS_S3_ENDPOINT_URL=https://<account>.r2.cloudflarestorage.com   # for Cloudflare R2
MPESA_ENVIRONMENT=production
MPESA_CONSUMER_KEY=...
MPESA_CONSUMER_SECRET=...
MPESA_SHORTCODE=...
MPESA_PASSKEY=...
MPESA_CALLBACK_URL=https://<your-domain>/api/payments/callback/
MPESA_AUTO_CONFIRM_SIMULATION=False
SECURE_SSL_REDIRECT=True
LOG_LEVEL=INFO
SESSION_BACKEND=db
```

## 5. Deploy

Railway detects the `Dockerfile` and builds the image. On deploy it:

1. Runs `release: python manage.py migrate --noinput` (from `Procfile`) — applies migrations to PostgreSQL.
2. Runs `web:` gunicorn bound to `$PORT`.
3. Static files were already collected at build time (`RUN python manage.py collectstatic`).

Your app is live at the Railway-generated domain (add your custom domain in
the Railway dashboard and point DNS there).

## 6. Image lazy-loading (S3/R2)

With `USE_S3=True` and `DEFAULT_FILE_STORAGE = S3Boto3Storage`:

- Uploaded property images go straight to the bucket; `MEDIA_URL` becomes the
  bucket/CDN URL (e.g. `https://nyumbahub-media.r2.cloudflarestorage.com/`).
- The API already returns absolute image URLs (`primary_image`, `images[]`).
- On the frontend, add `loading="lazy"` to `` tags (or an Intersection
  Observer) so property images lazy-load as the user scrolls.

## 7. Logs

- Django + gunicorn write to **stdout/stderr** (`LOGGING` config uses
  `StreamHandler`). Railway captures these automatically — view them in the
  Railway dashboard **Logs** tab or via `railway logs`.
- Log level is `INFO` in production (`LOG_LEVEL=INFO`); `DEBUG` locally.

## 8. Security tightening checklist

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` from env, strong and unique
- [ ] `ALLOWED_HOSTS` restricted to real domains
- [ ] `CSRF_TRUSTED_ORIGINS` + `CORS_ALLOWED_ORIGINS` restricted to `https://` real domains
- [ ] `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`
- [ ] `SECURE_HSTS_SECONDS` set (1 year)
- [ ] `X_FRAME_OPTIONS=DENY`, `SECURE_CONTENT_TYPE_NOSNIFF=True`
- [ ] `BLACKLIST_AFTER_ROTATION=True` (refresh tokens revoked on logout)
- [ ] M-Pesa using live (not sandbox) credentials; `AUTO_CONFIRM_SIMULATION=False`
- [ ] Remove the duplicate mock `initiate_payment` in `properties/views.py`

## 9. Local production test

```bash
cd /home/zayne/nyumbahub/nyumbahub-frontend
source /home/zayne/nyumbahub/venv/bin/activate
cp .env.example .env   # then edit .env for local prod-like values
python manage.py collectstatic --noinput
gunicorn --bind 0.0.0.0:8000 config.wsgi:application
# → http://127.0.0.1:8000/  with DEBUG=False
```

Then run `python manage.py check` and the test suite before pushing.
