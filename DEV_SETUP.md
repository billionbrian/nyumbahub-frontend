# Developer Setup Guide: TapIn Platform

Welcome to the **TapIn** development team. This document provides a comprehensive, step-by-step walkthrough for configuring your local development environment from repository cloning to having the full-stack Django and client application running smoothly.

---

## Table of Contents

1. [System Prerequisites](#1-system-prerequisites)
2. [Step 1: Clone the Repository](#step-1-clone-the-repository)
3. [Step 2: Create and Activate a Virtual Environment](#step-2-create-and-activate-a-virtual-environment)
   - [Linux & macOS](#linux--macos)
   - [Windows (PowerShell)](#windows-powershell)
   - [Windows (Command Prompt)](#windows-command-prompt)
4. [Step 3: Install Project Dependencies](#step-3-install-project-dependencies)
5. [Step 4: Environment Variables Configuration](#step-4-environment-variables-configuration)
6. [Step 5: Database Setup & Migrations](#step-5-database-setup--migrations)
   - [Apply Database Migrations](#apply-database-migrations)
   - [Seed Demo Landlord and Tenant Accounts](#seed-demo-landlord-and-tenant-accounts)
   - [Create an Administrative Superuser](#create-an-administrative-superuser)
7. [Step 6: Collect Static Assets](#step-6-collect-static-assets)
8. [Step 7: Launch the Development Server](#step-7-launch-the-development-server)
9. [Step 8: Verify Application Access](#step-8-verify-application-access)
10. [Step 9: Running Tests and System Checks](#step-9-running-tests-and-system-checks)
11. [Troubleshooting & Frequently Encountered Issues](#troubleshooting--frequently-encountered-issues)

---

## 1. System Prerequisites

Ensure the following tools are installed on your workstation prior to beginning setup:

- **Git**: Version 2.30 or higher ([Download Git](https://git-scm.com/downloads))
- **Python**: Version 3.10, 3.11, or 3.12 ([Download Python](https://www.python.org/downloads/))
  - *Windows note*: When running the Python installer, ensure the checkbox **"Add Python to PATH"** is checked.
- **pip**: Package installer for Python (bundled with standard Python installations)

Verify your installations in your terminal:

```bash
# Verify Git
git --version

# Verify Python
python --version    # or: python3 --version

# Verify Pip
pip --version       # or: python -m pip --version
```

---

## Step 1: Clone the Repository

Clone the project repository to your local workspace and navigate into the project directory:

### Linux / macOS:
```bash
git clone https://github.com/billionbrian/nyumbahub-frontend.git tapin
cd tapin
```

### Windows (PowerShell or Command Prompt):
```cmd
git clone https://github.com/billionbrian/nyumbahub-frontend.git tapin
cd tapin
```

---

## Step 2: Create and Activate a Virtual Environment

Always maintain an isolated virtual environment to avoid package dependency conflicts with system-level Python libraries.

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

# 2. (Optional) If script execution is restricted on your machine, permit local scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 3. Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

*Upon activation, your PowerShell prompt will display `(venv)`.*

---

### Windows (Command Prompt)

```cmd
# 1. Create a virtual environment named 'venv'
python -m venv venv

# 2. Activate the virtual environment
venv\Scripts\activate.bat
```

*Upon activation, your command line prompt will display `(venv)`.*

---

## Step 3: Install Project Dependencies

With the virtual environment active, ensure `pip` is up to date, then install all project requirements specified in `requirements.txt`:

### Linux / macOS:
```bash
# Upgrade pip to the latest release
python3 -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

### Windows:
```cmd
# Upgrade pip to the latest release
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

Key dependencies installed include:
- `Django 6.0+`: Core web framework
- `djangorestframework`: REST API framework
- `djangorestframework-simplejwt` & `PyJWT`: JSON Web Token authentication
- `django-cors-headers`: Cross-Origin Resource Sharing handler
- `requests`: External HTTP client (Daraja M-Pesa & Nominatim geocoding)
- `python-dotenv`: Environment configuration parser

---

## Step 4: Environment Variables Configuration

Copy the example environment configuration template into your local `.env` file:

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

Review and adjust the generated `.env` file if necessary:

```env
# TapIn Environment Configuration
DEBUG=True
SECRET_KEY=django-insecure-development-key-change-in-production

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

> **Security Note:** Never commit your production `.env` file to version control. The `.gitignore` is pre-configured to exclude `.env`.

---

## Step 5: Database Setup & Migrations

TapIn utilizes SQLite (`db.sqlite3`) for local development by default, requiring zero external database daemon configuration.

### Apply Database Migrations

Execute the migrations to initialize the database schema for authentication, user management, property listings, and payment models:

```bash
python manage.py migrate
```

Expected terminal output:
```text
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, payments, properties, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying properties.0001_initial... OK
  Applying payments.0001_initial... OK
```

---

### Seed Demo Landlord and Tenant Accounts

TapIn includes a built-in management command to automatically provision test accounts:

```bash
python manage.py create_demo_users
```

This provisions two pre-configured developer accounts:

| Role | Username | Email | Password | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Landlord** | `demo_landlord` | `demo_landlord@tapin.test` | `DemoLandlord123!` | Create, update, and manage property listings |
| **Tenant** | `demo_tenant` | `demo_tenant@tapin.test` | `DemoTenant123!` | Browse, save favorites, simulate bookings |

---

### Create an Administrative Superuser

To access the Django Admin interface at `/admin/`, create a local superuser:

```bash
python manage.py createsuperuser
```

Follow the prompts to enter your username, email, and password.

---

## Step 6: Collect Static Assets

Compile and sync all static frontend assets (HTML templates, styling, scripts, and media handlers):

```bash
python manage.py collectstatic --noinput
```

This synchronizes client assets to the `staticfiles/` directory served by Django.

---

## Step 7: Launch the Development Server

Start the Django local development server:

```bash
python manage.py runserver
```

When successful, your console will output:

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

Open your web browser and navigate to the following endpoints to verify full platform operation:

| Portal / View | Local URL | Description |
| :--- | :--- | :--- |
| **Home / Discovery** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Main property search, filtering, and listings |
| **Interactive Map** | [http://127.0.0.1:8000/map.html](http://127.0.0.1:8000/map.html) | Leaflet/OSM geospatial pin explorer |
| **Authentication** | [http://127.0.0.1:8000/login.html](http://127.0.0.1:8000/login.html) | Sign-in portal for tenants and landlords |
| **Property Management** | [http://127.0.0.1:8000/add-property.html](http://127.0.0.1:8000/add-property.html) | Landlord property creation and editing |
| **Django Admin** | [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) | Backend database administration |
| **API Endpoints** | [http://127.0.0.1:8000/api/properties/](http://127.0.0.1:8000/api/properties/) | RESTful API data feeds |

---

## Step 9: Running Tests and System Checks

Run automated test suites and framework validation to ensure code integrity:

```bash
# 1. Run Django System Integrity Check
python manage.py check

# 2. Run all unit and integration test suites
python manage.py test

# 3. Run individual application tests
python manage.py test accounts
python manage.py test properties
python manage.py test payments
```

---

## Troubleshooting & Frequently Encountered Issues

### 1. Windows: "File ... cannot be loaded because running scripts is disabled on this system"
- **Cause**: PowerShell execution policies default to `Restricted`.
- **Solution**: Open PowerShell as Current User and execute:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
  Then reactivate the virtual environment: `.\venv\Scripts\Activate.ps1`.

### 2. "Command 'python' not found" (Linux/macOS)
- **Cause**: Systems often alias Python 3 as `python3`.
- **Solution**: Use `python3` and `python3 -m pip` throughout commands, or configure an alias:
  ```bash
  alias python=python3
  ```

### 3. Port 8000 is Already in Use
- **Cause**: Another service or orphaned Django instance is occupying port 8000.
- **Solution**: Specify an alternative port when launching `runserver`:
  ```bash
  python manage.py runserver 8080
  ```
  Access the platform at `http://127.0.0.1:8080/`.

### 4. Database Lock / SQLite Errors (`sqlite3.OperationalError: database is locked`)
- **Cause**: Concurrent write locks or interrupted transactions.
- **Solution**: Stop all running Django processes (`Ctrl + C`), ensure no other terminal has an active Django shell, and restart `runserver`.

### 5. `ModuleNotFoundError: No module named '...'`
- **Cause**: Dependencies were installed globally or virtual environment is deactivated.
- **Solution**: Verify `(venv)` appears in your prompt, then run:
  ```bash
  pip install -r requirements.txt
  ```

---

## Need Further Help?

For architecture deep-dives and schema specifications, review:
- [BACKEND_ARCHITECTURE.md](docs/BACKEND_ARCHITECTURE.md)
- [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)
- [MPESA_INTEGRATION.md](docs/MPESA_INTEGRATION.md)

Welcome aboard, and happy developing with **TapIn**!
