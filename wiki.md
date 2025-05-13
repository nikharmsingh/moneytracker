# Money Tracker Wiki

Welcome to the Money Tracker Wiki! This comprehensive guide will help you understand, use, and contribute to the Money Tracker application.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
   - [Installation](#installation)
   - [Configuration](#configuration)
   - [Running the Application](#running-the-application)
3. [User Guide](#user-guide)
   - [Registration and Login](#registration-and-login)
   - [Dashboard Overview](#dashboard-overview)
   - [Managing Transactions](#managing-transactions)
   - [Category Management](#category-management)
   - [Salary Tracking](#salary-tracking)
   - [Data Filtering and Export](#data-filtering-and-export)
   - [User Profile](#user-profile)
4. [Technical Documentation](#technical-documentation)
   - [Architecture Overview](#architecture-overview)
   - [Database Schema](#database-schema)
   - [API Endpoints](#api-endpoints)
   - [Authentication System](#authentication-system)
5. [Development Guide](#development-guide)
   - [Project Structure](#project-structure)
   - [Adding New Features](#adding-new-features)
   - [Testing](#testing)
   - [Common Issues](#common-issues)
6. [Deployment](#deployment)
   - [Deploying to Render.com](#deploying-to-rendercom)
   - [Environment Variables](#environment-variables)
   - [Database Setup](#database-setup)
7. [Contributing](#contributing)
   - [Code Style](#code-style)
   - [Pull Request Process](#pull-request-process)
8. [FAQ](#faq)

## Introduction

Money Tracker is a Flask-based web application designed to help users manage their personal finances. It provides tools for tracking expenses, income, and visualizing spending patterns. The application uses MongoDB for data storage and offers a responsive, user-friendly interface built with Bootstrap 5.

### Key Features

- **User Authentication**: Secure login and registration system
- **Transaction Management**: Track both expenses (debits) and income (credits)
- **Financial Dashboard**: Visualize spending patterns and financial summaries
- **Category Management**: Organize transactions with customizable categories
- **Salary Tracking**: Monitor income over time
- **Data Export**: Download transaction data for external analysis
- **Responsive Design**: Mobile-friendly interface

## Getting Started

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd moneytracker
   ```

2. **Create and activate a virtual environment**:

   ```bash
   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

1. **Set up environment variables**:
   Create a `.env` file in the root directory with the following content:

   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   MONGODB_URI=your-mongodb-uri-here
   ```

2. **MongoDB Setup**:
   - Create a MongoDB Atlas account or use a local MongoDB instance
   - Create a database named `money_tracker`
   - Update the `MONGODB_URI` in your `.env` file with your connection string

### Running the Application

1. **Start the application**:

   ```bash
   python app.py
   ```

2. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## User Guide

### Registration and Login

1. **Registration**:

   - Navigate to the registration page by clicking "Register" on the home page
   - Enter a unique username, email address, and password
   - Click "Register" to create your account
   - Default expense categories will be automatically created for you

2. **Login**:
   - Enter your email and password on the login page
   - Click "Login" to access your dashboard
   - Use the "Remember Me" option for convenience on trusted devices

### Dashboard Overview

The dashboard provides a comprehensive view of your financial status:

1. **Summary Cards**:

   - Total Credits: Sum of all income transactions
   - Total Debits: Sum of all expense transactions
   - Current Month Summary: This month's credits and debits
   - Average Daily Spend: Current month's expenses divided by days passed

2. **Spending Chart**:

   - Pie chart showing expenses by category
   - Filter by year and month using the dropdown menus
   - Hover over segments to see detailed amounts

3. **Recent Transactions**:
   - Quick view of your 5 most recent transactions
   - Click on category names to change categories
   - Delete transactions directly from this list

### Managing Transactions

1. **Adding Transactions**:

   - Click "Add Transaction" on the dashboard
   - Select transaction type (Credit/Debit)
   - Enter amount, category, description, and date
   - Click "Add" to save the transaction

2. **Editing Transactions**:

   - Currently, direct editing is not supported
   - To modify a transaction, delete it and create a new one
   - You can update the category of a transaction directly from the dashboard

3. **Deleting Transactions**:
   - Click the trash icon next to any transaction
   - Confirm deletion when prompted

### Category Management

1. **Accessing Category Management**:

   - Click "Manage Categories" on the dashboard

2. **Types of Categories**:

   - Global Categories: Default categories available to all users (cannot be edited/deleted)
   - User Categories: Custom categories created by you

3. **Creating Categories**:

   - Enter a new category name in the input field
   - Click "Add Category"

4. **Editing Categories**:

   - Click the edit icon next to a user category
   - Enter the new name
   - Click "Update"

5. **Deleting Categories**:
   - Click the trash icon next to a user category
   - Confirm deletion when prompted
   - Note: Transactions with deleted categories will be reassigned to "Other"

### Salary Tracking

1. **Adding Salary Entries**:

   - Click "Add Salary" on the dashboard
   - Enter the amount and date
   - Click "Add" to save

2. **Viewing Salary History**:

   - Navigate to "Salary Visualization" from the dashboard
   - View monthly salary trends in the bar chart
   - See monthly expenses alongside salary for comparison

3. **Deleting Salary Entries**:
   - Navigate to "Salary Visualization"
   - Click the trash icon next to any salary entry
   - Confirm deletion when prompted

### Data Filtering and Export

1. **Filtering Transactions**:

   - Navigate to "All Transactions" from the dashboard
   - Use the date range pickers to select start and end dates
   - Click "Filter" to apply

2. **Exporting Data**:
   - After filtering transactions, click "Export as CSV"
   - Choose to include or exclude specific columns
   - Download the CSV file for use in spreadsheet applications

### User Profile

1. **Accessing Profile**:

   - Click on your username in the navigation bar
   - Select "Profile" from the dropdown menu

2. **Profile Information**:
   - View account statistics
   - See total transactions, credits, debits, and balance
   - View current month's spending and average daily spend

## Technical Documentation

### Architecture Overview

Money Tracker follows a Model-View-Controller (MVC) architecture:

- **Models** (`models.py`): Defines data structures and database interactions
- **Views** (`templates/`): HTML templates for rendering the UI
- **Controller** (`app.py`): Handles HTTP requests and business logic

The application uses:

- Flask for the web framework
- MongoDB for data storage
- Flask-Login for authentication
- Chart.js for data visualization
- Bootstrap 5 for UI components

### Database Schema

Money Tracker uses MongoDB with the following collections:

1. **users**:

   - `_id`: ObjectId (primary key)
   - `username`: String (unique)
   - `email`: String (unique)
   - `password`: String (hashed)
   - `registered_on`: DateTime

2. **expenses**:

   - `_id`: ObjectId (primary key)
   - `amount`: Float
   - `category_id`: ObjectId (reference to categories)
   - `description`: String
   - `date`: DateTime
   - `transaction_type`: String ('CR' for credit, 'DR' for debit)
   - `user_id`: String (reference to users)
   - `timestamp`: DateTime

3. **salaries**:

   - `_id`: ObjectId (primary key)
   - `amount`: Float
   - `date`: DateTime
   - `user_id`: String (reference to users)

4. **categories**:
   - `_id`: ObjectId (primary key)
   - `name`: String
   - `user_id`: ObjectId (reference to users, null for global categories)
   - `is_global`: Boolean

### API Endpoints

Money Tracker provides the following routes:

#### Authentication Routes

- `GET/POST /login`: User login
- `GET/POST /register`: User registration
- `GET /logout`: User logout

#### Dashboard Routes

- `GET /`: Home page (redirects to dashboard if logged in)
- `GET /dashboard`: Main dashboard

#### Transaction Routes

- `GET/POST /add_expense`: Add new transaction
- `GET /delete_expense/<id>`: Delete transaction
- `GET/POST /transactions`: View all transactions with filtering
- `POST /update_category`: Update transaction category
- `GET /export_transactions`: Export transactions as CSV

#### Salary Routes

- `GET/POST /add_salary`: Add new salary entry
- `GET /delete_salary/<id>`: Delete salary entry
- `GET /salary_visualization`: View salary history

#### Category Routes

- `GET/POST /categories`: Manage categories
- `POST /add_category`: Add new category
- `POST /update_category_name`: Update category name
- `GET /delete_category/<id>`: Delete category

#### User Routes

- `GET /profile`: View user profile

#### Utility Routes

- `GET /health`: Health check endpoint

### Authentication System

Money Tracker uses Flask-Login for authentication:

1. **User Model**:

   - Implements UserMixin for Flask-Login compatibility
   - Provides methods for user retrieval and creation

2. **Login Process**:

   - User submits email and password
   - Password is verified against stored hash
   - Flask-Login creates a session for the user

3. **Registration Process**:

   - Validates username and email uniqueness
   - Hashes password using Werkzeug's security functions
   - Creates user record and default categories

4. **Session Management**:

   - Flask-Login handles session creation and validation
   - Sessions expire based on Flask's session configuration

5. **Access Control**:
   - `@login_required` decorator protects routes
   - Unauthenticated users are redirected to login page

## Development Guide

### Project Structure

```
moneytracker/
├── app.py                    # Main application file
├── models.py                 # Database models
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── templates/                # HTML templates
│   ├── base.html             # Base template with layout
│   ├── home.html             # Landing page
│   ├── index.html            # Main dashboard
│   ├── login.html            # Login page
│   ├── register.html         # Registration page
│   ├── add_expense.html      # Add transaction form
│   ├── add_salary.html       # Add salary form
│   ├── categories.html       # Category management
│   ├── transactions.html     # Transaction list with filters
│   └── salary_visualization.html  # Salary history visualization
└── static/                   # Static files (CSS, JS, images)
    └── css/
        └── style.css         # Custom CSS styles
```

### Adding New Features

When adding new features to Money Tracker, follow these steps:

1. **Plan the feature**:

   - Define the user story and acceptance criteria
   - Design the UI/UX flow
   - Identify database changes needed

2. **Implement the model**:

   - Add new collections or fields to `models.py` if needed
   - Create methods for CRUD operations

3. **Create the routes**:

   - Add new routes to `app.py`
   - Implement the business logic

4. **Design the templates**:

   - Create or modify HTML templates in the `templates/` directory
   - Use the existing base template for consistency

5. **Test the feature**:
   - Test manually across different scenarios
   - Ensure it works on mobile devices

### Testing

Currently, Money Tracker does not have automated tests. When implementing tests, consider:

1. **Unit Tests**:

   - Test individual functions and methods
   - Use pytest for Python testing

2. **Integration Tests**:

   - Test interactions between components
   - Focus on database operations and route handlers

3. **UI Tests**:
   - Test the user interface
   - Use Selenium or similar tools for browser automation

### Common Issues

1. **MongoDB Connection Issues**:

   - Ensure your MongoDB URI is correct
   - Check network connectivity
   - Verify IP whitelist settings in MongoDB Atlas

2. **Category Assignment Problems**:

   - If transactions show "Unknown" category, run the fix_invalid_categories function
   - Ensure categories exist before adding transactions

3. **Date Filtering Issues**:

   - Check date format consistency
   - Ensure timezone handling is consistent

4. **Chart Rendering Problems**:
   - Check for JavaScript console errors
   - Ensure data is properly formatted for Chart.js

## Deployment

### Deploying to Render.com

1. **Create a Render.com Account**:

   - Sign up at [Render.com](https://render.com)
   - Connect your GitHub account

2. **Create a New Web Service**:

   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Select the branch to deploy

3. **Configure the Service**:

   - Name: `money-tracker` (or your preferred name)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Set Environment Variables**:

   - Add required environment variables (see below)

5. **Deploy**:
   - Click "Create Web Service"
   - Monitor the deployment logs

### Environment Variables

Set these environment variables in your deployment environment:

- `FLASK_APP`: Set to `app.py`
- `FLASK_ENV`: Set to `production` for deployment
- `SECRET_KEY`: A secure random string for session encryption
- `MONGODB_URI`: Your MongoDB connection string

### Database Setup

1. **MongoDB Atlas**:

   - Create a MongoDB Atlas account
   - Create a new cluster
   - Create a database named `money_tracker`
   - Create a database user with read/write permissions
   - Get the connection string

2. **Security Settings**:
   - Add your deployment platform's IP to the MongoDB Atlas IP whitelist
   - Or allow access from anywhere (`0.0.0.0/0`) for simplicity

## Contributing

### Code Style

When contributing to Money Tracker, please follow these style guidelines:

1. **Python Code**:

   - Follow PEP 8 style guide
   - Use meaningful variable and function names
   - Add docstrings to functions and classes

2. **HTML/CSS**:

   - Use consistent indentation (2 or 4 spaces)
   - Follow Bootstrap conventions for components
   - Keep CSS organized in the style.css file

3. **JavaScript**:
   - Use ES6 syntax where possible
   - Add comments for complex logic
   - Keep functions small and focused

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: brief description"
   ```
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request**:
   - Provide a clear description of the changes
   - Reference any related issues
   - Wait for review and address feedback

## FAQ

### General Questions

**Q: Is my financial data secure?**
A: Yes, Money Tracker uses secure authentication and stores passwords as hashed values. Your data is stored in MongoDB with access controls.

**Q: Can I use Money Tracker on my mobile device?**
A: Yes, Money Tracker has a responsive design that works well on mobile devices, tablets, and desktops.

**Q: Is there a limit to how many transactions I can track?**
A: There is no built-in limit to the number of transactions. Performance may vary based on your MongoDB plan if using Atlas.

### Technical Questions

**Q: How do I reset my password?**
A: Currently, password reset functionality is not implemented. This feature is planned for future releases.

**Q: Can I import data from other financial apps?**
A: Direct import is not currently supported. You can manually add transactions or consider contributing this feature.

**Q: How do I back up my data?**
A: You can export your transactions as CSV files. For a complete backup, you would need to back up your MongoDB database.

**Q: Can I run Money Tracker offline?**
A: Yes, you can run Money Tracker locally with a local MongoDB instance for completely offline usage.
