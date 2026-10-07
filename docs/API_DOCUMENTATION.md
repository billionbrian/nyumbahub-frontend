# API Documentation

## Overview

TapIn provides a RESTful API for user authentication and property management. All API endpoints follow REST conventions and return JSON responses.

**Base URL**: `http://127.0.0.1:8000/api/`

**Authentication**: JWT Bearer Token (required for protected endpoints)

**Content-Type**: `application/json`

---

## Authentication Endpoints

### 1. User Signup

Register a new user account.

**Endpoint**: `POST /api/auth/signup/`

**Authentication**: Not required

**Request Body**:

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securePassword123",
  "role": "tenant",
  "phone": "+254712345678"
}
```

**Fields**:
- `username` (string, required): Unique username
- `email` (string, required): Valid email address
- `password` (string, required): User password (will be hashed)
- `role` (string, required): User role - either "tenant" or "landlord"
- `phone` (string, optional): Phone number
- `name` (string, optional): Alternative to username (will be converted to username)

**Success Response** (201 Created):

```json
{
  "message": "Account created successfully"
}
```

**Error Response** (400 Bad Request):

```json
{
  "username": ["This field is required."],
  "email": ["This field is required."],
  "role": ["Role must be either 'tenant' or 'landlord'."]
}
```

**Error Response** (500 Internal Server Error):

```json
{
  "error": "Error message",
  "detail": "Internal server error occurred"
}
```

---

### 2. User Login

Authenticate a user and receive JWT tokens.

**Endpoint**: `POST /api/auth/login/`

**Authentication**: Not required

**Request Body**:

```json
{
  "username": "johndoe",
  "password": "securePassword123"
}
```

**Fields**:
- `username` (string, required): Username or email
- `password` (string, required): User password

**Success Response** (200 OK):

```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "tenant",
    "phone": "+254712345678",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Fields**:
- `token` (string): JWT access token (valid for 60 minutes)
- `refresh` (string): JWT refresh token (valid for 7 days)
- `user` (object): User information

**Error Response** (401 Unauthorized):

```json
{
  "detail": "No active account found with the given credentials"
}
```

---

### 3. Get Current User

Retrieve information about the currently authenticated user.

**Endpoint**: `GET /api/auth/me/`

**Authentication**: Required (JWT Bearer Token)

**Headers**:
```
Authorization: Bearer <your-jwt-token>
```

**Success Response** (200 OK):

```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "tenant",
  "phone": "+254712345678",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Error Response** (401 Unauthorized):

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Error Response** (403 Forbidden):

```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Property Endpoints

### 4. List All Properties

Retrieve a list of all available properties.

**Endpoint**: `GET /api/properties/`

**Authentication**: Not required (public endpoint)

**Query Parameters**:
- None currently supported (future: filtering, pagination)

**Success Response** (200 OK):

```json
[
  {
    "id": 1,
    "landlord": {
      "id": 2,
      "username": "landlord1",
      "email": "landlord@example.com",
      "role": "landlord",
      "phone": "+254723456789",
      "created_at": "2024-01-10T08:00:00Z"
    },
    "title": "Modern Apartment in Westlands",
    "description": "Spacious 2-bedroom apartment with modern amenities.",
    "location": "Westlands, Nairobi",
    "rent_amount": "45000.00",
    "bedrooms": 2,
    "bathrooms": 1,
    "property_type": "apartment",
    "available": true,
    "created_at": "2024-01-15T12:00:00Z"
  },
  {
    "id": 2,
    "landlord": {
      "id": 2,
      "username": "landlord1",
      "email": "landlord@example.com",
      "role": "landlord",
      "phone": "+254723456789",
      "created_at": "2024-01-10T08:00:00Z"
    },
    "title": "Cozy Studio in Kilimani",
    "description": "Perfect for singles, fully furnished studio apartment.",
    "location": "Kilimani, Nairobi",
    "rent_amount": "25000.00",
    "bedrooms": 1,
    "bathrooms": 1,
    "property_type": "studio",
    "available": true,
    "created_at": "2024-01-16T09:30:00Z"
  }
]
```

---

### 5. Get Single Property

Retrieve details of a specific property.

**Endpoint**: `GET /api/properties/{id}/`

**Authentication**: Not required (public endpoint)

**URL Parameters**:
- `id` (integer): Property ID

**Success Response** (200 OK):

