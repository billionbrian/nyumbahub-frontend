# Database Schema Documentation

## Overview

NyumbaHub uses Django ORM (Object-Relational Mapping) for database operations. The database schema is defined through Django models in the `accounts` and `properties` applications.

**Database Engine**: SQLite3 (development), PostgreSQL (production)

**ORM**: Django ORM

**Migration System**: Django Migrations

---

## Database Tables

### 1. Users Table (auth_user)

**Table Name**: `auth_user`

**Description**: Custom user model extending Django's AbstractUser with additional fields for role-based access control.

**Model File**: `accounts/models.py`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | IntegerField | Primary Key, Auto Increment | Unique user identifier |
| username | CharField | Max Length: 150, Unique | User's username |
| first_name | CharField | Max Length: 150, Optional | User's first name |
| last_name | CharField | Max Length: 150, Optional | User's last name |
| email | CharField | Max Length: 254, Unique | User's email address |
| password | CharField | Max Length: 128 | Hashed password (PBKDF2) |
| is_staff | BooleanField | Default: False | Admin access flag |
| is_active | BooleanField | Default: True | Account active flag |
| is_superuser | BooleanField | Default: False | Superuser flag |
| last_login | DateTimeField | Optional | Last login timestamp |
| date_joined | DateTimeField | Auto Now Add | Account creation timestamp |
| role | CharField | Max Length: 20, Choices: tenant/landlord, Default: tenant | User role in the system |
| phone | CharField | Max Length: 20, Optional | User's phone number |
| created_at | DateTimeField | Auto Now Add | Custom creation timestamp |

#### Relationships

- **One-to-Many**: User has many Properties (as landlord)
  - Related name: `properties`
  - Foreign key in Property model

#### Indexes

- `username` (unique index)
- `email` (unique index)

#### Constraints

- `username` must be unique
- `email` must be unique
- `role` must be either 'tenant' or 'landlord'

#### Model Definition

```python
class User(AbstractUser):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.role})"
```

---

### 2. Properties Table (properties_property)

**Table Name**: `properties_property`

**Description**: Stores property listings created by landlords.

**Model File**: `properties/models.py`

#### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | IntegerField | Primary Key, Auto Increment | Unique property identifier |
| landlord | ForeignKey | References: auth_user (id), On Delete: CASCADE | Property owner (user) |
| title | CharField | Max Length: 200, Required | Property title |
| description | TextField | Required | Detailed property description |
| location | CharField | Max Length: 200, Required | Property location |
| rent_amount | DecimalField | Max Digits: 10, Decimal Places: 2, Required | Monthly rent in KES |
| bedrooms | IntegerField | Default: 1, Required | Number of bedrooms |
| bathrooms | IntegerField | Default: 1, Required | Number of bathrooms |
| property_type | CharField | Max Length: 20, Choices, Default: apartment | Type of property |
| available | BooleanField | Default: True | Availability status |
| created_at | DateTimeField | Auto Now Add | Listing creation timestamp |

#### Property Type Choices

| Value | Label |
|-------|-------|
| apartment | Apartment |
| house | House |
| studio | Studio |
| townhouse | Townhouse |
| villa | Villa |

#### Relationships

- **Many-to-One**: Property belongs to one User (landlord)
  - Foreign key: `landlord`
  - Related name in User model: `properties`
  - On delete: CASCADE (property deleted if landlord deleted)

#### Indexes

- `landlord_id` (foreign key index)
- `created_at` (for ordering)

#### Constraints

- `rent_amount` must be greater than 0 (validated at serializer level)
- `bedrooms` must be greater than 0 (validated at serializer level)
- `bathrooms` must be greater than 0 (validated at serializer level)
- `property_type` must be one of the defined choices

#### Ordering

- Default ordering: `-created_at` (newest first)

#### Model Definition

```python
class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
        ('townhouse', 'Townhouse'),
        ('villa', 'Villa'),
    ]
    
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=200)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField(default=1)
    bathrooms = models.IntegerField(default=1)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='apartment')
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
    
    def __str__(self):
        return f"{self.title} - {self.location} (KES {self.rent_amount})"
```

---

## Database Relationships

### Entity Relationship Diagram

```
┌─────────────────┐
│     User        │
│  (auth_user)    │
├─────────────────┤
│ id (PK)         │
│ username        │
│ email           │
│ password        │
│ role            │
│ phone           │
│ created_at      │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────┐
│   Property      │
│(properties_     │
│    property)    │
├─────────────────┤
│ id (PK)         │
│ landlord (FK)   │
│ title           │
│ description     │
│ location        │
│ rent_amount     │
│ bedrooms        │
│ bathrooms       │
│ property_type   │
│ available       │
│ created_at      │
└─────────────────┘
```

