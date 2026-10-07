# 🛠 Developer Setup Guide: NyumbaHub Platform
### *TapInn • Tap into your next home*

Welcome to the **NyumbaHub** engineering team. This guide provides an end-to-end, reproducible setup walkthrough to configure your local development environment on **Linux**, **macOS**, and **Windows** (PowerShell & Command Prompt), from repository cloning to having the full-stack Django application, database, and client running smoothly.

---

## Table of Contents

1. [System Prerequisites](#1-system-prerequisites)
2. [Step 1: Clone the Repository](#step-1-clone-the-repository)
3. [Step 2: Create and Activate a Virtual Environment](#step-2-create-and-activate-a-virtual-environment)
   - [Linux & macOS](#linux--macos)
   - [Windows (PowerShell)](#windows-powershell)
   - [Windows (Command Prompt)](#windows-command-prompt)
4. [Step 3: Install Project Dependencies](#step-3-install-project-dependencies)
5. [Step 4: Environment Variables Configuration (`.env`)](#step-4-environment-variables-configuration-env)
6. [Step 5: Database Setup & Migrations](#step-5-database-setup--migrations)
   - [Apply Database Migrations](#apply-database-migrations)
   - [Provision Demo Accounts](#provision-demo-accounts)
   - [Create an Administrative Superuser](#create-an-administrative-superuser)
7. [Step 6: Collect Static Assets](#step-6-collect-static-assets)
8. [Step 7: Launch the Development Server](#step-7-launch-the-development-server)
9. [Step 8: Verify Application Access](#step-8-verify-application-access)
10. [Step 9: Testing & Code Validation](#step-9-testing--code-validation)
11. [Troubleshooting & Frequently Encountered Issues](#troubleshooting--frequently-encountered-issues)

---

## 1. System Prerequisites

Before starting, verify that the following utilities are installed on your system:

- **Git**: Version 2.30 or higher ([Download Git](https://git-scm.com/downloads))
- **Python**: Version 3.10, 3.11, or 3.12 ([Download Python](https://www.python.org/downloads/))
  - *Windows note*: During installation, ensure the checkbox **"Add Python to PATH"** is selected.
- **pip**: Standard package installer for Python (bundled with Python).

Verify your local installation in your terminal:

```bash
# Verify Git
git --version

# Verify Python (should output 3.10.x, 3.11.x, or 3.12.x)
python --version    # On Linux/macOS: python3 --version

# Verify Pip
pip --version       # On Linux/macOS: python3 -m pip --version
```

---

## Step 1: Clone the Repository

Clone the project repository to your local workspace:

### Linux / macOS:
```bash
# Via SSH (Recommended)
git clone git@github.com:billionbrian/nyumbahub-frontend.git nyumbahub
cd nyumbahub

# Or via HTTPS
git clone https://github.com/billionbrian/nyumbahub-frontend.git nyumbahub
cd nyumbahub
```

### Windows (PowerShell or Command Prompt):
```cmd
:: Via SSH (Recommended)
git clone git@github.com:billionbrian/nyumbahub-frontend.git nyumbahub
cd nyumbahub

:: Or via HTTPS
git clone https://github.com/billionbrian/nyumbahub-frontend.git nyumbahub
cd nyumbahub
```

---

## Step 2: Create and Activate a Virtual Environment

Always maintain an isolated virtual environment to avoid dependency conflicts.

### Linux & macOS

```bash
# 1. Create a virtual environment named 'venv'
python3 -m venv venv

# 2. Activate the virtual environment
source venv/bin/activate
```

*Upon activation, your terminal prompt will be prefixed with `(venv)`.*

---

### Windows (PowerShell)

```powershell
# 1. Create a virtual environment named 'venv'
python -m venv venv

# 2. (If script execution is restricted on your workstation, enable local scripts)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

*Upon activation, your PowerShell prompt will display `(venv)`.*

---

### Windows (Command Prompt `cmd.exe`)

```cmd
:: 1. Create a virtual environment named 'venv'
python -m venv venv

:: 2. Activate the virtual environment
venv\Scripts\activate.bat
```

*Upon activation, your Command Prompt will display `(venv)`.*

---

## Step 3: Install Project Dependencies

With your virtual environment active, upgrade `pip` and install all pinned packages:

### Linux / macOS:
```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows:
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Core Packages Installed:
- **`Django 6.0.6`**: Web framework powering models, views, and routing.
- **`djangorestframework 3.17.1`**: RESTful API framework and serialization.
- **`djangorestframework-simplejwt 5.5.1` & `PyJWT 2.13.0`**: Stateless JSON Web Token authentication.
- **`django-cors-headers 4.9.0`**: Cross-Origin Resource Sharing middleware.
- **`django-filter 24.3`**: Flexible URL query parameter filtering.
- **`psycopg2-binary 2.9.12`**: PostgreSQL database connector (production-ready).
- **`requests >= 2.31.0`**: External HTTP client (Daraja M-Pesa & Nominatim geocoding).
- **`python-dotenv >= 1.0.0`**: Environment variable loading.

---

## Step 4: Environment Variables Configuration (`.env`)

Copy the provided example environment template into your local `.env`:

### Linux / macOS:
```bash
cp .env.example .env
```

### Windows (PowerShell):
```powershell
Copy-Item .env.example .env
```

### Windows (Command Prompt):
```cmd
copy .env.example .env
```

Your default `.env` is pre-configured for sandbox development:

```env
# Core Django
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production

# OpenStreetMap Nominatim User Agent
GEOCODING_NOMINATIM_USER_AGENT=NyumbaHub-StudentHousing/1.0 (admin@nyumbahub.test)

# Safaricom Daraja API Configuration (Sandbox)
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your_sandbox_consumer_key
MPESA_CONSUMER_SECRET=your_sandbox_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://sandbox.safaricom.co.ke/mpesa/
MPESA_TIMEOUT=30
MPESA_FALLBACK_ON_TIMEOUT=True
MPESA_AUTO_CONFIRM_SIMULATION=True
```

> **Note:** `.env` is ignored by `.gitignore` to prevent leaking secrets.

---

## Step 5: Database Setup & Migrations

NyumbaHub uses SQLite3 (`db.sqlite3`) for local development by default, requiring no database daemon setup.

### Apply Database Migrations

Initialize database schemas across `accounts`, `properties`, and `payments`:

```bash
python manage.py migrate
```

---

### Provision Demo Accounts

Run the custom management command to provision pre-configured test users:

```bash
python manage.py create_demo_users
```

This creates:
- **Landlord**: `demo_landlord` (`demo_landlord@nyumbahub.test` / `DemoLandlord123!`)
- **Tenant**: `demo_tenant` (`demo_tenant@nyumbahub.test` / `DemoTenant123!`)

---

### Create an Administrative Superuser

To access the Django Admin panel at `/admin/`:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter a username, email, and password.

---

## Step 6: Collect Static Assets

Compile and sync static files (HTML templates, CSS styles, JavaScript, and fonts):

```bash
python manage.py collectstatic --noinput
```

This synchronizes client assets to `staticfiles/` which Django serves during development and production.

---

## Step 7: Launch the Development Server

Start the Django local development server:

```bash
python manage.py runserver
```

You should see:
```text
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
Django version 6.0.6, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

---

## Step 8: Verify Application Access

Navigate to the local URLs below to test key platform features:

| Feature / Page | URL | Description |
| :--- | :--- | :--- |
| **Main Portal / Home** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Property search, filters, cards, and TapInn header branding |
| **Interactive Map** | [http://127.0.0.1:8000/map.html](http://127.0.0.1:8000/map.html) | Leaflet/OSM geospatial map with custom teardrop pins |
| **Sign In** | [http://127.0.0.1:8000/login.html](http://127.0.0.1:8000/login.html) | Login with `demo_tenant` or `demo_landlord` |
| **Create Listing** | [http://127.0.0.1:8000/add-property.html](http://127.0.0.1:8000/add-property.html) | Landlord property management and photo uploader |
| **Digital Lease** | [http://127.0.0.1:8000/digital-agreement.html](http://127.0.0.1:8000/digital-agreement.html) | Tenancy agreement generator with signature canvas |
| **Django Admin** | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) | Database model inspection and superuser operations |
| **REST API** | [http://127.0.0.1:8000/api/properties/](http://127.0.0.1:8000/api/properties/) | Headless DRF endpoints with browsable API |

---

## Step 9: Testing & Code Validation

Before submitting any code changes, verify that all system checks and tests pass:

```bash
# 1. System check
python manage.py check

# 2. Run all tests
python manage.py test

# 3. Test individual apps
python manage.py test accounts
python manage.py test properties
python manage.py test payments
```

---

## Troubleshooting & Frequently Encountered Issues

### 1. Windows: "File ... cannot be loaded because running scripts is disabled on this system"
- **Cause**: PowerShell restricts script execution by default.
- **Solution**: Execute the following in PowerShell:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  Then reactivate: `.\venv\Scripts\Activate.ps1`.

### 2. "Command 'python' not found" (Linux / macOS)
- **Cause**: Python 3 is installed as `python3`.
- **Solution**: Use `python3` and `python3 -m pip`, or add an alias to your `~/.bashrc` / `~/.zshrc`:
  ```bash
  alias python=python3
  ```

### 3. Port 8000 in Use
- **Cause**: Another service or orphaned process is listening on port 8000.
- **Solution**: Start the server on an alternative port:
  ```bash
  python manage.py runserver 8080
  ```

### 4. Database Locked (`sqlite3.OperationalError: database is locked`)
- **Cause**: An active transaction or concurrent write is locking SQLite.
- **Solution**: Stop all active Django servers and shell sessions (`Ctrl + C`), then restart `runserver`.

### 5. `ModuleNotFoundError: No module named 'rest_framework'`
- **Cause**: The virtual environment is either inactive or dependencies were installed globally.
- **Solution**: Confirm `(venv)` is shown in your terminal prompt, then run `pip install -r requirements.txt`.

---

## Additional Documentation

- [README.md](README.md) - Platform Overview & API Reference
- [docs/BACKEND_ARCHITECTURE.md](docs/BACKEND_ARCHITECTURE.md) - Architectural Deep-Dive
- [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) - API Endpoints Specification
- [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Database Schema Reference
- [docs/MPESA_INTEGRATION.md](docs/MPESA_INTEGRATION.md) - Safaricom Daraja M-Pesa Integration Guide

Happy building with **NyumbaHub** & **TapInn**!