```json
{
  "id": 1,
  "landlord": {
    "id": 2,
    "username": "landlord1",
    "email": "landlord@example.com",
    "role": "landlord",
    "phone": "+254723456789",
    "created_at": "2024-01-10T08:00:00Z"
  },
  "title": "Modern Apartment in Westlands",
  "description": "Spacious 2-bedroom apartment with modern amenities.",
  "location": "Westlands, Nairobi",
  "rent_amount": "45000.00",
  "bedrooms": 2,
  "bathrooms": 1,
  "property_type": "apartment",
  "available": true,
  "created_at": "2024-01-15T12:00:00Z"
}
```

**Error Response** (404 Not Found):

```json
{
  "detail": "Not found."
}
```

---

### 6. Create Property

Create a new property listing.

**Endpoint**: `POST /api/properties/`

**Authentication**: Required (JWT Bearer Token, Landlord only)

**Headers**:
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

**Request Body**:

```json
{
  "title": "Modern Apartment in Westlands",
  "description": "Spacious 2-bedroom apartment with modern amenities.",
  "location": "Westlands, Nairobi",
  "rent_amount": 45000,
  "bedrooms": 2,
  "bathrooms": 1,
  "property_type": "apartment",
  "available": true
}
```

**Fields**:
- `title` (string, required): Property title
- `description` (string, required): Detailed description
- `location` (string, required): Property location
- `rent_amount` (decimal, required): Monthly rent in KES (must be > 0)
- `bedrooms` (integer, required): Number of bedrooms (must be > 0)
- `bathrooms` (integer, required): Number of bathrooms (must be > 0)
- `property_type` (string, required): Type of property - "apartment", "house", "studio", "townhouse", or "villa"
- `available` (boolean, optional): Availability status (default: true)

**Success Response** (201 Created):

```json
{
  "id": 1,
  "landlord": {
    "id": 1,
    "username": "landlord1",
    "email": "landlord@example.com",
    "role": "landlord",
    "phone": "+254723456789",
    "created_at": "2024-01-10T08:00:00Z"
  },
  "title": "Modern Apartment in Westlands",
  "description": "Spacious 2-bedroom apartment with modern amenities.",
  "location": "Westlands, Nairobi",
  "rent_amount": "45000.00",
  "bedrooms": 2,
  "bathrooms": 1,
  "property_type": "apartment",
  "available": true,
  "created_at": "2024-01-15T12:00:00Z"
}
```

**Error Response** (400 Bad Request):

```json
{
  "rent_amount": ["Rent amount must be greater than zero."],
  "bedrooms": ["Number of bedrooms must be greater than zero."]
}
```

**Error Response** (401 Unauthorized):

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Error Response** (403 Forbidden):

```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 7. Update Property

Update an existing property listing.

**Endpoint**: `PUT /api/properties/{id}/` or `PATCH /api/properties/{id}/`

**Authentication**: Required (JWT Bearer Token, Property Owner only)

**Headers**:
```
Authorization: Bearer <your-jwt-token>
Content-Type: application/json
```

**URL Parameters**:
- `id` (integer): Property ID

**Request Body** (PUT - all fields required):

```json
{
  "title": "Updated Apartment Title",
  "description": "Updated description",
  "location": "Westlands, Nairobi",
  "rent_amount": 50000,
  "bedrooms": 2,
  "bathrooms": 2,
  "property_type": "apartment",
  "available": false
}
```

**Request Body** (PATCH - only fields to update):

```json
{
  "rent_amount": 50000,
  "available": false
}
```

**Success Response** (200 OK):

```json
{
  "id": 1,
  "landlord": {
    "id": 1,
    "username": "landlord1",
    "email": "landlord@example.com",
    "role": "landlord",
    "phone": "+254723456789",
    "created_at": "2024-01-10T08:00:00Z"
  },
  "title": "Updated Apartment Title",
  "description": "Updated description",
  "location": "Westlands, Nairobi",
  "rent_amount": "50000.00",
  "bedrooms": 2,
  "bathrooms": 2,
  "property_type": "apartment",
  "available": false,
  "created_at": "2024-01-15T12:00:00Z"
}
```

**Error Response** (404 Not Found):

```json
{
  "detail": "Not found."
}
```

**Error Response** (403 Forbidden):

```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 8. Delete Property

Delete a property listing.

**Endpoint**: `DELETE /api/properties/{id}/`