### Relationship Types

1. **User to Property**: One-to-Many
   - One landlord can have multiple properties
   - Each property belongs to exactly one landlord
   - Implemented via ForeignKey in Property model

---

## Database Migrations

### Migration Files

**Accounts App Migrations**:
- `accounts/migrations/0001_initial.py` - Initial User model creation

**Properties App Migrations**:
- `properties/migrations/0001_initial.py` - Initial Property model creation

### Running Migrations

```bash
# Create migration files after model changes
python manage.py makemigrations

# Apply migrations to database
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Undo last migration (development only)
python manage.py migrate accounts <previous_migration>
```

### Migration Best Practices

1. Always review generated migration files
2. Test migrations in development before production
3. Never modify migration files after they're applied
4. Use data migrations for data changes
5. Backup database before running migrations in production

---

## Database Queries

### Common ORM Queries

#### User Queries

```python
# Get all users
users = User.objects.all()

# Get user by ID
user = User.objects.get(id=1)

# Get user by username
user = User.objects.get(username='johndoe')

# Get all landlords
landlords = User.objects.filter(role='landlord')

# Get all tenants
tenants = User.objects.filter(role='tenant')

# Create new user
user = User.objects.create_user(
    username='newuser',
    email='user@example.com',
    password='password123',
    role='tenant'
)

# Update user
user = User.objects.get(id=1)
user.phone = '+254712345678'
user.save()

# Delete user
user = User.objects.get(id=1)
user.delete()
```

#### Property Queries

```python
# Get all properties
properties = Property.objects.all()

# Get property by ID
property = Property.objects.get(id=1)

# Get properties by landlord
landlord_properties = Property.objects.filter(landlord_id=1)

# Get available properties
available_properties = Property.objects.filter(available=True)

# Get properties by type
apartments = Property.objects.filter(property_type='apartment')

# Get properties by location
nairobi_properties = Property.objects.filter(location__icontains='Nairobi')

# Get properties by rent range
affordable = Property.objects.filter(rent_amount__lte=50000)

# Create new property
property = Property.objects.create(
    landlord=landlord_user,
    title='New Property',
    description='Description here',
    location='Nairobi',
    rent_amount=45000,
    bedrooms=2,
    bathrooms=1,
    property_type='apartment'
)

# Update property
property = Property.objects.get(id=1)
property.available = False
property.save()

# Delete property
property = Property.objects.get(id=1)
property.delete()
```

#### Complex Queries

```python
# Get properties with landlord info
properties = Property.objects.select_related('landlord').all()

# Get landlord properties with specific criteria
landlord_properties = Property.objects.filter(
    landlord_id=1,
    available=True,
    property_type='apartment'
).order_by('-created_at')

# Count properties per landlord
from django.db.models import Count
landlord_stats = User.objects.filter(
    role='landlord'
).annotate(
    property_count=Count('properties')
)

# Search properties by title or description
from django.db.models import Q
search_results = Property.objects.filter(
    Q(title__icontains='modern') | Q(description__icontains='modern')
)
```

---

## Database Constraints and Validation

### Model-Level Constraints

1. **User Model**:
   - `username`: Unique, max 150 characters
   - `email`: Unique, max 254 characters
   - `role`: Must be 'tenant' or 'landlord'
   - `phone`: Max 20 characters, optional

2. **Property Model**:
   - `title`: Max 200 characters, required
   - `description`: Required, no max length
   - `location`: Max 200 characters, required
   - `rent_amount`: Decimal (10, 2), required
   - `bedrooms`: Integer, default 1, required
   - `bathrooms`: Integer, default 1, required
   - `property_type`: Must be one of defined choices
   - `available`: Boolean, default True

### Serializer-Level Validation

Additional validation performed in serializers:

1. **PropertySerializer**:
   - `rent_amount`: Must be > 0
   - `bedrooms`: Must be > 0
   - `bathrooms`: Must be > 0

2. **SignupSerializer**:
   - `role`: Must be 'tenant' or 'landlord'
   - `username`: Required (or `name` can be provided as alternative)

---

## Database Performance Considerations

### Indexes

- **User table**: Indexed on `username` and `email` for fast lookups
- **Property table**: Indexed on `landlord_id` for fast landlord queries
- **Property table**: Indexed on `created_at` for ordering

