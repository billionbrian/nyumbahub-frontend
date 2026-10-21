"""
Django settings for config project.

Production-ready for Railway deployment. Nearly every value is driven by
environment variables so the same codebase works in local dev and on Railway.
"""
import os
from pathlib import Path
from datetime import timedelta

import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env only for local development. Railway injects env vars directly.
load_dotenv(BASE_DIR / '.env')

# ---------------------------------------------------------------------------
# Core security
# ---------------------------------------------------------------------------
# In production this MUST come from the environment (never committed).
SECRET_KEY = os.getenv(
    'DJANGO_SECRET_KEY',
    'django-insecure-dev-only-change-me-in-production',
)

DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

# Comma-separated list in env, e.g. ALLOWED_HOSTS=nyumbahub.app,www.nyumbahub.app
ALLOWED_HOSTS = [h.strip() for h in os.getenv('ALLOWED_HOSTS', '*').split(',') if h.strip()]

# Must include scheme, e.g. CSRF_TRUSTED_ORIGINS=https://nyumbahub.app
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

# Custom user model
AUTH_USER_MODEL = 'accounts.User'

# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_filters',
    'whitenoise.runserver_nostatic',  # convenience for local runserver only
    'storages',                        # S3 / R2 media storage
    # Local apps
    'accounts',
    'properties',
    'payments',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # serve static files in prod
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ---------------------------------------------------------------------------
# Database — PostgreSQL on Railway (DATABASE_URL injected automatically)
# Falls back to SQLite for local dev when DATABASE_URL is absent.
# ---------------------------------------------------------------------------
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600,
        ssl_require=os.getenv('DB_SSL_REQUIRE', 'False').lower() in ('true', '1', 't'),
    )
}

# ---------------------------------------------------------------------------
# Sessions & cache
# ---------------------------------------------------------------------------
# SESSION_BACKEND=db   -> database-backed sessions (zero extra infra, recommended to start)
# SESSION_BACKEND=redis-> Redis sessions (scale upgrade; requires Railway Redis + django-redis)
SESSION_BACKEND = os.getenv('SESSION_BACKEND', 'db')

if SESSION_BACKEND == 'redis':
    REDIS_URL = os.getenv('REDIS_URL')
    if REDIS_URL:
        CACHES = {
            'default': {
                'BACKEND': 'django_redis.cache.RedisCache',
                'LOCATION': REDIS_URL,
                'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            }
        }
        SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
        SESSION_CACHE_ALIAS = 'default'
    else:
        # Redis requested but REDIS_URL missing -> fall back to database
        SESSION_ENGINE = 'django.contrib.sessions.backends.db'
else:
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_AGE = 1209600        # 2 weeks
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ---------------------------------------------------------------------------
# Security hardening (production)
# ---------------------------------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 't')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))   # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ('true', '1', 't')
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'True').lower() in ('true', '1', 't')
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    REFERRER_POLICY = 'strict-origin-when-cross-origin'

# ---------------------------------------------------------------------------
# CORS — restrict to your real origins in production
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = DEBUG              # True only in local dev
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]

# ---------------------------------------------------------------------------
# Static files (WhiteNoise) & Media (S3 / Cloudflare R2)
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'frontend']
# Compressed + hashed manifest for cache-busting in production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'   # only used for local dev

# Offload uploaded property images to object storage (Railway FS is ephemeral)
USE_S3 = os.getenv('USE_S3', 'False').lower() in ('true', '1', 't')
if USE_S3:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')  # set for Cloudflare R2
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_DEFAULT_ACL = os.getenv('AWS_DEFAULT_ACL', 'public-read')
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    # Media is served directly from the bucket/CDN URL
    if AWS_STORAGE_BUCKET_NAME and not os.getenv('MEDIA_URL'):
        if AWS_S3_ENDPOINT_URL:
            MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
        else:
            MEDIA_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com/'

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 12,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# ---------------------------------------------------------------------------
# Simple JWT
# ---------------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_LIFETIME_MINUTES', '60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_LIFETIME_DAYS', '7'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,        # revoke refresh tokens on logout
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ---------------------------------------------------------------------------
# Geocoding (Nominatim / Photon)
# ---------------------------------------------------------------------------
GEOCODING_PROVIDER = 'nominatim'
GEOCODING_NOMINATIM_URL = 'https://nominatim.openstreetmap.org/reverse'
GEOCODING_NOMINATIM_USER_AGENT = os.getenv(
    'GEOCODING_NOMINATIM_USER_AGENT', 'NyumbaHub-StudentHousing/1.0 (admin@nyumbahub.test)'
)
GEOCODING_TIMEOUT_SECONDS = int(os.getenv('GEOCODING_TIMEOUT_SECONDS', '5'))

# ---------------------------------------------------------------------------
# Safaricom Daraja M-Pesa
# ---------------------------------------------------------------------------
MPESA_CONFIG = {
    'ENVIRONMENT': os.getenv('MPESA_ENVIRONMENT', 'sandbox'),
    'CONSUMER_KEY': os.getenv('MPESA_CONSUMER_KEY', ''),
    'CONSUMER_SECRET': os.getenv('MPESA_CONSUMER_SECRET', ''),
    'SHORTCODE': os.getenv('MPESA_SHORTCODE', '174379'),
    'PASSKEY': os.getenv('MPESA_PASSKEY', ''),
    'CALLBACK_URL': os.getenv('MPESA_CALLBACK_URL', ''),
    'TIMEOUT': int(os.getenv('MPESA_TIMEOUT', '30')),
    'FALLBACK_ON_TIMEOUT': os.getenv('MPESA_FALLBACK_ON_TIMEOUT', 'True').lower() in ('true', '1', 'yes'),
    'AUTO_CONFIRM_SIMULATION': os.getenv('MPESA_AUTO_CONFIRM_SIMULATION', 'False').lower() in ('true', '1', 'yes'),
}

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------------------------------------------------------------------------
# Logging — stdout/stderr so Railway can capture and ship logs
# ---------------------------------------------------------------------------
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOG_LEVEL', 'INFO' if not DEBUG else 'DEBUG'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'payments': {
            'handlers': ['console'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'properties': {
            'handlers': ['console'],
            'level': os.getenv('LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
