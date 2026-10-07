# Backend Requirements and Dependencies

## System Requirements

### Development Environment
- **Python**: 3.12 or higher
- **Operating System**: Linux, macOS, or Windows
- **RAM**: Minimum 4GB (8GB recommended)
- **Disk Space**: Minimum 2GB free space
- **Git**: For version control

### Production Environment
- **Python**: 3.12 or higher
- **Database**: PostgreSQL 12+ (recommended) or SQLite 3
- **Web Server**: Gunicorn or uWSGI
- **Reverse Proxy**: Nginx or Apache
- **SSL Certificate**: For HTTPS
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk Space**: Minimum 5GB free space

## Python Dependencies

All Python dependencies are listed in `requirements.txt`:

```
asgiref==3.11.1
Django==6.0.6
django-cors-headers==4.9.0
djangorestframework==3.17.1
djangorestframework_simplejwt==5.5.1
psycopg2-binary==2.9.12
PyJWT==2.13.0
sqlparse==0.5.5
```

### Dependency Details

#### Core Framework
- **Django 6.0.6**
  - Purpose: Web framework
  - Description: Provides ORM, authentication, admin panel, templating, and core web functionality
  - Documentation: https://docs.djangoproject.com/en/6.0/

- **asgiref 3.11.1**
  - Purpose: ASGI reference implementation
  - Description: Provides ASGI (Asynchronous Server Gateway Interface) utilities for async support
  - Documentation: https://docs.djangoproject.com/en/stable/topics/async/

#### API Framework
- **djangorestframework 3.17.1**
  - Purpose: REST API toolkit
  - Description: Provides powerful tools for building Web APIs including serializers, viewsets, and authentication
  - Documentation: https://www.django-rest-framework.org/

#### Authentication
- **djangorestframework_simplejwt 5.5.1**
  - Purpose: JWT authentication
  - Description: JSON Web Token authentication implementation for Django REST Framework
  - Documentation: https://django-rest-framework-simplejwt.readthedocs.io/

- **PyJWT 2.13.0**
  - Purpose: JWT encoding/decoding
  - Description: Library for encoding and decoding JSON Web Tokens
  - Documentation: https://pyjwt.readthedocs.io/

#### CORS Support
- **django-cors-headers 4.9.0**
  - Purpose: CORS middleware
  - Description: Handles Cross-Origin Resource Sharing for frontend-backend communication
  - Documentation: https://pypi.org/project/django-cors-headers/

#### Database
- **psycopg2-binary 2.9.12**
  - Purpose: PostgreSQL adapter
  - Description: PostgreSQL database adapter for Python (binary distribution for easier installation)
  - Documentation: https://www.psycopg.org/docs/
  - Note: Required for production PostgreSQL deployment. Not used in development with SQLite.

- **sqlparse 0.5.5**
  - Purpose: SQL parser
  - Description: Non-validating SQL parser for Django's database operations
  - Documentation: https://sqlparse.readthedocs.io/

## Optional Dependencies

### Development Tools (Not in requirements.txt but recommended)
- **pytest-django**: For testing
- **pytest-cov**: For code coverage
- **black**: For code formatting
- **flake8**: For linting
- **django-debug-toolbar**: For debugging
- **python-dotenv**: For environment variable management

### Production Tools
- **gunicorn**: WSGI HTTP Server
- **whitenoise**: Static file serving
- **sentry-sdk**: Error tracking
- **django-storages**: Cloud storage integration
- **boto3**: AWS S3 integration

## Database Requirements

### SQLite (Development)
- **Version**: 3.x
- **Configuration**: Built-in with Python
- **File**: `db.sqlite3`
- **Pros**: Simple setup, no additional installation
- **Cons**: Not suitable for production, limited concurrency

### PostgreSQL (Production - Recommended)
- **Version**: 12 or higher
- **Configuration**: Requires psycopg2-binary
- **Connection**: Configure in `config/settings.py`
- **Pros**: Production-ready, better concurrency, advanced features
- **Cons**: Requires separate installation and configuration

#### PostgreSQL Configuration Example