**Authentication**: Required (JWT Bearer Token, Property Owner only)

**Headers**:
```
Authorization: Bearer <your-jwt-token>
```

**URL Parameters**:
- `id` (integer): Property ID

**Success Response** (204 No Content):

No response body

**Error Response** (404 Not Found):

```json
{
  "detail": "Not found."
}
```

**Error Response** (403 Forbidden):

```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Authentication & Authorization

### JWT Token Usage

1. **Obtain Token**: Login via `/api/auth/login/` to get access and refresh tokens
2. **Use Token**: Include access token in Authorization header for protected endpoints
3. **Refresh Token**: Use refresh token to get new access token (endpoint not yet implemented)
4. **Token Expiration**: Access tokens expire after 60 minutes

### Authorization Rules

#### Public Endpoints (No Authentication Required)
- `GET /api/properties/` - List all properties
- `GET /api/properties/{id}/` - Get single property
- `POST /api/auth/signup/` - User signup
- `POST /api/auth/login/` - User login

#### Protected Endpoints (Authentication Required)
- `GET /api/auth/me/` - Get current user (any authenticated user)

#### Landlord-Only Endpoints
- `POST /api/properties/` - Create property (landlord only)

#### Owner-Only Endpoints
- `PUT /api/properties/{id}/` - Update property (property owner only)
- `PATCH /api/properties/{id}/` - Partially update property (property owner only)
- `DELETE /api/properties/{id}/` - Delete property (property owner only)

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | OK - Request successful |
| 201  | Created - Resource created successfully |
| 204  | No Content - Resource deleted successfully |
| 400  | Bad Request - Invalid request data |
| 401  | Unauthorized - Authentication required or failed |
| 403  | Forbidden - Insufficient permissions |
| 404  | Not Found - Resource not found |
| 500  | Internal Server Error - Server error |

---

## Error Response Format

All error responses follow this format:

```json
{
  "detail": "Error message"
}
```

Or for validation errors:

```json
{
  "field_name": ["Error message 1", "Error message 2"]
}
```

---

## Rate Limiting

Currently not implemented. Planned for future releases.

---

## Pagination

Currently not implemented. All results are returned in a single response. Planned for future releases.

---

## Filtering and Sorting

Currently not implemented. Planned for future releases with features like:
- Filter by property type
- Filter by location
- Filter by rent range
- Filter by availability
- Sort by rent (low to high, high to low)
- Sort by date (newest, oldest)

---

## Testing the API

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

**Create Property** (with token):
```bash
curl -X POST http://127.0.0.1:8000/api/properties/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{"title":"Test Property","description":"A nice place","location":"Nairobi","rent_amount":50000,"bedrooms":2,"bathrooms":1,"property_type":"apartment"}'
```

### Using Postman

1. Set base URL to `http://127.0.0.1:8000`
2. For protected endpoints, add JWT token to Authorization header:
   - Header name: `Authorization`
   - Header value: `Bearer <your-jwt-token>`
3. Set Content-Type to `application/json`
4. Send requests and view responses

### Using JavaScript/Fetch

```javascript
// Login
fetch('http://127.0.0.1:8000/api/auth/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'testuser',
    password: 'password123'
  })
})
.then(response => response.json())
.then(data => {
  const token = data.token;
  localStorage.setItem('token', token);
});

// Get Properties (protected)
fetch('http://127.0.0.1:8000/api/properties/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

---

## CORS Configuration

The API allows requests from the following origins:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:8000`
- `http://127.0.0.1:8000`

Credentials are enabled for cookie-based authentication if needed.

---

## Future API Enhancements

Planned features for future releases:

### Authentication
- Password reset endpoint
- Email verification
- Refresh token endpoint
- Logout endpoint
- Social authentication (Google, Facebook)

### Properties
- Image upload for properties
- Advanced filtering and search
- Pagination
- Sorting options
- Saved properties for tenants
- Property reviews and ratings
- Property inquiries/messages

### Users
- User profile management
- Update user information
- Change password
- Delete account

### Admin
- Admin dashboard endpoints
- User management
- Property moderation
- Analytics and reporting

---

## Support

For API-related issues or questions:
1. Check the error messages in the response
2. Review this documentation
3. Check the [BACKEND_ARCHITECTURE.md](BACKEND_ARCHITECTURE.md) for system details
4. Contact the development team