### Query Optimization

1. **Use select_related** for ForeignKey relationships:
   ```python
   Property.objects.select_related('landlord').all()
   ```

2. **Use prefetch_related** for ManyToMany relationships (future):
   ```python
   Property.objects.prefetch_related('amenities').all()
   ```

3. **Use only() to fetch only needed fields**:
   ```python
   Property.objects.only('title', 'location', 'rent_amount')
   ```

4. **Use pagination** for large result sets (future implementation)

---

## Database Backup and Restore

### SQLite (Development)

```bash
# Backup
cp db.sqlite3 db.sqlite3.backup

# Restore
cp db.sqlite3.backup db.sqlite3
```

### PostgreSQL (Production)

```bash
# Backup
pg_dump -U username -d nyumbahub_db > backup.sql

# Restore
psql -U username -d nyumbahub_db < backup.sql
```

---

## Database Administration

### Django Admin Panel

Access the Django admin panel at `/admin/` to manage database records:

- **Users**: View, create, edit, delete users
- **Properties**: View, create, edit, delete properties

### Django Shell

Use Django shell for programmatic database operations:

```bash
python manage.py shell
```

### Database Inspection

```bash
# Show SQL for a query
from django.db import connection
from accounts.models import User
print(connection.queries)

# Use Django Extensions (if installed)
python manage.py shell_plus
python manage.py dbshell
```

---

## Future Database Enhancements

Planned database additions for future releases:

### New Models

1. **PropertyImage**: Store property images
2. **PropertyAmenity**: Property amenities (WiFi, parking, etc.)
3. **PropertyReview**: User reviews for properties
4. **SavedProperty**: Properties saved by tenants
5. **Message**: Messaging between tenants and landlords
6. **RentalApplication**: Rental applications from tenants
7. **RentalAgreement**: Digital rental agreements

### New Fields

1. **Property**: 
   - images (ManyToMany to PropertyImage)
   - amenities (ManyToMany to PropertyAmenity)
   - square_footage
   - furnished (Boolean)
   - pet_friendly (Boolean)
   - latitude, longitude (for maps)

2. **User**:
   - profile_image
   - bio
   - verified (Boolean)
   - rating (Decimal)

### Indexes

- Add composite indexes for common query patterns
- Add full-text search indexes for property search

---

## Data Integrity

### Cascade Deletes

- When a User is deleted, all their Properties are also deleted (CASCADE)
- This ensures no orphaned property records

### Transactions

Django uses database transactions by default for data integrity:

```python
from django.db import transaction

@transaction.atomic
def create_property_with_images(property_data, images):
    property = Property.objects.create(**property_data)
    # Create images
    for image_data in images:
        PropertyImage.objects.create(property=property, **image_data)
    # All or nothing - if image creation fails, property is rolled back
```

---

## Security Considerations

### Password Storage

- Passwords are hashed using Django's PBKDF2 algorithm
- Salt is automatically handled by Django
- Never store plain text passwords

### SQL Injection Prevention

- Django ORM automatically prevents SQL injection
- Never use raw SQL unless absolutely necessary
- If using raw SQL, use parameterized queries

### Data Access Control

- Use Django's authentication and authorization system
- Implement custom permissions for fine-grained control
- Never expose sensitive data in API responses

---

## Database Maintenance

### Regular Tasks

1. **Vacuum** (PostgreSQL): Reclaim disk space
2. **Analyze**: Update query planner statistics
3. **Reindex**: Rebuild indexes if needed
4. **Backup**: Regular automated backups
5. **Monitor**: Track database performance metrics

### Django Commands

```bash
# Check for database issues
python manage.py check

# Create database diagram (with django-extensions)
python manage.py graph_models -a -o my_project_visualized.png
```

---

## Troubleshooting

### Common Issues

1. **Migration Conflicts**:
   - Solution: Resolve conflicts manually or use `--merge`

2. **Database Locked** (SQLite):
   - Solution: Close all connections, delete lock file

3. **Foreign Key Constraint Errors**:
   - Solution: Ensure referenced records exist before creating relationships

4. **Performance Issues**:
   - Solution: Add indexes, use select_related/prefetch_related, optimize queries

---

## Additional Resources

- [Django Models Documentation](https://docs.djangoproject.com/en/6.0/topics/db/models/)
- [Django ORM Documentation](https://docs.djangoproject.com/en/6.0/topics/db/queries/)
- [Django Migrations](https://docs.djangoproject.com/en/6.0/topics/migrations/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
