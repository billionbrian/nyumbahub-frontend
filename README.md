# 🏠 TapIn

<div align="center">

### Find a Home Faster. Connect Landlords and Tenants Seamlessly.

TapIn is a modern property listing platform designed to help tenants find houses quickly while enabling landlords and property managers to advertise vacant properties efficiently.

</div>

---

## 📖 Project Description

TapIn is a web-based housing marketplace focused on simplifying the rental process.

The platform allows:

- Landlords to post available houses.
- Tenants to search and browse available properties.
- Users to communicate regarding vacancies.
- Property information to be managed digitally.

The long-term goal is to build a trusted housing ecosystem for Kenya and beyond.

---

# 🎯 Current Development Goal

The frontend structure is already being developed.

The current collaboration is focused on building the backend foundation required to support:

### Priority Tasks

#### 1. User Authentication System

Implement:

- User Registration (Signup)
- User Login
- JWT Authentication
- Password Hashing (bcrypt)
- Protected Routes

Users should be able to register as:

- Tenant
- Landlord

---

#### 2. House Listing Database

Create the database structure and API endpoints necessary for:

- Creating property listings
- Retrieving all listings
- Retrieving a single listing
- Updating listings
- Deleting listings

A landlord should only manage their own properties.

---

# 🛠 Recommended Tech Stack

### Backend

- Node.js
- Express.js

### Database

- MongoDB Atlas
- Mongoose ODM

### Authentication

- JWT (JSON Web Tokens)
- bcryptjs

### Environment Variables

- dotenv

---

# 📂 Proposed Project Structure

```bash
backend/
│
├── config/
│   └── db.js
│
├── controllers/
│   ├── authController.js
│   └── propertyController.js
│
├── middleware/
│   ├── authMiddleware.js
│   └── errorMiddleware.js
│
├── models/
│   ├── User.js
│   └── Property.js
│
├── routes/
│   ├── authRoutes.js
│   └── propertyRoutes.js
│
├── utils/
│
├── .env
├── server.js
└── package.json
```

---

# 👤 User Model

```javascript
{
  name: String,
  email: String,
  phone: String,
  password: String,
  role: String, // tenant | landlord
  createdAt: Date
}
```

---

# 🏠 Property Model

```javascript
{
  title: String,
  description: String,
  location: String,
  rentAmount: Number,
  bedrooms: Number,
  bathrooms: Number,
  propertyType: String,
  images: [String],
  available: Boolean,
  landlord: ObjectId,
  createdAt: Date
}
```

---

# 🔐 Authentication Requirements

## Signup

Endpoint:

```http
POST /api/auth/register
```

Example Request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "0712345678",
  "password": "password123",
  "role": "tenant"
}
```

---

## Login

Endpoint:

```http
POST /api/auth/login
```

Example Request:

```json
{
  "email": "john@example.com",
  "password": "password123"
}
```

Expected Response:

```json
{
  "token": "jwt_token_here",
  "user": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "tenant"
  }
}
```

---

# 🏠 Property API Requirements

## Create Property

```http
POST /api/properties
```

Authentication Required.

---

## Get All Properties

```http
GET /api/properties
```

Public Route.

---

## Get Single Property

```http
GET /api/properties/:id
```

Public Route.

---

## Update Property

```http
PUT /api/properties/:id
```

Only property owner can update.

---

## Delete Property

```http
DELETE /api/properties/:id
```

Only property owner can delete.

---

# 🔒 Authorization Rules

### Tenant

Can:

- Register
- Login
- Browse listings
- View property details

Cannot:

- Create property listings

---

### Landlord

Can:

- Register
- Login
- Create listings
- Edit listings
- Delete listings

---

# 🌍 Environment Variables

Create a `.env` file:

```env
PORT=5000

MONGO_URI=your_mongodb_connection_string

JWT_SECRET=your_jwt_secret
```

---

# 🚀 Expected Deliverables

The collaborator is expected to complete:

## Authentication Module

- [ ] User Signup
- [ ] User Login
- [ ] Password Hashing
- [ ] JWT Authentication
- [ ] Protected Routes

## Database Integration

- [ ] MongoDB Connection
- [ ] User Model
- [ ] Property Model

## Property Listing System

- [ ] Create Property
- [ ] Fetch Properties
- [ ] Update Property
- [ ] Delete Property

## Documentation

- [ ] API Documentation
- [ ] Environment Setup Guide

--

# 📌 Future Features 

These features are planned but should not be implemented now:

 Image Uploads (Cloudinary)
 House Search Filters
 Saved Properties
 Tenant-Landlord Messaging
 Notifications
 Digital Rental Agreements
 Mobile Application
 Payment Integration



# 🤝 Collaboration Notes

This repository is currently focused on building the backend foundation.

Please prioritize:

1. Authentication (Signup/Login)
2. MongoDB Database Setup
3. House Listing CRUD Operations

Keep the code modular, scalable, and production-ready.

---

# 👨‍💻 Project Owner

Brian Billion

TapIn Project