In `config/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nyumbahub_db',
        'USER': 'nyumbahub_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Web Server Requirements

### Development
- **Django Development Server**: Built-in with `python manage.py runserver`
- **Port**: Default 8000 (configurable)
- **Purpose**: Development and testing only

### Production
- **Gunicorn**: Recommended WSGI server
  - Install: `pip install gunicorn`
  - Run: `gunicorn config.wsgi:application`
  - Workers: 2-4 per CPU core
  - Documentation: https://docs.gunicorn.org/

- **uWSGI**: Alternative WSGI server
  - Install: `pip install uwsgi`
  - Documentation: https://uwsgi-docs.readthedocs.io/

### Reverse Proxy
- **Nginx**: Recommended reverse proxy
  - Serves static files
  - Handles SSL termination
  - Load balancing
  - Documentation: https://nginx.org/en/docs/

- **Apache**: Alternative reverse proxy
  - Documentation: https://httpd.apache.org/docs/

## Security Requirements

### SSL/TLS
- **Certificate**: Required for production
- **Providers**: Let's Encrypt (free), commercial providers
- **Configuration**: Configure in Nginx/Apache

### Environment Variables
- **SECRET_KEY**: Django secret key (required)
- **DEBUG**: Set to False in production
- **ALLOWED_HOSTS**: Configure with actual domain
- **DATABASE_URL**: Database connection string
- **JWT_SECRET**: JWT signing key (can use SECRET_KEY)

### Security Headers
- **CORS**: Configure allowed origins
- **CSRF**: Django CSRF protection enabled
- **XSS**: Django XSS protection enabled
- **Clickjacking**: Django XFrameOptionsMiddleware enabled

## Performance Requirements

### Caching (Optional but Recommended)
- **Redis**: For session storage and caching
- **Memcached**: Alternative caching solution
- **Django Cache Framework**: Built-in caching support

### Static Files
- **Storage**: Local filesystem or cloud storage (AWS S3, CloudFront)
- **CDN**: Content Delivery Network for global distribution
- **Compression**: Enable gzip compression

## Monitoring and Logging

### Logging
- **Django Logging**: Built-in logging framework
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Files**: Configure in settings.py

### Error Tracking (Optional)
- **Sentry**: Error tracking and monitoring
- **Rollbar**: Alternative error tracking
- **Documentation**: https://docs.sentry.io/

## API Requirements

### REST API
- **Format**: JSON
- **Authentication**: JWT Bearer token
- **Content-Type**: application/json
- **Base URL**: `/api/`

### Rate Limiting (Future)
- **django-ratelimit**: For API rate limiting
- **Configuration**: Per endpoint limits

## Browser Requirements (Frontend)

### Supported Browsers
- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions
- **Mobile**: iOS Safari, Chrome Mobile

### JavaScript
- **ES6+**: Modern JavaScript features
- **Fetch API**: For HTTP requests
- **Local Storage**: For token storage

## Testing Requirements

### Unit Testing
- **pytest**: Testing framework (optional)
- **django.test.TestCase**: Built-in Django testing
- **Coverage**: pytest-cov (optional)

### API Testing
- **Postman**: API testing tool
- **Insomnia**: Alternative API testing tool
- **cURL**: Command-line API testing

## Deployment Requirements

### Hosting Options
- **VPS**: DigitalOcean, Linode, AWS EC2
- **PaaS**: Heroku, PythonAnywhere, Render
- **Container**: Docker, Kubernetes

### CI/CD (Optional)
- **GitHub Actions**: Continuous integration
- **GitLab CI**: Alternative CI/CD
- **Jenkins**: Enterprise CI/CD

## Version Control

### Git
- **Version**: 2.x
- **Branching**: Git flow or feature branch workflow
- **Hosting**: GitHub, GitLab, Bitbucket

## Installation Summary

### Quick Install
```bash
# Clone repository
git clone <repository-url>
cd nyumbahub/nyumbahub-frontend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

### Production Install
```bash
# Install additional production dependencies
pip install gunicorn psycopg2-binary

# Set environment variables
export DEBUG=False
export SECRET_KEY='your-secret-key'
export ALLOWED_HOSTS='yourdomain.com'

# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Dependency Conflicts
If you encounter dependency conflicts:
```bash
# Upgrade pip
pip install --upgrade pip

# Install with specific versions
pip install -r requirements.txt --upgrade

# Use virtual environment to isolate dependencies
```

### PostgreSQL Issues
If PostgreSQL connection fails:
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check connection
psql -U postgres -d nyumbahub_db

# Verify credentials in settings.py
```

### Port Already in Use
If port 8000 is in use:
```bash
# Use different port
python manage.py runserver 8001

# Or kill process using port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/en/6.0/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Python Packaging Guide](https://packaging.python.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
