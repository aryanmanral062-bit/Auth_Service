# Authentication Service

A modular authentication backend built with **Python and FastAPI**, featuring user registration, password hashing, JWT-based authentication, refresh tokens, and database-backed session management.

This project was built to develop practical backend engineering skills, including REST API development, database integration, authentication, authorization, and modular application architecture.

## Features

### User Management
- User registration with email validation.
- Password validation using Pydantic schemas.
- Secure password hashing using bcrypt through Passlib.
- Duplicate email checks.
- User status management (`is_active`).
- Superuser flag for administrative authorization.
- Response schemas to control the user data returned by the API.

### Authentication
- User login using email and password.
- JWT access token generation.
- JWT refresh token generation.
- Token expiration and token-type validation.
- Bearer token authentication through FastAPI dependencies.
- Current-user retrieval from the database.
- Active-user validation.
- Superuser authorization checks.

### Session Management
- Database-backed refresh token sessions.
- SHA-256 hashing of refresh tokens before storing them in the database.
- Session expiration tracking.
- Session activity tracking using `last_used_at`.
- Logout by revoking a specific refresh-token session.
- Logout from all devices by revoking all active sessions belonging to the current user.

### Database and Architecture
- SQLAlchemy ORM for database models and queries.
- SQLite database for local development.
- Separate modules for models, schemas, services, security, database configuration, dependencies, and API routes.
- FastAPI dependency injection for database sessions and authenticated users.
- Automatic database table creation for development.

## Tech Stack

- **Language:** Python
- **API Framework:** FastAPI
- **Data Validation:** Pydantic
- **ORM:** SQLAlchemy
- **Database:** SQLite
- **Password Hashing:** Passlib with bcrypt
- **Token Authentication:** JWT using `python-jose`
- **API Documentation:** FastAPI-generated OpenAPI documentation and Swagger UI

## Project Structure

```text
app/
├── main.py
├── db/
│   └── database.py
├── models/
│   ├── user.py
│   └── session.py
├── schemas/
│   └── user.py
├── core/
│   ├── security.py
│   └── jwt_utility.py
├── services/
│   ├── user.py
│   └── session.py
└── api/
    ├── dependencies/
    │   ├── database.py
    │   └── auth.py
    └── routes/
        └── v1/
            ├── auth.py
            └── users.py
```

### Responsibilities of Major Modules

| Module | Responsibility |
|---|---|
| `app/main.py` | Initializes FastAPI, registers routers, and exposes the health endpoint. |
| `app/db/database.py` | Configures the SQLAlchemy engine, session factory, and declarative base. |
| `app/models/user.py` | Defines the user database model. |
| `app/models/session.py` | Defines database-backed refresh-token sessions. |
| `app/schemas/user.py` | Defines request and response schemas using Pydantic. |
| `app/core/security.py` | Handles password hashing, password verification, and token hashing. |
| `app/core/jwt_utility.py` | Creates and verifies access and refresh JWTs. |
| `app/services/user.py` | Implements user retrieval, creation, and credential authentication. |
| `app/services/session.py` | Implements session creation, lookup, tracking, and revocation. |
| `app/api/dependencies/database.py` | Provides and closes a database session for each request. |
| `app/api/dependencies/auth.py` | Validates access tokens, retrieves the current user, and enforces superuser access. |
| `app/api/routes/v1/auth.py` | Exposes the registration, login, refresh, logout, and logout-all endpoints. |
| `app/api/routes/v1/users.py` | Imported by the application; its implementation is not documented here because its source code has not been reviewed. |

## API Endpoints

The authentication router is registered under `/api/v1`, and the router itself uses the `/auth` prefix.

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Checks whether the API is running. |
| `POST` | `/api/v1/auth/register` | Registers a new user. |
| `POST` | `/api/v1/auth/login` | Authenticates a user and returns access and refresh tokens. |
| `POST` | `/api/v1/auth/refresh` | Issues a new access token using a valid refresh token and active database session. |
| `POST` | `/api/v1/auth/logout` | Revokes the session associated with a refresh token. |
| `POST` | `/api/v1/auth/logout-all` | Revokes all active sessions belonging to the authenticated user. |

### 1. Health Check

**Endpoint:** `GET /health`

Returns a simple response confirming that the API is running.

### 2. User Registration

**Endpoint:** `POST /api/v1/auth/register`

Accepts an email and password, checks whether the email is already registered, hashes the password, and creates a user record.

The response uses `UserResponse`, which excludes the password and hashed password.

### 3. User Login

**Endpoint:** `POST /api/v1/auth/login`

Validates the user's credentials and account status. On successful authentication, the service generates an access token and a refresh token, then stores a hash of the refresh token in the database.

The tokens are returned to the client.

### 4. Refresh Access Token

**Endpoint:** `POST /api/v1/auth/refresh`

