# Technical Documentation

[Home](index.md) | [User Guide](user-guide.md) | [Technical Docs](technical-docs.md) | [Development Guide](development-guide.md) | [Deployment Guide](deployment-guide.md) | [FAQ](faq.md)

This document provides technical details about the Money Tracker application's architecture, database schema, and API endpoints.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Authentication System](#authentication-system)
- [Security Framework](#security-framework)

## Architecture Overview

Money Tracker follows a Model-View-Controller (MVC) architecture:

- **Models** (`models.py`): Defines data structures and database interactions
- **Views** (`templates/`): HTML templates for rendering the UI
- **Controller** (`app.py`): Handles HTTP requests and business logic

### Technology Stack

- **Backend Framework**: Flask
- **Database**: MongoDB
- **Authentication**: Flask-Login, PyOTP (for 2FA)
- **Security**: Flask-Limiter, TOTP-based 2FA, Session Management
- **Frontend**: HTML, CSS, JavaScript
- **CSS Framework**: Bootstrap 5
- **Data Visualization**: Chart.js
- **QR Code Generation**: qrcode, Pillow

### Component Interaction

1. **Client Request Flow**:

   - User makes a request to a route
   - Flask routes the request to the appropriate function in `app.py`
   - The function processes the request, interacts with models as needed
   - The function renders a template with data
   - The rendered HTML is returned to the client

2. **Data Flow**:
   - Models interact with MongoDB to retrieve and store data
   - Controllers (route handlers) use models to get data
   - Controllers pass data to templates
   - Templates render data for the user

## Database Schema

Money Tracker uses MongoDB with the following collections:

### Users Collection

```json
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "password": String,
  "registered_on": DateTime,
  "last_login": DateTime,
  "login_attempts": Integer,
  "account_locked_until": DateTime,
  "password_reset_token": String,
  "password_reset_expires": DateTime,
  "password_changed_on": DateTime,
  "two_factor_enabled": Boolean,
  "two_factor_secret": String,
  "two_factor_backup_codes": Array,
  "active_sessions": Array,
  "security_logs": Array
}
```

- `_id`: Unique identifier for the user
- `username`: Unique username for the user
- `email`: Unique email address for the user
- `password`: Hashed password using Werkzeug's security functions
- `registered_on`: Date and time when the user registered
- `last_login`: Date and time of the last successful login
- `login_attempts`: Counter for failed login attempts
- `account_locked_until`: Timestamp until which the account is locked after multiple failed login attempts
- `password_reset_token`: Token for password reset functionality
- `password_reset_expires`: Expiration timestamp for the password reset token
- `password_changed_on`: Date and time when the password was last changed
- `two_factor_enabled`: Whether two-factor authentication is enabled
- `two_factor_secret`: Secret key for TOTP-based two-factor authentication
- `two_factor_backup_codes`: List of backup codes for 2FA recovery
- `active_sessions`: List of active user sessions with device and IP information
- `security_logs`: List of security-related events for the user account

### Expenses Collection

```json
{
  "_id": ObjectId,
  "amount": Float,
  "category_id": ObjectId,
  "description": String,
  "date": DateTime,
  "transaction_type": String,
  "user_id": String,
  "timestamp": DateTime
}
```

- `_id`: Unique identifier for the expense
- `amount`: Monetary amount of the transaction
- `category_id`: Reference to a category in the categories collection
- `description`: Text description of the transaction
- `date`: Date of the transaction
- `transaction_type`: "CR" for credit (income) or "DR" for debit (expense)
- `user_id`: Reference to the user who owns this transaction
- `timestamp`: When the record was created in the system

### Salaries Collection

```json
{
  "_id": ObjectId,
  "amount": Float,
  "date": DateTime,
  "user_id": String
}
```

- `_id`: Unique identifier for the salary entry
- `amount`: Salary amount
- `date`: Date when the salary was received
- `user_id`: Reference to the user who owns this salary entry

### Categories Collection

```json
{
  "_id": ObjectId,
  "name": String,
  "user_id": ObjectId,
  "is_global": Boolean
}
```

- `_id`: Unique identifier for the category
- `name`: Category name
- `user_id`: Reference to the user who created this category (null for global categories)
- `is_global`: Whether this is a global category available to all users

## API Endpoints

Money Tracker provides the following routes:

### Authentication Routes

| Route                     | Method | Description                    | Authentication Required |
| ------------------------- | ------ | ------------------------------ | ----------------------- |
| `/login`                  | GET    | Display login form             | No                      |
| `/login`                  | POST   | Process login                  | No                      |
| `/register`               | GET    | Display registration form      | No                      |
| `/register`               | POST   | Process registration           | No                      |
| `/logout`                 | GET    | Log out user                   | Yes                     |
| `/verify_2fa`             | GET    | Display 2FA verification form  | No                      |
| `/verify_2fa`             | POST   | Process 2FA verification       | No                      |
| `/reset_password`         | GET    | Display password reset request | No                      |
| `/reset_password`         | POST   | Process password reset request | No                      |
| `/reset_password/<token>` | GET    | Display password reset form    | No                      |
| `/reset_password/<token>` | POST   | Process password reset         | No                      |

### Dashboard Routes

| Route        | Method | Description                        | Authentication Required |
| ------------ | ------ | ---------------------------------- | ----------------------- |
| `/`          | GET    | Home page or redirect to dashboard | No                      |
| `/dashboard` | GET    | Main dashboard                     | Yes                     |

### Transaction Routes

| Route                  | Method | Description                        | Authentication Required |
| ---------------------- | ------ | ---------------------------------- | ----------------------- |
| `/add_expense`         | GET    | Display add transaction form       | Yes                     |
| `/add_expense`         | POST   | Process new transaction            | Yes                     |
| `/delete_expense/<id>` | GET    | Delete transaction                 | Yes                     |
| `/transactions`        | GET    | View all transactions with filters | Yes                     |
| `/update_category`     | POST   | Update transaction category        | Yes                     |
| `/export_transactions` | GET    | Export transactions as CSV         | Yes                     |

### Salary Routes

| Route                   | Method | Description              | Authentication Required |
| ----------------------- | ------ | ------------------------ | ----------------------- |
| `/add_salary`           | GET    | Display add salary form  | Yes                     |
| `/add_salary`           | POST   | Process new salary entry | Yes                     |
| `/delete_salary/<id>`   | GET    | Delete salary entry      | Yes                     |
| `/salary_visualization` | GET    | View salary history      | Yes                     |

### Category Routes

| Route                   | Method | Description                      | Authentication Required |
| ----------------------- | ------ | -------------------------------- | ----------------------- |
| `/categories`           | GET    | Display category management page | Yes                     |
| `/categories`           | POST   | Process category updates         | Yes                     |
| `/add_category`         | POST   | Add new category                 | Yes                     |
| `/update_category_name` | POST   | Update category name             | Yes                     |
| `/delete_category/<id>` | GET    | Delete category                  | Yes                     |

### User Routes

| Route      | Method | Description       | Authentication Required |
| ---------- | ------ | ----------------- | ----------------------- |
| `/profile` | GET    | View user profile | Yes                     |

### Security Routes

| Route                            | Method | Description                        | Authentication Required |
| -------------------------------- | ------ | ---------------------------------- | ----------------------- |
| `/security_settings`             | GET    | View security settings dashboard   | Yes                     |
| `/setup_2fa`                     | GET    | Display 2FA setup page             | Yes                     |
| `/setup_2fa`                     | POST   | Process 2FA setup                  | Yes                     |
| `/disable_2fa`                   | POST   | Disable 2FA                        | Yes                     |
| `/change_password`               | POST   | Change user password               | Yes                     |
| `/security/sessions/revoke/<id>` | POST   | Revoke a specific session          | Yes                     |
| `/security/sessions/revoke_all`  | POST   | Revoke all sessions except current | Yes                     |

### Utility Routes

| Route     | Method | Description           | Authentication Required |
| --------- | ------ | --------------------- | ----------------------- |
| `/health` | GET    | Health check endpoint | No                      |

## Authentication System

Money Tracker uses Flask-Login for authentication:

### User Model

The User class in `models.py` implements the required methods for Flask-Login:

- `is_authenticated`: Always returns True for a valid User object
- `is_active`: Always returns True for a valid User object
- `is_anonymous`: Always returns False for a valid User object
- `get_id()`: Returns the user ID as a string

### Login Manager Configuration

```python
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
```

### Authentication Flow

1. **Login Process**:

   - User submits email and password
   - Application checks if account is locked due to too many failed attempts
   - Application retrieves user by email
   - Password is verified using `check_password_hash`
   - Failed login attempts are tracked and may trigger account lockout
   - If 2FA is enabled, user is redirected to 2FA verification
   - If valid (and 2FA verified if enabled), `login_user()` is called to create a session
   - A new session is recorded with device and IP information
   - User is redirected to the requested page or dashboard

2. **Two-Factor Authentication Process**:

   - After successful password verification, if 2FA is enabled:
     - User is redirected to 2FA verification page
     - User enters 6-digit code from authenticator app
     - Code is verified against the stored secret using PyOTP
     - If valid, login process continues
     - If invalid, user is prompted to try again
   - Backup codes can be used if user loses access to authenticator app

3. **Registration Process**:

   - User submits registration form
   - Application checks if username or email already exists
   - Password strength is validated (length, complexity)
   - If valid, password is hashed using `generate_password_hash`
   - New user is created in the database with security fields
   - Security log entry is created for account creation
   - Default categories are created for the user
   - User is redirected to login page

4. **Logout Process**:

   - User clicks logout
   - Current session is removed from active sessions
   - `logout_user()` is called to end the session
   - Security log entry is created for logout
   - User is redirected to login page

5. **Session Management**:

   - Each login creates a new session with unique ID
   - Session includes device information and IP address
   - Sessions are stored in the user document
   - Users can view and revoke active sessions
   - Sessions are updated with last activity timestamp

6. **Password Reset Process**:

   - User requests password reset by providing email
   - A secure token is generated and stored with expiration
   - Email with reset link is sent to user (simulated in development)
   - User clicks link and enters new password
   - Password strength is validated
   - New password is hashed and stored
   - All sessions are invalidated except the current one
   - Security log entry is created for password change

7. **Access Control**:
   - Protected routes use the `@login_required` decorator
   - Unauthenticated users are redirected to the login page
   - Rate limiting is applied to sensitive routes
   - The next parameter preserves the originally requested URL

## Security Framework

Money Tracker implements a comprehensive security framework to protect user accounts and sensitive financial data.

### Two-Factor Authentication (2FA)

The application uses TOTP (Time-based One-Time Password) for two-factor authentication:

```python
# Generate a new 2FA secret
secret = pyotp.random_base32()

# Create a TOTP object
totp = pyotp.TOTP(secret)

# Verify a token
is_valid = totp.verify(token)
```

- **Setup Process**:

  - A random secret is generated using `pyotp.random_base32()`
  - A QR code is generated containing the secret and app information
  - The user scans the QR code with an authenticator app
  - The user verifies setup by entering a code from the app
  - Backup codes are generated for account recovery

- **Verification Process**:
  - User enters the 6-digit code from their authenticator app
  - Code is verified against the stored secret using PyOTP
  - Backup codes can be used as an alternative

### Rate Limiting

Flask-Limiter is used to prevent brute force attacks and abuse:

```python
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    # Login logic
```

- **Protected Routes**:
  - `/login`: 10 requests per minute
  - `/register`: 10 requests per hour
  - `/reset_password`: 5 requests per hour
  - `/reset_password/<token>`: 10 requests per hour

### Account Lockout

The application implements account lockout after multiple failed login attempts:

- Failed login attempts are tracked in the user document
- After 5 failed attempts, the account is locked for 15 minutes
- The lockout is enforced by checking `account_locked_until` timestamp
- Successful login resets the failed attempt counter

### Session Management

Each user session is tracked with detailed information:

```json
{
  "session_id": "unique-session-id",
  "created_at": DateTime,
  "last_active": DateTime,
  "ip_address": "user-ip-address",
  "user_agent": "browser-and-device-info"
}
```

- Sessions are stored in the user document
- Each login creates a new session with a unique ID
- Users can view all active sessions
- Users can revoke individual sessions or all sessions except the current one
- Session activity is updated on each request

### Security Logging

All security-related events are logged in the user document:

```json
{
  "action": "login_success",
  "timestamp": DateTime,
  "ip_address": "user-ip-address",
  "user_agent": "browser-and-device-info"
}
```

- **Logged Events**:
  - Account creation
  - Successful and failed login attempts
  - Password changes and reset requests
  - 2FA setup, enabling, and disabling
  - Session creation and termination
  - Account lockouts

### Password Security

The application enforces strong password policies:

- Passwords must be at least 8 characters long
- Passwords must include uppercase letters, lowercase letters, numbers, and special characters
- Passwords are hashed using Werkzeug's `generate_password_hash` function
- Password reset tokens are securely generated and have a 24-hour expiration
- Password changes require current password verification
