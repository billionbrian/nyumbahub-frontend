# NyumbaHub Backend Documentation

Welcome to the NyumbaHub backend documentation. This folder contains comprehensive documentation for the Django-based backend system.

## Documentation Files

### 📋 [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md)
Complete overview of the backend architecture, including:
- Technology stack and framework details
- Project structure and organization
- Application architecture breakdown
- API design principles
- Security features
- Deployment considerations

**Read this first** to understand the overall system design.

### 🚀 [CONTRIBUTOR_SETUP.md](CONTRIBUTOR_SETUP.md)
Step-by-step guide for setting up the development environment:
- Prerequisites and system requirements
- Installation instructions
- Development workflow
- Common issues and solutions
- Git workflow guidelines

**Start here** if you're a new contributor setting up your local environment.

### 📦 [REQUIREMENTS.md](REQUIREMENTS.md)
Detailed requirements and dependencies documentation:
- System requirements (development and production)
- Python dependencies with descriptions
- Database requirements (SQLite and PostgreSQL)
- Web server requirements
- Security requirements
- Performance considerations

**Reference this** for understanding project dependencies and requirements.

### 🔌 [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
Complete API reference documentation:
- Authentication endpoints (signup, login, current user)
- Property endpoints (CRUD operations)
- Request/response formats
- Authentication and authorization rules
- HTTP status codes
- Error handling
- API testing examples

**Use this** when working with API endpoints or integrating the frontend.

### 🗄️ [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
Database schema and ORM documentation:
- Database tables and field definitions
- Relationships between models
- Entity relationship diagrams
- Common ORM queries
- Database constraints and validation
- Performance optimization
- Migration management

**Reference this** for understanding the data model and database operations.

## Quick Start

1. **New Contributor?** Start with [CONTRIBUTOR_SETUP.md](CONTRIBUTOR_SETUP.md)
2. **Understanding the System?** Read [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md)
3. **Building the Frontend?** Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
4. **Working with Data?** Review [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
5. **Deploying?** See [REQUIREMENTS.md](REQUIREMENTS.md) for production requirements

## Technology Stack

- **Framework**: Django 6.0.6
- **API**: Django REST Framework 3.17.1
- **Authentication**: JWT (SimpleJWT)
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Python**: 3.12+

## Key Features

- User authentication with JWT tokens
- Role-based access control (tenant/landlord)
- Property listing CRUD operations
- RESTful API design
- CORS support for frontend integration
- Comprehensive validation and error handling

## Getting Help

If you need assistance:
1. Check the relevant documentation file above
2. Review the error messages in the terminal
3. Check the Django debug page (if DEBUG=True)
4. Contact the project maintainers

## Contributing

When contributing to the backend:
1. Follow the setup guide in [CONTRIBUTOR_SETUP.md](CONTRIBUTOR_SETUP.md)
2. Understand the architecture from [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md)
3. Follow the API specifications in [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
4. Respect the database schema in [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)
5. Write tests for new features
6. Update documentation as needed

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/en/6.0/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- Project README: `../README.md`

---

**Last Updated**: 6th June 2026
