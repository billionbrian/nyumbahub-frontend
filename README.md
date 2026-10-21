# NyumbaHub

TapInn — Tap into your next home

NyumbaHub is a full-stack housing marketplace for Kenyan university students, young professionals, and residential property owners. The platform connects verified landlords with prospective tenants through digital transparency, geolocation mapping, digital tenancy agreements, and Safaricom M-Pesa payment integration.

## Technology Stack

- **Framework**: Django 6.0.6, Python 3.10+
- **API**: Django REST Framework 3.17.1
- **Authentication**: simplejwt (JWT access and refresh tokens)
- **CORS**: django-cors-headers
- **Filtering**: django-filter, DRF SearchFilter and OrderingFilter
- **Database**: SQLite3 (development), PostgreSQL (production)
- **Payments**: Safaricom Daraja M-Pesa STK Push
- **Maps**: Leaflet, OpenStreetMap Nominatim, Komoot Photon
- **Frontend**: HTMX, Django templates, Leaflet.js, Chart.js

## Key Features

- **Property discovery**: Search and filter listings by price, type, bedrooms, and location
- **Interactive map**: Leaflet-powered map with property markers and pricing
- **M-Pesa checkout**: STK Push payment initiation with status polling
- **Landlord management**: Role-gated property creation, editing, and deletion
- **Digital tenancy agreements**: Lease templates with signature capture
- **Theme system**: Light, dark, and system auto modes

## Project Structure

```
nyumbahub/
├── config/              # Django project settings, URLs, and views
├── accounts/            # User authentication (landlord, tenant roles)
├── properties/          # Property listings and images
├── payments/            # M-Pesa Daraja payment integration
├── frontend/            # HTML templates, CSS, and JavaScript
├── docs/                # API, architecture, database, and M-Pesa docs
├── DEV_SETUP.md         # Local development setup guide
├── requirements.txt     # Python dependencies
├── manage.py            # Django management utility
└── .env.example         # Environment variable template
```

## Quickstart

1. Clone the repository
   ```bash
   git clone git@github.com:billionbrian/nyumbahub-frontend.git nyumbahub
   cd nyumbahub
   ```

2. Create and activate a virtual environment
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Configure environment variables
   ```bash
   cp .env.example .env
   ```

4. Set up the database
   ```bash
   python manage.py migrate
   python manage.py create_demo_users
   ```

5. Launch the server
   ```bash
   python manage.py collectstatic --noinput
   python manage.py runserver
   ```

Open http://127.0.0.1:8000/ in your browser.

### Demo accounts

| Role | Username | Password |
|------|----------|----------|
| Landlord | demo_landlord | DemoLandlord123! |
| Tenant | demo_tenant | DemoTenant123! |

## API Reference

### Authentication (`/api/auth/`)
- `POST /signup/` — Register a new user
- `POST /login/` — Authenticate and receive JWT tokens
- `GET /me/` — Get current user profile (auth required)
- `PATCH /me/` — Update user profile (auth required)
- `POST /token/refresh/` — Refresh access token
- `POST /logout/` — Logout (auth required)

### Properties (`/api/properties/`)
- `GET /` — List properties with filtering and pagination
- `POST /` — Create a property listing (landlord only)
- `GET /{id}/` — Retrieve a single property
- `PUT` / `PATCH` /{id}/` — Update a property (owner only)
- `DELETE` /{id}/` — Delete a property (owner only)
- `GET /mine/` — List landlord's own properties

### Payments (`/api/payments/`)
- `POST /initiate/` — Initiate M-Pesa STK Push
- `GET /status/{checkout_id}/` — Check payment status
- `POST /callback/` — Safaricom webhook callback
- `POST /simulate-callback/` — Sandbox simulation for local testing

## Tests

```bash
python manage.py check
python manage.py test
```

## Deployment

See DEPLOYMENT_GUIDE.md for Railway deployment instructions.

## License

All rights reserved. Copyright 2026 NyumbaHub.
