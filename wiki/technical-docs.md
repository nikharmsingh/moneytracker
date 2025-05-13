# Technical Documentation

[Home](index.md) | [User Guide](user-guide.md) | [Technical Docs](technical-docs.md) | [Development Guide](development-guide.md) | [Deployment Guide](deployment-guide.md) | [FAQ](faq.md)

This document provides technical details about the Money Tracker application's architecture, database schema, and API endpoints.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Database Schema](#database-schema)
- [API Endpoints](#api-endpoints)
- [Authentication System](#authentication-system)

## Architecture Overview

Money Tracker follows a Model-View-Controller (MVC) architecture:

- **Models** (`models.py`): Defines data structures and database interactions
- **Views** (`templates/`): HTML templates for rendering the UI
- **Controller** (`app.py`): Handles HTTP requests and business logic

### Technology Stack

- **Backend Framework**: Flask
- **Database**: MongoDB
- **Authentication**: Flask-Login
- **Frontend**: HTML, CSS, JavaScript
- **CSS Framework**: Bootstrap 5
- **Data Visualization**: Chart.js

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
  "registered_on": DateTime
}
```

- `_id`: Unique identifier for the user
- `username`: Unique username for the user
- `email`: Unique email address for the user
- `password`: Hashed password using Werkzeug's security functions
- `registered_on`: Date and time when the user registered

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

| Route       | Method | Description               | Authentication Required |
| ----------- | ------ | ------------------------- | ----------------------- |
| `/login`    | GET    | Display login form        | No                      |
| `/login`    | POST   | Process login             | No                      |
| `/register` | GET    | Display registration form | No                      |
| `/register` | POST   | Process registration      | No                      |
| `/logout`   | GET    | Log out user              | Yes                     |

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
   - Application retrieves user by email
   - Password is verified using `check_password_hash`
   - If valid, `login_user()` is called to create a session
   - User is redirected to the requested page or dashboard

2. **Registration Process**:

   - User submits registration form
   - Application checks if username or email already exists
   - If unique, password is hashed using `generate_password_hash`
   - New user is created in the database
   - Default categories are created for the user
   - User is redirected to login page

3. **Logout Process**:

   - User clicks logout
   - `logout_user()` is called to end the session
   - User is redirected to login page

4. **Session Management**:

   - Flask-Login handles session creation and validation
   - User ID is stored in the session
   - `load_user()` retrieves the user object when needed

5. **Access Control**:
   - Protected routes use the `@login_required` decorator
   - Unauthenticated users are redirected to the login page
   - The next parameter preserves the originally requested URL
