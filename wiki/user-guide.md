# User Guide

[Home](index.md) | [User Guide](user-guide.md) | [Technical Docs](technical-docs.md) | [Development Guide](development-guide.md) | [Deployment Guide](deployment-guide.md) | [FAQ](faq.md)

This guide will help you get started with Money Tracker and make the most of its features.

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Dashboard Overview](#dashboard-overview)
- [Managing Transactions](#managing-transactions)
- [Category Management](#category-management)
- [Salary Tracking](#salary-tracking)
- [Data Filtering and Export](#data-filtering-and-export)
- [User Profile](#user-profile)
- [Security Features](#security-features)

## Installation

### Prerequisites

Before installing Money Tracker, ensure you have:

- Python 3.9 or higher
- MongoDB Atlas account (or local MongoDB instance)
- pip (Python package manager)

### Setup Steps

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

4. **Set up environment variables**:
   Create a `.env` file in the root directory with the following content:

   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   MONGODB_URI=your-mongodb-uri-here
   ```

5. **Run the application**:

   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## Getting Started

### Registration and Login

1. **Registration**:

   - Navigate to the registration page by clicking "Register" on the home page
   - Enter a unique username, email address, and a strong password
     - Passwords must be at least 8 characters long and include uppercase letters, lowercase letters, numbers, and special characters
   - Click "Register" to create your account
   - Default expense categories will be automatically created for you

2. **Login**:

   - Enter your email and password on the login page
   - Check "Remember Me" for convenience on trusted devices
   - Click "Login" to access your dashboard
   - If two-factor authentication is enabled, you'll be prompted to enter a verification code
   - After 5 failed login attempts, your account will be temporarily locked for security reasons

3. **Password Reset**:
   - If you forget your password, click "Forgot password?" on the login page
   - Enter your email address to receive a password reset link
   - Click the link in the email to create a new password
   - The reset link is valid for 24 hours

## Dashboard Overview

The dashboard provides a comprehensive view of your financial status:

### Summary Cards

- **Total Credits**: Sum of all income transactions
- **Total Debits**: Sum of all expense transactions
- **Current Month Summary**: This month's credits and debits
- **Average Daily Spend**: Current month's expenses divided by days passed

### Spending Chart

- Pie chart showing expenses by category
- Filter by year and month using the dropdown menus
- Hover over segments to see detailed amounts

### Recent Transactions

- Quick view of your 5 most recent transactions
- Click on category names to change categories
- Delete transactions directly from this list

## Managing Transactions

### Adding Transactions

1. Click "Add Transaction" on the dashboard
2. Select transaction type (Credit/Debit)
3. Enter amount, category, description, and date
4. Click "Add" to save the transaction

### Editing Transactions

- Currently, direct editing is not supported
- To modify a transaction, delete it and create a new one
- You can update the category of a transaction directly from the dashboard

### Deleting Transactions

1. Click the trash icon next to any transaction
2. Confirm deletion when prompted

## Category Management

### Accessing Category Management

- Click "Manage Categories" on the dashboard

### Types of Categories

- **Global Categories**: Default categories available to all users (cannot be edited/deleted)
- **User Categories**: Custom categories created by you

### Creating Categories

1. Enter a new category name in the input field
2. Click "Add Category"

### Editing Categories

1. Click the edit icon next to a user category
2. Enter the new name
3. Click "Update"

### Deleting Categories

1. Click the trash icon next to a user category
2. Confirm deletion when prompted
3. Note: Transactions with deleted categories will be reassigned to "Other"

## Salary Tracking

### Adding Salary Entries

1. Click "Add Salary" on the dashboard
2. Enter the amount and date
3. Click "Add" to save

### Viewing Salary History

1. Navigate to "Salary Visualization" from the dashboard
2. View monthly salary trends in the bar chart
3. See monthly expenses alongside salary for comparison

### Deleting Salary Entries

1. Navigate to "Salary Visualization"
2. Click the trash icon next to any salary entry
3. Confirm deletion when prompted

## Data Filtering and Export

### Filtering Transactions

1. Navigate to "All Transactions" from the dashboard
2. Use the date range pickers to select start and end dates
3. Click "Filter" to apply

### Exporting Data

1. After filtering transactions, click "Export as CSV"
2. Choose to include or exclude specific columns
3. Download the CSV file for use in spreadsheet applications

## User Profile

### Accessing Profile

1. Click on your username in the navigation bar
2. Select "Profile" from the dropdown menu

### Profile Information

- View account statistics
- See total transactions, credits, debits, and balance
- View current month's spending and average daily spend
- Access security settings via the "Security Settings" button

## Security Features

Money Tracker includes comprehensive security features to protect your account and financial data.

### Security Settings

To access security settings:

1. Click on your username in the navigation bar and select "Profile"
2. Click the "Security Settings" button on your profile page
3. Or click "Security Settings" directly from the main navigation menu

### Two-Factor Authentication (2FA)

Two-factor authentication adds an extra layer of security by requiring a verification code in addition to your password when logging in.

#### Setting Up 2FA

1. Navigate to Security Settings
2. In the "Two-Factor Authentication" tab, click "Set Up Two-Factor Authentication"
3. Install an authenticator app on your mobile device if you don't already have one:
   - Google Authenticator ([Android](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2), [iOS](https://apps.apple.com/app/google-authenticator/id388497605))
   - Authy ([Android](https://play.google.com/store/apps/details?id=com.authy.authy), [iOS](https://apps.apple.com/app/authy/id494168017))
   - Microsoft Authenticator ([Android](https://play.google.com/store/apps/details?id=com.azure.authenticator), [iOS](https://apps.apple.com/app/microsoft-authenticator/id983156458))
4. Scan the QR code with your authenticator app
5. Enter the 6-digit verification code from your app to complete setup
6. Save your backup codes in a secure location (these will only be shown once)

#### Using 2FA

1. When logging in, after entering your password, you'll be prompted for a verification code
2. Open your authenticator app and enter the 6-digit code
3. If you've lost access to your authenticator app, you can use one of your backup codes

#### Disabling 2FA

1. Navigate to Security Settings
2. In the "Two-Factor Authentication" tab, enter your password
3. Click "Disable Two-Factor Authentication"

### Session Management

Money Tracker allows you to view and manage all your active login sessions.

#### Viewing Active Sessions

1. Navigate to Security Settings
2. Click the "Active Sessions" tab
3. View all devices currently logged into your account

#### Revoking Sessions

1. To revoke a specific session, click the "Revoke" button next to it
2. To revoke all sessions except your current one, click "Revoke All Other Sessions"
3. After revoking a session, that device will be logged out immediately

### Security Logs

Security logs help you monitor account activity and detect unauthorized access.

1. Navigate to Security Settings
2. Click the "Security Logs" tab
3. View a chronological list of security events, including:
   - Successful and failed login attempts
   - Password changes
   - Two-factor authentication setup or changes
   - Session creation and termination
   - Account lockouts

### Password Management

#### Changing Your Password

1. Navigate to Security Settings
2. Click the "Password" tab
3. Enter your current password
4. Enter and confirm your new password
   - Must be at least 8 characters long
   - Must include uppercase letters, lowercase letters, numbers, and special characters
5. Click "Change Password"