Validates the refresh JWT, checks for a corresponding active database session, checks the session expiration, updates the session's last-used timestamp, and returns a new access token.

The current implementation reuses the same refresh token instead of rotating it.

### 5. Logout

**Endpoint:** `POST /api/v1/auth/logout`

Accepts a refresh token and revokes its active database session.

The access token is not immediately invalidated by this operation and can remain usable until its expiration.

### 6. Logout from All Devices

**Endpoint:** `POST /api/v1/auth/logout-all`

Requires an authenticated user. Revokes all active refresh-token sessions belonging to that user.

Previously issued access tokens are not immediately invalidated by this operation.

## Authentication Flow

### Registration

```text
Client
  ↓
POST /auth/register
  ↓
Validate request with Pydantic
  ↓
Check whether email already exists
  ↓
Hash password
  ↓
Save user in database
  ↓
Return user response
```

### Login

```text
Client
  ↓
POST /auth/login
  ↓
Find user by email
  ↓
Verify password hash
  ↓
Check account status
  ↓
Generate access and refresh JWTs
  ↓
Hash refresh token and save session
  ↓
Return tokens
```

### Authenticated Request

```text
Client sends Bearer access token
  ↓
OAuth2PasswordBearer extracts token
  ↓
Verify JWT signature and expiration
  ↓
Validate token type and subject
  ↓
Retrieve user from database
  ↓
Check whether user is active
  ↓
Allow access to the protected endpoint
```

### Token Refresh

```text
Client submits refresh token
  ↓
Verify refresh JWT
  ↓
Find matching active database session
  ↓
Check session expiration
  ↓
Issue new access token
  ↓
Update last-used timestamp
  ↓
Return tokens
```

## Token Configuration

The current configuration in `app/core/jwt_utility.py` uses:

| Setting | Current value |
|---|---|
| JWT algorithm | HS256 |
| Access token lifetime | 30 minutes |
| Refresh token lifetime | 7 days |
| Access token type claim | `access` |
| Refresh token type claim | `refresh` |

The JWT subject (`sub`) contains the user's ID as a string.

The application uses a development fallback for `SECRET_KEY`. A secure, externally configured secret is required before deployment.

## Database Models

### User

The `users` table stores:

- User ID
- Unique email address
- Hashed password
- Active status
- Superuser status
- Creation timestamp
- Update timestamp

### Session

The `sessions` table stores:

- Session ID
- Associated user ID
- Hashed refresh token
- Active status
- Expiration timestamp
- Optional IP address and user-agent fields
- Creation timestamp
- Last-used timestamp

A foreign key links sessions to users, with `ON DELETE CASCADE` configured for the relationship.

## Local Development

### Prerequisites

- Python installed.
- A virtual environment.
- The project's Python dependencies installed.

The code uses FastAPI, SQLAlchemy, Pydantic, Passlib, bcrypt, and `python-jose`. `email-validator` is also needed for Pydantic's `EmailStr`.

Install the dependencies using the project's dependency file if available, or install the required packages individually.

### Run the Application

From the project root, run:

```bash
uvicorn app.main:app --reload
```

The application uses a local SQLite database configured as:

```text
sqlite:///./sql_app.db
```

The database tables are created automatically during application import/startup through `Base.metadata.create_all()`.

Open the following URL after starting the server:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

## Security Considerations and Current Limitations

This project implements core authentication and session-management mechanisms, but it should not yet be considered production-ready.

Known limitations and future improvements include:

- Replace the development JWT secret fallback with secure environment-based configuration or a secrets manager.
- Introduce database migrations using Alembic instead of relying on `create_all()` for schema changes.
- Add rate limiting and protection against brute-force login attempts.
- Implement refresh-token rotation and reuse detection.
- Consider immediate access-token revocation if required by the application's security model.
- Review transaction handling and error recovery for database operations.
- Review timezone handling for database timestamps across supported database systems.
- Add automated unit and integration tests.
- Add email verification, password reset, and multi-factor authentication if required.
- Configure deployment-specific HTTPS, CORS, security headers, and secret management.
- Review authorization requirements for protected user-management endpoints.

These are future improvements, not features claimed as implemented.

## Learning Outcomes

This project provides practical experience with:

- REST API design and HTTP status codes.
- FastAPI routers and dependency injection.
- Pydantic request validation and response serialization.
- SQLAlchemy models, queries, and database sessions.
- Password hashing and credential verification.
- JWT creation, verification, expiration, and token claims.
- Bearer token authentication.
- Authentication versus authorization.
- Database-backed session tracking and revocation.
- Separation of API routes, business logic, schemas, models, and security utilities.

## Project Status

**Current status:** Core authentication and refresh-session functionality implemented; further code review, testing, security hardening, and production improvements remain.

The project is intended to evolve into a more complete authentication service as additional backend engineering concepts are learned and implemented.
