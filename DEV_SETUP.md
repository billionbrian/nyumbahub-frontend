# Developer Setup Guide — NyumbaHub

End-to-end setup for the NyumbaHub Django application on Linux, macOS, and Windows.

## System prerequisites

Verify the following are installed:

- **Git** 2.30 or higher
- **Python** 3.10, 3.11, or 3.12
- **pip** (bundled with Python)

Verify installations:

```bash
git --version
python3 --version
pip3 --version
```

## Step 1: Clone the repository

```bash
git clone git@github.com:billionbrian/nyumbahub-frontend.git nyumbahub
cd nyumbahub
```

Or via HTTPS:

```bash
git clone https://github.com:billionbrian/nyumbahub-frontend.git nyumbahub
cd nyumbahub
```

## Step 2: Create and activate a virtual environment

Use an isolated virtual environment to avoid dependency conflicts.

### Linux and macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows (PowerShell)

```powershell
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### Windows (Command Prompt)

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

## Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Core packages include Django 6.0.6, Django REST Framework, simplejwt, django-cors-headers, django-filter, psycopg2-binary, requests, and python-dotenv.

## Step 4: Configure environment variables

Copy the example template:

```bash
cp .env.example .env
```

Edit `.env` with your local values. The file is gitignored to prevent leaking secrets.

## Step 5: Database setup and migrations

NyumbaHub uses SQLite3 for local development.

```bash
python manage.py migrate
```

### Provision demo accounts

```bash
python manage.py create_demo_users
```

This creates:

| Role | Username | Password |
|------|----------|----------|
| Landlord | demo_landlord | DemoLandlord123! |
| Tenant | demo_tenant | DemoTenant123! |

### Create a superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account for the Django admin panel.

## Step 6: Collect static assets

```bash
python manage.py collectstatic --noinput
```

This synchronizes static files to `staticfiles/`.

## Step 7: Launch the development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Step 8: Verify application access

| Feature | URL |
|---------|-----|
| Home | http://127.0.0.1:8000/ |
| Interactive map | http://127.0.0.1:8000/map.html |
| Sign in | http://127.0.0.1:8000/login.html |
| Create listing | http://127.0.0.1:8000/add-property.html |
| Digital lease | http://127.0.0.1:8000/digital-agreement.html |
| Django admin | http://127.0.0.1:8000/admin/ |
| REST API | http://127.0.0.1:8000/api/properties/ |

## Step 9: Testing and code validation

```bash
python manage.py check
python manage.py test
python manage.py test accounts
python manage.py test properties
python manage.py test payments
```

## Troubleshooting

**PowerShell script execution disabled**

Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**`python` command not found on Linux/macOS**

Use `python3` instead of `python`, or add an alias to your shell profile.

**Port 8000 in use**

Run: `python manage.py runserver 8080`

**Database locked**

Stop all running Django servers and restart.

**Module not found: rest_framework**

Activate the virtual environment and run `pip install -r requirements.txt`.

## Additional documentation

- README.md — Platform overview and API reference
- docs/BACKEND_ARCHITECTURE.md — Architecture deep-dive
- docs/API_DOCUMENTATION.md — REST endpoint specification
- docs/DATABASE_SCHEMA.md — Database schema reference
- docs/MPESA_INTEGRATION.md — Safaricom Daraja M-Pesa integration guide
