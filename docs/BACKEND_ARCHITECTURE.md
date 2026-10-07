# Backend Architecture Report

## Overview

NyumbaHub backend is built using **Django 6.0.6** with **Django REST Framework (DRF)** to provide a robust RESTful API for the property listing platform. The architecture follows Django's Model-View-Template (MVT) pattern with REST API principles.

## Technology Stack

### Core Framework
- **Django 6.0.6**: Web framework providing ORM, authentication, admin panel, and core functionality
- **Django REST Framework 3.17.1**: Toolkit for building Web APIs with serializers, viewsets, and authentication
- **Python 3.12**: Programming language

### Authentication & Security
- **djangorestframework_simplejwt 5.5.1**: JWT (JSON Web Token) authentication implementation
- **PyJWT 2.13.0**: JWT encoding/decoding library
- **django-cors-headers 4.9.0**: CORS (Cross-Origin Resource Sharing) middleware for frontend integration

### Database
- **SQLite3**: Default database for development (db.sqlite3)
- **psycopg2-binary 2.9.12**: PostgreSQL adapter for production deployment
- **Django ORM**: Object-relational mapping for database operations

### Additional Dependencies
- **asgiref 3.11.1**: ASGI (Asynchronous Server Gateway Interface) reference implementation
- **sqlparse 0.5.5**: SQL parser for Django

## Project Structure

```
nyumbahub-frontend/
├── config/                 # Project configuration
│   ├── settings.py         # Django settings (database, auth, CORS, JWT)
│   ├── urls.py             # Main URL routing
│   ├── views.py            # Frontend file serving
│   ├── wsgi.py             # WSGI configuration for deployment
│   └── asgi.py             # ASGI configuration for async support
├── accounts/               # User authentication app
│   ├── models.py           # Custom User model
│   ├── serializers.py      # User data serialization
│   ├── views.py            # Authentication endpoints
│   ├── urls.py             # Auth URL routing
│   └── admin.py            # Admin configuration
├── properties/             # Property management app
│   ├── models.py           # Property model
│   ├── serializers.py      # Property data serialization
│   ├── views.py            # Property CRUD endpoints
│   ├── urls.py             # Property URL routing
│   └── admin.py            # Admin configuration
├── frontend/               # Static frontend files
├── staticfiles/            # Collected static files
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── db.sqlite3              # SQLite database (development)
```

## Application Architecture

### 1. Config Module (`config/`)
**Purpose**: Central configuration and routing

**Key Components**:
- **settings.py**: Contains all Django settings including:
  - Database configuration (SQLite for dev, PostgreSQL ready for prod)
  - JWT authentication settings (60min access token, 7-day refresh token)
  - CORS configuration for frontend-backend communication
  - Custom user model configuration
  - REST Framework authentication classes
- **urls.py**: Main URL dispatcher routing:
  - `/admin/` - Django admin panel
  - `/api/auth/` - Authentication endpoints
  - `/api/properties/` - Property CRUD endpoints
  - Frontend file serving for SPA
- **views.py**: Serves frontend static files (HTML, CSS, JS)

### 2. Accounts App (`accounts/`)
**Purpose**: User authentication and authorization

**Key Components**:
- **Custom User Model**: Extends Django's AbstractUser with:
  - `role`: User role (tenant/landlord)
  - `phone`: Phone number field
  - `created_at`: Timestamp
- **Serializers**:
  - `UserSerializer`: User data serialization
  - `SignupSerializer`: User registration with validation
  - `LoginSerializer`: JWT token generation with user data
- **Views**:
  - `signup`: User registration endpoint (POST)
  - `LoginView`: JWT login endpoint (POST)
  - `current_user`: Get authenticated user data (GET)
- **URL Routes**:
  - `/api/auth/signup/` - Register new user
  - `/api/auth/login/` - Login and get JWT token
  - `/api/auth/me/` - Get current user info

**Authentication Flow**:
1. User registers via `/api/auth/signup/` with username, email, password, role, phone
2. User logs in via `/api/auth/login/` with username/email and password
3. Server returns JWT access token (60min) and refresh token (7days)
4. Client includes token in Authorization header: `Bearer <token>`
5. Protected endpoints validate token and extract user context

### 3. Properties App (`properties/`)
**Purpose**: Property listing management

