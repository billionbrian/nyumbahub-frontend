# Contributor Setup Guide

This guide will help you set up the NyumbaHub backend development environment on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.12+**: Download from [python.org](https://www.python.org/downloads/)
- **Git**: Download from [git-scm.com](https://git-scm.com/downloads)
- **Virtual Environment (venv)**: Included with Python 3.3+
- **Code Editor**: VS Code, PyCharm, or your preferred IDE

## Setup Instructions

### 1. Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd nyumbahub/nyumbahub-frontend
```

### 2. Create Virtual Environment

Create a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**Note**: You should see `(venv)` in your terminal prompt indicating the virtual environment is active.

### 3. Install Dependencies

Install all required Python packages:

```bash
# Install dependencies from requirements.txt
pip install -r requirements.txt
```

This will install:
- Django 6.0.6
- Django REST Framework 3.17.1
- djangorestframework_simplejwt 5.5.1
- django-cors-headers 4.9.0
- psycopg2-binary 2.9.12
- PyJWT 2.13.0
- asgiref 3.11.1
- sqlparse 0.5.5

### 4. Database Setup

The project uses SQLite by default for development. The database file (`db.sqlite3`) is already included in the repository.

If you need to recreate the database or run migrations:

```bash
# Run migrations to create database tables
python manage.py migrate

# Create a superuser for admin access
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 5. Verify Setup

Run the development server to verify everything is working:

```bash
# Start development server
python manage.py runserver
```

You should see output like:
```
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
December 06, 2024 - 08:00:00
Django version 6.0.6, using settings 'config.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Visit `http://127.0.0.1:8000/` in your browser to see the application.

### 6. Access Admin Panel

Access the Django admin panel at `http://127.0.0.1:8000/admin/`

Use the superuser credentials you created in step 4.

## Project Structure Overview

```
nyumbahub-frontend/
├── config/                 # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # URL routing
│   └── views.py            # Frontend serving
├── accounts/               # Authentication app
│   ├── models.py           # User model
│   ├── serializers.py      # User serializers
│   ├── views.py            # Auth endpoints
│   └── urls.py             # Auth URLs
├── properties/             # Properties app
│   ├── models.py           # Property model
│   ├── serializers.py      # Property serializers
│   ├── views.py            # Property endpoints
│   └── urls.py             # Property URLs
├── frontend/               # Static frontend files
├── staticfiles/            # Collected static files
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── db.sqlite3              # SQLite database
```

## Development Workflow

### Running the Development Server

```bash
# Activate virtual environment (if not already active)
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Start server
python manage.py runserver
```

The server will run on `http://127.0.0.1:8000/`

### Creating Database Migrations

After making changes to models:

```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Using Django Shell

For interactive database operations:

```bash
# Open Django shell
python manage.py shell

# Example: Create a user
from accounts.models import User
user = User.objects.create_user(username='testuser', email='test@example.com', password='password123', role='tenant')
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test properties
```

### Collecting Static Files

```bash
# Collect static files for production
python manage.py collectstatic
```

## API Testing

### Using cURL

**Signup**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123","role":"tenant"}'
```

**Login**:
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

**Get Properties**:
```bash
curl http://127.0.0.1:8000/api/properties/
```

**Create Property** (requires JWT token):
```bash
curl -X POST http://127.0.0.1:8000/api/properties/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"title":"Test Property","description":"A nice place","location":"Nairobi","rent_amount":50000,"bedrooms":2,"bathrooms":1,"property_type":"apartment"}'
```

### Using Postman/Insomnia

1. Import the API endpoints
2. Set base URL to `http://127.0.0.1:8000`
3. For protected endpoints, add JWT token to Authorization header:
   - Header name: `Authorization`
   - Header value: `Bearer <your-jwt-token>`

## Common Issues and Solutions

### Issue: ModuleNotFoundError

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Database locked

**Solution**: Stop the development server and delete `db.sqlite3`, then run migrations again:
```bash
rm db.sqlite3
python manage.py migrate
```

### Issue: Port already in use

**Solution**: Use a different port:
```bash
python manage.py runserver 8001
```

### Issue: CORS errors

**Solution**: Ensure your frontend URL is in `CORS_ALLOWED_ORIGINS` in `config/settings.py`

## Environment Variables (Optional)

For production deployment, create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

Update `config/settings.py` to load these variables using `python-dotenv`.

## Code Style Guidelines

- Follow PEP 8 Python style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use Django's built-in features when possible

## Git Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit:
```bash
git add .
git commit -m "Description of your changes"
```

3. Push to remote:
```bash
git push origin feature/your-feature-name
```

4. Create a pull request for review

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/en/6.0/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Python Documentation](https://docs.python.org/3/)

## Getting Help

If you encounter issues:
1. Check the error messages in the terminal
2. Review the Django debug page (if DEBUG=True)
3. Check the logs in the console
4. Refer to the documentation in the `docs/` folder
5. Contact the project maintainers

## Next Steps

After setup:
1. Review the [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) for system overview
2. Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API endpoints
3. Review [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) for data models
4. Start contributing to the project!

Happy coding chief!
