# 🚂 Railway Deployment Guide — NyumbaHub (TapInn)

**For:** Anyone with access to the private GitHub repo  
**Goal:** Deploy NyumbaHub to Railway (free tier) with PostgreSQL  
**Domain:** `nyumbahubtapinn.co.ke`  
**Repo:** `billionbrian/nyumbahub-frontend`

> ⚠️ **Important:** This repo is **private**. You need write access to clone/push/deploy it. All production-ready code has already been pushed — you just need to run the deploy on Railway.

---

## Before you start

Make sure you have:

1. A **GitHub account** with access to `billionbrian/nyumbahub-frontend` (private repo)
2. A **Railway account** (free tier) at [railway.app](https://railway.app)
3. A **Cloudflare account** (optional, only if you want to manage `nyumbahubtapinn.co.ke` DNS via Cloudflare)
4. **S3 or Cloudflare R2 bucket** details (for storing property images — Railway's disk resets on every deploy, so local uploads will disappear without this)
5. **Safaricom Daraja live credentials** (Consumer Key, Consumer Secret, Shortcode, Passkey) for production M-Pesa

---

## Step 1: Get the code on your machine

```bash
# Clone the private repo (you need GitHub access)
git clone git@github.com:billionbrian/nyumbahub-frontend.git
# or via HTTPS:
# git clone https://github.com/billionbrian/nyumbahub-frontend.git

cd nyumbahub-frontend
```

The production-ready code is already on `main`. You do **not** need to make any code changes.

---

## Step 2: Create the Railway project

1. Log in to [Railway Dashboard](https://railway.app/dashboard)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `billionbrian/nyumbahub-frontend` → `main` branch
4. Set **Root Directory** to `.` (the repo root)
5. Railway will detect the `Dockerfile` and `Procfile` automatically

---

## Step 3: Add a PostgreSQL database

Railway needs PostgreSQL for production (SQLite won't survive redeploys).

1. In your Railway project dashboard, click **New** → **Database** → **PostgreSQL**
2. Wait for it to provision
3. Railway automatically creates a `DATABASE_URL` environment variable — you do **not** need to set it manually

> ⚠️ Do **not** use SQLite in production. The database must be PostgreSQL.

---

## Step 4: (Optional but recommended) Add Redis for sessions

If you want Redis-backed sessions (faster, scalable):

1. Click **New** → **Database** → **Redis**
2. Railway creates a `REDIS_URL` variable

If you skip Redis, sessions will use the PostgreSQL database (`SESSION_BACKEND=db`) — this works fine for the free tier.

---

## Step 5: Set environment variables

In the Railway dashboard, go to your project → **Variables** tab. Add every variable below.

### Required variables

| Variable | What to put | Notes |
|----------|-------------|-------|
| `DEBUG` | `False` | Must be `False` in production |
| `DJANGO_SECRET_KEY` | A long random string | Generate one: `openssl rand -hex 32` |
| `ALLOWED_HOSTS` | `nyumbahubtapinn.co.ke,<railway-url>.up.railway.app` | Comma-separated, no spaces |
| `CSRF_TRUSTED_ORIGINS` | `https://nyumbahubtapinn.co.ke,https://<railway-url>.up.railway.app` | Must start with `https://` |
| `CORS_ALLOWED_ORIGINS` | `https://nyumbahubtapinn.co.ke,https://<railway-url>.up.railway.app` | Must start with `https://` |
| `SESSION_BACKEND` | `db` | Use `redis` only if you added Redis |
| `USE_S3` | `True` | **Required** — Railway disk is ephemeral |
| `AWS_ACCESS_KEY_ID` | Your S3/R2 access key | |
| `AWS_SECRET_ACCESS_KEY` | Your S3/R2 secret key | |
| `AWS_STORAGE_BUCKET_NAME` | Your bucket name | e.g. `nyumbahub-media` |
| `AWS_S3_REGION_NAME` | `us-east-1` | Or your bucket region |
| `AWS_S3_ENDPOINT_URL` | (optional) | Set only if using Cloudflare R2: `https://<account>.r2.cloudflarestorage.com` |
| `AWS_DEFAULT_ACL` | `public-read` | |
| `SECURE_SSL_REDIRECT` | `True` | Forces HTTPS |
| `LOG_LEVEL` | `INFO` | |
| `MPESA_ENVIRONMENT` | `production` | **Not** sandbox for live site |
| `MPESA_CONSUMER_KEY` | Your live Daraja consumer key | |
| `MPESA_CONSUMER_SECRET` | Your live Daraja consumer secret | |
| `MPESA_SHORTCODE` | Your live Paybill/Till number | |
| `MPESA_PASSKEY` | Your live Daraja passkey | |
| `MPESA_CALLBACK_URL` | `https://nyumbahubtapinn.co.ke/api/payments/callback/` | Must be public HTTPS |
| `MPESA_TIMEOUT` | `30` | |
| `MPESA_FALLBACK_ON_TIMEOUT` | `False` | Production: don't simulate |
| `MPESA_AUTO_CONFIRM_SIMULATION` | `False` | Production: don't simulate |
| `JWT_ACCESS_LIFETIME_MINUTES` | `60` | |
| `JWT_REFRESH_LIFETIME_DAYS` | `7` | |
| `GEOCODING_NOMINATIM_USER_AGENT` | `NyumbaHub-StudentHousing/1.0 (admin@nyumbahub.test)` | |

> 🔐 **Never** commit real secrets to GitHub. The `.env` file is gitignored — inject all secrets via Railway Variables only.

---

## Step 6: Deploy

1. In the Railway dashboard, your project should start building automatically once variables are set
2. If not, click **Deployments** → **Deploy latest**
3. Railway will:
   - Build the Docker image
   - Run `release: python manage.py migrate --noinput` (applies migrations to PostgreSQL)
   - Start `web: gunicorn ...` on Railway's port
4. When done, Railway gives you a URL like: `https://nyumbahub-xxx.up.railway.app`

---

## Step 7: Add your custom domain (`nyumbahubtapinn.co.ke`)

1. In Railway dashboard → **Settings** → **Domains**
2. Click **Add Domain** → enter `nyumbahubtapinn.co.ke`
3. Railway will show you DNS records to add (CNAME / A records)
4. Add those records at your domain registrar (where you bought `nyumbahubtapinn.co.ke`)
5. Wait for DNS to propagate (minutes to hours)

> ⚠️ You need access to the domain registrar's DNS settings. If you don't have access, you can still test on the Railway-provided URL (`*.up.railway.app`) and add the custom domain later.

---

## Step 8: Verify the deployment

Open these URLs in your browser:

| URL | What to check |
|-----|---------------|
| `https://<your-domain>/` | Homepage loads |
| `https://<your-domain>/api/properties/` | API returns JSON list of properties |
| `https://<your-domain>/admin/` | Django admin login works |
| `https://<your-domain>/api/auth/login/` | Login endpoint responds |

**Demo login credentials** (already seeded in the database if migrations ran):

| Role | Username | Password |
|------|----------|----------|
| Landlord | `demo_landlord` | `DemoLandlord123!` |
| Tenant | `demo_tenant` | `DemoTenant123!` |

> 📝 If the database is empty, run `python manage.py create_demo_users` and seed properties locally, then push — or ask the contributor to seed the database before you deploy.

---

## Step 9: Post-deploy security checklist

- [ ] `DEBUG = False`
- [ ] `DJANGO_SECRET_KEY` is strong and unique (not the dev default)
- [ ] `ALLOWED_HOSTS` contains only your real domains
- [ ] `CSRF_TRUSTED_ORIGINS` and `CORS_ALLOWED_ORIGINS` use `https://`
- [ ] `SECURE_SSL_REDIRECT = True`
- [ ] M-Pesa uses **live** credentials (`MPESA_ENVIRONMENT=production`), not sandbox
- [ ] `MPESA_AUTO_CONFIRM_SIMULATION = False`
- [ ] `USE_S3 = True` with real bucket credentials (images won't persist without it)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Build fails | Check Railway **Deployments** → **Logs** for the error |
| `DATABASE_URL` missing | Make sure you added the PostgreSQL service in Step 3 |
| Images disappear after redeploy | You must set `USE_S3=True` and configure S3/R2 (Step 5) |
| M-Pesa payments fail | Use live Daraja credentials, not sandbox; set `MPESA_ENVIRONMENT=production` |
| Custom domain not resolving | Verify DNS records at your registrar; wait for propagation |

---

## Files already in the repo (for reference)

| File | Purpose |
|------|---------|
| `Dockerfile` | Container build instructions |
| `Procfile` | Railway release (`migrate`) + web (`gunicorn`) commands |
| `docker-compose.yml` | Local dev stack (Django + PostgreSQL + Redis + cloudflared) |
| `config/settings.py` | Production-ready Django settings |
| `.env.example` | Template of all environment variables |
| `DEPLOY_RAILWAY.md` | Technical deploy runbook |
| `DEPLOYMENT_GUIDE.md` | This guide |

---

## Need help?

Ask the contributor who pushed this code — they can clarify any part of the setup. Once deployed, NyumbaHub will be live at your Railway URL and (after DNS) at `https://nyumbahubtapinn.co.ke`.
