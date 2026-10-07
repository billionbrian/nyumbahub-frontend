# 🏠 NyumbaHub
### *TapInn • Tap into your next home*

[![Django](https://img.shields.io/badge/Django-6.0.6-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.17.1-A30000?style=for-the-badge&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Safaricom Daraja](https://img.shields.io/badge/M--Pesa-Daraja_STK_Push-00A651?style=for-the-badge&logo=safepal&logoColor=white)](https://developer.safaricom.co.ke/)
[![HTMX](https://img.shields.io/badge/HTMX-2.x-3366CC?style=for-the-badge&logo=htmx&logoColor=white)](https://htmx.org/)
[![Leaflet](https://img.shields.io/badge/Maps-Leaflet_&_OSM-199900?style=for-the-badge&logo=leaflet&logoColor=white)](https://leafletjs.com/)

---

## 📌 Overview

**NyumbaHub** (powered by **TapInn**) is a production-ready, full-stack housing marketplace designed specifically for Kenyan university students, young professionals, and residential property owners. The platform bridges the gap between verified landlords and prospective tenants, eliminating middlemen exploitation, viewing fees, and rental fraud through digital transparency, real-time geolocation mapping, automated digital tenancy agreements, and direct Safaricom M-Pesa payment integration.

---

## 🛠 Exact Technology Stack

The platform is engineered with a unified, single-origin architecture where the **Django REST Framework** backend powers both headless REST APIs and efficiently serves the hypermedia-driven client frontend.

### Backend & API
- **Framework**: Python 3.10+ / [Django 6.0.6](https://docs.djangoproject.com/en/6.0/)
- **API Engine**: [Django REST Framework (DRF) 3.17.1](https://www.django-rest-framework.org/)
- **Authentication**: [djangorestframework-simplejwt 5.5.1](https://django-rest-framework-simplejwt.readthedocs.io/) & [PyJWT 2.13.0](https://pyjwt.readthedocs.io/) (Stateless JWT Access & Refresh tokens)
- **CORS Handling**: [django-cors-headers 4.9.0](https://github.com/adamchainz/django-cors-headers)
- **Filtering & Search**: [django-filter 24.3](https://django-filter.readthedocs.io/) and DRF `SearchFilter` / `OrderingFilter`
- **ASGI & Parsing**: `asgiref 3.11.1` and `sqlparse 0.5.5`

### Database & ORM
- **Development**: [SQLite3](https://www.sqlite.org/) (`db.sqlite3` with zero setup required)
- **Production Adapter**: [psycopg2-binary 2.9.12](https://www.psycopg.org/) (ready for PostgreSQL)
- **Object-Relational Mapping**: Django ORM with customized models and optimized indexing

### Payment & External Services
- **Payment Gateway**: **Safaricom Lipa Na M-Pesa Online (Daraja API STK Push)**
  - Automated STK Push generation
  - Webhook callback listener (`/api/payments/callback/`)
  - Status polling mechanism (`/api/payments/status/<checkout_id>/`)
  - Automatic sandbox timeout handling and simulation fallback
- **Geocoding & Maps**:
  - [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/) for reverse and forward address resolution
  - [Komoot Photon](https://photon.komoot.io/) for fast location autocomplete
  - Configurable User-Agent settings in `config.settings`

### Frontend Client Architecture
- **Single-Origin Delivery**: Static templates served seamlessly via Django routing (`config.views.serve_frontend_file`)
- **Hypermedia Engine**: [HTMX 2.x](https://htmx.org/) with `head-support.js` for SPA-like transitions, modal swaps, and full browser history
- **Interactive Geospatial Maps**: [Leaflet.js](https://leafletjs.com/) with custom SVG house teardrop pins, popups, and coordinate drag-and-drop
- **Theme Management Engine**: Native CSS Custom Properties supporting **Light**, **Dark**, and **System Auto** modes with instant persistence
- **Digital Leases**: HTML5 Canvas Signature Pad for legally-binding digital tenancy lease signing
- **Analytics & Dashboards**: [Chart.js](https://www.chartjs.org/) for landlord listing performance metrics

---

## 🌟 Key Platform Features

### 1. 🔍 Tenant Property Discovery & Search
- Multi-criteria real-time filtering: Price range (KES), property types (`single`, `bedsitter`, `one_bedroom`, `two_bedroom`, `three_bedroom`, `apartment`, `villa`), bedrooms, and availability.
- Full-text search matching property titles, descriptions, and neighborhood locations.
- Client-side saved properties (favorites) stored locally with instant access.

### 2. 🗺 Interactive Campus Housing Map (`/map.html`)
- Geospatial mapping powered by Leaflet & OpenStreetMap.
- Custom interactive property markers displaying rent prices, thumbnails, and room specs.
- Accurate commute indicators for university hubs (Nairobi, Westlands, Juja, Eldoret, etc.).

### 3. 💳 Safaricom M-Pesa STK Push Checkout (`/api/payments/`)
- Direct in-app booking deposit initiation via Safaricom STK Push prompt sent straight to the tenant's handset.
- Real-time client polling verifies payment completion against Safaricom callback receipts.
- Automatic locking: Successfully booked properties automatically transition to `status='booked'` (`available=False`).
- Offline / Sandbox Fallback: Automatic developer simulation when Safaricom sandbox servers experience downtime.

### 4. 🏢 Landlord Property Management (`/add-property.html` & `/account.html`)
- Dedicated role-gated property creation and editing suite.
- Image uploads with automatic thumbnail generation and primary photo selection.
- Point-and-click coordinate placement with automatic reverse geocoding to address text.
- Protected landlord endpoints: Landlords can only modify or delete listings they own (`/api/properties/mine/`).

### 5. ✍️ Digital Tenancy Agreements (`/digital-agreement.html`)
- Standardized, enforceable residential lease agreement templates.
- Dual touch/mouse signature capture for landlords and tenants.

### 6. 🌓 Theme System & Mobile Drawer
- Dark, Light, and System Auto theme switcher integrated with zero flicker.
- Fully responsive mobile navigation rail and quick-action bottom tab bar.
- Header branding featuring **NyumbaHub** and the **TapInn** signature tagline (*"Tap into your next home"*).

---

## 📂 Project Directory Structure

```text
nyumbahub/
├── config/                                 # Project orchestration & Django core
│   ├── settings.py                         # Settings (JWT, CORS, Daraja, Geocoding)
│   ├── urls.py                             # Root routing & frontend delivery
│   ├── views.py                            # serve_frontend_file fallback router
│   ├── asgi.py                             # ASGI specification
│   └── wsgi.py                             # WSGI production specification
│
├── accounts/                               # User authentication & identity app
│   ├── models.py                           # Custom User model (roles: landlord, tenant)
│   ├── serializers.py                      # User serializers & validation
│   ├── views.py                            # signup, LoginView, current_user, logout
│   ├── urls.py                             # /api/auth/ routing
│   └── management/commands/                # Built-in provisioning commands
│       └── create_demo_users.py            # Automated demo test accounts command
│
├── properties/                             # Property listings & inventory app
│   ├── models.py                           # Property & PropertyImage models
│   ├── serializers.py                      # Property serialization & nested images
│   ├── views.py                            # PropertyViewSet (CRUD, filtering, mine)
│   ├── permissions.py                      # IsLandlord, IsPropertyOwner permissions
│   ├── urls.py                             # /api/properties/ router
│   └── services/
│       └── geocoding.py                    # Nominatim OSM reverse geocoding service
│
├── payments/                               # Daraja M-Pesa transactions app
│   ├── models.py                           # Payment transaction model & receipt records
│   ├── serializers.py                      # Payment validation serializers
│   ├── views.py                            # initiate_payment, mpesa_callback, payment_status
│   ├── urls.py                             # /api/payments/ routing
│   └── services/
│       └── daraja.py                       # Safaricom Daraja STK Push API integration
│
├── frontend/                               # Client templates and static source
│   ├── index.html                          # Main discovery feed and property search
│   ├── map.html                            # Interactive full-screen Leaflet housing map
│   ├── property-detail.html                # Unit details, WhatsApp link, M-Pesa booking
│   ├── add-property.html                   # Landlord listing creation & editing portal
│   ├── account.html                        # User profile & landlord inventory manager
│   ├── login.html & signup.html            # Authentication portals
│   ├── digital-agreement.html              # Tenancy agreement generator with signature pad
│   ├── services.html, gallery.html...      # Static content pages
│   ├── components/                         # Shared UI blocks
│   │   ├── navbar.html                     # Header with TapInn branding & theme selector
│   │   └── footer.html                     # Standardized footer
│   ├── styles/                             # Global UI CSS library & design tokens
│   └── js/                                 # Client layout, HTMX, and auth scripts
│
├── staticfiles/                            # Production collected static files
├── media/                                  # Uploaded property images & attachments
├── docs/                                   # Supplementary architecture documentation
│   ├── API_DOCUMENTATION.md                # Comprehensive REST endpoint specification
│   ├── BACKEND_ARCHITECTURE.md             # In-depth architectural deep-dive
│   ├── DATABASE_SCHEMA.md                  # Table schemas & field reference
│   └── MPESA_INTEGRATION.md                # Safaricom Daraja integration guide
│
├── DEV_SETUP.md                            # Complete Windows & Linux setup walkthrough
├── requirements.txt                        # Pinned Python package dependencies
├── manage.py                               # Django execution utility
└── .env.example                            # Environment configuration template
```

---

## 🚀 Quickstart Guide

For an exhaustive, step-by-step onboarding guide for **Windows** (PowerShell & Command Prompt) and **Linux/macOS**, consult [DEV_SETUP.md](DEV_SETUP.md).

### 1. Clone the Repository
```bash
# Via SSH (Recommended)
git clone git@github.com:billionbrian/nyumbahub-frontend.git nyumbahub
cd nyumbahub

# Or via HTTPS
git clone https://github.com/billionbrian/nyumbahub-frontend.git nyumbahub
cd nyumbahub
```

### 2. Configure Virtual Environment & Dependencies

#### Linux & macOS:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
# Linux / macOS
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

### 4. Database Setup & Demo Data
```bash
# Run database migrations
python manage.py migrate

# Provision demo accounts (demo_landlord & demo_tenant)
python manage.py create_demo_users

# (Optional) Create an admin superuser
python manage.py createsuperuser
```

### 5. Collect Static Files & Launch
```bash
# Collect static assets
python manage.py collectstatic --noinput

# Start development server
python manage.py runserver
```

Open your browser at **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** to access the application.

---

## 🔑 Pre-Configured Test Accounts

Running `python manage.py create_demo_users` creates two ready-to-use accounts:

| Role | Username | Email | Password | Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **Landlord** | `demo_landlord` | `demo_landlord@nyumbahub.test` | `DemoLandlord123!` | Create, edit, and delete properties |
| **Tenant** | `demo_tenant` | `demo_tenant@nyumbahub.test` | `DemoTenant123!` | Browse, save listings, initiate M-Pesa payments |

---

## 📡 REST API Reference

All REST endpoints return JSON payloads and utilize standard HTTP status codes.

### Authentication Endpoints (`/api/auth/`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/signup/` | Register a new user (`tenant` or `landlord`) | No |
| `POST` | `/api/auth/login/` | Authenticate and obtain JWT access & refresh tokens | No |
| `GET` | `/api/auth/me/` | Retrieve currently authenticated user profile | Bearer Token |
| `PATCH` | `/api/auth/me/` | Update user profile (phone, names, email) | Bearer Token |
| `POST` | `/api/auth/token/refresh/` | Obtain a new access token using a refresh token | No |
| `POST` | `/api/auth/logout/` | Terminate session | Bearer Token |

### Property Endpoints (`/api/properties/`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/properties/` | List properties with filtering & pagination | No |
| `POST` | `/api/properties/` | Create a new property listing (with image upload) | Landlord Only |
| `GET` | `/api/properties/{id}/` | Retrieve full details for a single property | No |
| `PUT` / `PATCH` | `/api/properties/{id}/` | Update an existing property | Property Owner |
| `DELETE` | `/api/properties/{id}/` | Remove a property listing | Property Owner |
| `GET` | `/api/properties/mine/` | Retrieve listings belonging to logged-in landlord | Landlord Only |

#### Query Parameters for Property Filtering
- `search`: Keyword search matching title, location, description (e.g. `?search=westlands`)
- `min_price` & `max_price`: Price range in KES (e.g. `?min_price=10000&max_price=30000`)
- `property_type`: Filter by type (`single`, `bedsitter`, `one_bedroom`, `two_bedroom`, `three_bedroom`, `apartment`, `villa`)
- `bedrooms`: Number of bedrooms (e.g. `?bedrooms=2`)
- `status`: `available`, `booked`, or `maintenance`
- `page` & `page_size`: Pagination control (default page size: 12)

### Payment Endpoints (`/api/payments/`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/payments/initiate/` | Initiate Daraja M-Pesa STK Push prompt | Optional |
| `GET` | `/api/payments/status/{checkout_id}/` | Query status of initiated STK Push transaction | No |
| `POST` | `/api/payments/callback/` | Safaricom Daraja webhook callback endpoint | No (Public) |
| `POST` | `/api/payments/simulate-callback/` | Sandbox simulation tool for local verification | No |

---

## ⚙️ Environment Variables Reference

Configure these variables inside your local `.env` file:

```env
# Core Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-for-development

# Geocoding Service Configuration
GEOCODING_NOMINATIM_USER_AGENT=NyumbaHub-StudentHousing/1.0 (admin@nyumbahub.test)

# Safaricom Daraja M-Pesa Configuration (Sandbox)
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your_daraja_consumer_key
MPESA_CONSUMER_SECRET=your_daraja_consumer_secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919
MPESA_CALLBACK_URL=https://sandbox.safaricom.co.ke/mpesa/
MPESA_TIMEOUT=30
MPESA_FALLBACK_ON_TIMEOUT=True
MPESA_AUTO_CONFIRM_SIMULATION=True
```

---

## 🧪 Running Automated Tests

Validate system integrity and application test suites:

```bash
# 1. System configuration check
python manage.py check

# 2. Run all tests
python manage.py test

# 3. Run individual module test suites
python manage.py test accounts
python manage.py test properties
python manage.py test payments
```

---

## 🤝 Contribution Guidelines

1. **Branching Strategy**: Branch off `main` using descriptive names:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```
2. **Code Standards**: Maintain PEP 8 compliance, write descriptive commit messages, and ensure static assets compile cleanly.
3. **Verify Integrity**: Always execute `python manage.py check` and run test suites before submitting pull requests.

---

## 📄 License & Attribution

Developed with passion by the **NyumbaHub** engineering team. All rights reserved &copy; 2026.