**Key Components**:
- **Property Model**: Contains:
  - `landlord`: Foreign key to User
  - `title`: Property title
  - `description`: Detailed description
  - `location`: Property location
  - `rent_amount`: Monthly rent (KES)
  - `bedrooms`: Number of bedrooms
  - `bathrooms`: Number of bathrooms
  - `property_type`: Type (apartment, house, studio, townhouse, villa)
  - `available`: Availability status
  - `created_at`: Timestamp
- **Serializers**:
  - `PropertySerializer`: Property data serialization with landlord info
  - Validation for rent_amount, bedrooms, bathrooms (must be > 0)
- **Views**:
  - `PropertyViewSet`: ModelViewSet with custom permissions
  - `IsLandlord`: Custom permission - user must be landlord
  - `IsPropertyOwner`: Custom permission - user must own the property
- **URL Routes**:
  - `/api/properties/` - List all properties (GET)
  - `/api/properties/<id>/` - Get single property (GET)
  - `/api/properties/` - Create property (POST, landlord only)
  - `/api/properties/<id>/` - Update property (PUT/PATCH, owner only)
  - `/api/properties/<id>/` - Delete property (DELETE, owner only)

**Permission System**:
- **List/Retrieve**: Public access (no authentication required)
- **Create**: Authenticated landlords only
- **Update/Delete**: Property owner only (landlord who created it)

## API Design Principles

### RESTful Conventions
- **HTTP Methods**: GET (retrieve), POST (create), PUT/PATCH (update), DELETE (delete)
- **Status Codes**: 
  - 200 OK - Successful GET/PUT/PATCH
  - 201 Created - Successful POST
  - 400 Bad Request - Validation errors
  - 401 Unauthorized - Missing/invalid token
  - 403 Forbidden - Insufficient permissions
  - 404 Not Found - Resource not found
  - 500 Internal Server Error - Server errors

### Authentication
- **JWT Token-based authentication** using SimpleJWT
- **Access Token**: 60 minutes lifetime
- **Refresh Token**: 7 days lifetime
- **Token Format**: Bearer token in Authorization header
- **Algorithm**: HS256

### CORS Configuration
- **Allowed Origins**: 
  - http://localhost:3000
  - http://127.0.0.1:3000
  - http://localhost:8000
  - http://127.0.0.1:8000
- **Credentials**: Enabled for cookie-based auth if needed

## Database Schema

### Users Table (auth_user)
- Inherits from Django AbstractUser
- Additional fields: role, phone, created_at
- Relationships: Has many properties (as landlord)

### Properties Table (properties_property)
- landlord (FK to User)
- title (CharField)
- description (TextField)
- location (CharField)
- rent_amount (DecimalField)
- bedrooms (IntegerField)
- bathrooms (IntegerField)
- property_type (CharField with choices)
- available (BooleanField)
- created_at (DateTimeField)

## Security Features

### Authentication
- Password hashing using Django's PBKDF2
- JWT token validation
- Token expiration (access: 60min, refresh: 7days)

### Authorization
- Role-based access control (tenant vs landlord)
- Object-level permissions (property ownership)
- Custom permission classes for fine-grained control

### CORS
- Configured allowed origins for frontend integration
- Credentials support for secure requests

### Input Validation
- Serializer-level validation for all inputs
- Field-level validation (e.g., rent_amount > 0)
- Role validation (must be 'tenant' or 'landlord')

## Deployment Considerations

### Development
- SQLite database
- DEBUG = True
- ALLOWED_HOSTS = ['*']
- Secret key in settings (should be environment variable in production)

### Production Requirements
- Switch to PostgreSQL
- Set DEBUG = False
- Configure ALLOWED_HOSTS with actual domain
- Use environment variables for SECRET_KEY
- Configure static files serving (whitenoise or CDN)
- Use HTTPS
- Configure CORS with production frontend URL
- Set up proper logging
- Use production WSGI server (Gunicorn/uWSGI)

## Logging
- Comprehensive logging in authentication views
- Error tracking with traceback
- Info logging for user actions (signup, login, validation)

## Frontend Integration
- Frontend served from Django backend
- SPA (Single Page Application) architecture
- All API calls to `/api/` endpoints
- Static files served from `frontend/` directory
- Fallback to index.html for client-side routing

## Future Enhancements
- Image upload for properties
- Advanced search and filtering
- Saved properties for tenants
- Messaging system between tenants and landlords
- Payment integration
- Property reviews and ratings
- Geolocation features
- Email notifications
- Password reset functionality
