# Railway Deployment Guide — NyumbaHub

Deploy NyumbaHub to Railway (free tier) with PostgreSQL.

Domain: nyumbahubtapinn.co.ke
Repo: billionbrian/nyumbahub-frontend

## Prerequisites

- GitHub account with access to the private repo
- Railway account at railway.app
- S3 or Cloudflare R2 bucket details for property image storage
- Safaricom Daraja live credentials (Consumer Key, Consumer Secret, Shortcode, Passkey)

## Step 1: Clone the repository

```bash
git clone git@github.com:billionbrian/nyumbahub-frontend.git
cd nyumbahub-frontend
```

The production-ready code is already on the `main` branch. No code changes are required.

## Step 2: Create the Railway project

1. Log in to the Railway dashboard.
2. Create a new project and select "Deploy from GitHub repo".
3. Choose `billionbrian/nyumbahub-frontend`, branch `main`.
4. Set the root directory to `.` (the repository root).

Railway detects the `Dockerfile` and `Procfile` automatically.

## Step 3: Add a PostgreSQL database

SQLite does not survive redeploys and must not be used in production.

1. In the Railway project dashboard, add a PostgreSQL database service.
2. Railway provisions `DATABASE_URL` automatically.

## Step 4: (Optional) Add Redis

Redis is optional for session storage. If added, Railway provisions `REDIS_URL`.

Without Redis, sessions use the PostgreSQL database (`SESSION_BACKEND=db`), which works for the free tier.

## Step 5: Configure environment variables

In the Railway dashboard, open the project Variables tab and add the following:

| Variable | Value | Notes |
|----------|-------|-------|
| `DEBUG` | `False` | Required for production |
| `DJANGO_SECRET_KEY` | Strong random string | Generate with `openssl rand -hex 32` |
| `ALLOWED_HOSTS` | `nyumbahubtapinn.co.ke,<railway-url>` | Comma-separated domains |
| `CSRF_TRUSTED_ORIGINS` | `https://nyumbahubtapinn.co.ke,https://<railway-url>` | Must use `https://` |
| `CORS_ALLOWED_ORIGINS` | `https://nyumbahubtapinn.co.ke,https://<railway-url>` | Must use `https://` |
| `SESSION_BACKEND` | `db` | Use `redis` only if Redis was added |
| `USE_S3` | `True` | Required — Railway disk is ephemeral |
| `AWS_ACCESS_KEY_ID` | S3/R2 access key | |
| `AWS_SECRET_ACCESS_KEY` | S3/R2 secret key | |
| `AWS_STORAGE_BUCKET_NAME` | Bucket name | e.g. `nyumbahub-media` |
| `AWS_S3_REGION_NAME` | `us-east-1` | Or your bucket region |
| `AWS_S3_ENDPOINT_URL` | Optional | For Cloudflare R2 |
| `AWS_DEFAULT_ACL` | `public-read` | |
| `SECURE_SSL_REDIRECT` | `True` | Forces HTTPS |
| `LOG_LEVEL` | `INFO` | |
| `MPESA_ENVIRONMENT` | `production` | Live credentials only |
| `MPESA_CONSUMER_KEY` | Live Daraja consumer key | |
| `MPESA_CONSUMER_SECRET` | Live Daraja consumer secret | |
| `MPESA_SHORTCODE` | Live Paybill/Till number | |
| `MPESA_PASSKEY` | Live Daraja passkey | |
| `MPESA_CALLBACK_URL` | `https://nyumbahubtapinn.co.ke/api/payments/callback/` | Public HTTPS URL |
| `MPESA_TIMEOUT` | `30` | |
| `MPESA_FALLBACK_ON_TIMEOUT` | `False` | |
| `MPESA_AUTO_CONFIRM_SIMULATION` | `False` | |
| `JWT_ACCESS_LIFETIME_MINUTES` | `60` | |
| `JWT_REFRESH_LIFETIME_DAYS` | `7` | |
| `GEOCODING_NOMINATIM_USER_AGENT` | `NyumbaHub-StudentHousing/1.0 (admin@nyumbahub.test)` | |

Do not commit real secrets to GitHub. Inject all secrets through Railway Variables.

## Step 6: Deploy

1. Open the Deployments tab in the Railway dashboard.
2. Trigger a new deployment.
3. Railway builds the Docker image, runs database migrations, and starts gunicorn.

The app is available at the Railway-generated URL (for example, `https://nyumbahub-xxx.up.railway.app`).

## Step 7: Add the custom domain

1. In the Railway dashboard, go to Settings > Domains.
2. Add `nyumbahubtapinn.co.ke`.
3. Add the DNS records Railway provides at your domain registrar.
4. Wait for DNS propagation.

If you do not have registrar access, continue testing on the Railway URL and add the custom domain later.

## Step 8: Verify the deployment

Check these URLs:

| URL | Expected result |
|-----|-----------------|
| `https://<your-domain>/` | Homepage loads |
| `https://<your-domain>/api/properties/` | JSON list of properties |
| `https://<your-domain>/admin/` | Django admin login |
| `https://<your-domain>/api/auth/login/` | Login endpoint responds |

Demo accounts:

| Role | Username | Password |
|------|----------|----------|
| Landlord | demo_landlord | DemoLandlord123! |
| Tenant | demo_tenant | DemoTenant123! |

## Security checklist

- `DEBUG` is `False`
- `DJANGO_SECRET_KEY` is strong and unique
- `ALLOWED_HOSTS` contains only real domains
- `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` use `https://`
- `SECURE_SSL_REDIRECT` is `True`
- M-Pesa uses live credentials, not sandbox
- `USE_S3` is `True` with real bucket credentials

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Build fails | Check Railway Deployments > Logs |
| `DATABASE_URL` missing | Add the PostgreSQL service |
| Images disappear after redeploy | Set `USE_S3=True` and configure S3/R2 |
| M-Pesa payments fail | Use live Daraja credentials |
| Custom domain not resolving | Verify DNS records at your registrar |

## Files in the repository

| File | Purpose |
|------|---------|
| `Dockerfile` | Container build instructions |
| `Procfile` | Railway release and web commands |
| `docker-compose.yml` | Local development stack |
| `config/settings.py` | Production Django settings |
| `.env.example` | Environment variable template |
| `DEPLOY_RAILWAY.md` | Technical deploy runbook |
