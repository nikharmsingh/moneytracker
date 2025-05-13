# Frequently Asked Questions (FAQ)

[Home](index.md) | [User Guide](user-guide.md) | [Technical Docs](technical-docs.md) | [Development Guide](development-guide.md) | [Deployment Guide](deployment-guide.md) | [FAQ](faq.md)

This page answers common questions about the Money Tracker application.

## Table of Contents

- [General Questions](#general-questions)
- [Account Management](#account-management)
- [Transactions and Categories](#transactions-and-categories)
- [Data and Privacy](#data-and-privacy)
- [Technical Questions](#technical-questions)
- [Troubleshooting](#troubleshooting)

## General Questions

### What is Money Tracker?

Money Tracker is a web application that helps you manage your personal finances by tracking expenses, income, and visualizing spending patterns. It provides tools for categorizing transactions, monitoring monthly spending, and analyzing financial trends.

### Is Money Tracker free to use?

Yes, Money Tracker is an open-source application that you can deploy and use for free. You may incur costs for hosting the application and database if you choose to deploy it on cloud platforms.

### Can I use Money Tracker on my mobile device?

Yes, Money Tracker has a responsive design that works well on mobile devices, tablets, and desktops. You can access all features through your mobile browser without needing to install an app.

### Does Money Tracker support multiple currencies?

Currently, Money Tracker does not have built-in support for multiple currencies. All transactions are assumed to be in the same currency. This feature may be added in future updates.

## Account Management

### How do I create an account?

1. Visit the Money Tracker homepage
2. Click "Register" in the navigation menu
3. Enter your username, email address, and password
4. Click "Register" to create your account

### How do I reset my password?

Currently, Money Tracker does not have an automated password reset feature. This feature is planned for future releases. If you forget your password, please contact the administrator of your deployment.

### Can I delete my account?

Account deletion is not currently available through the user interface. This feature is planned for future releases. If you need to delete your account, please contact the administrator of your deployment.

### Is my password stored securely?

Yes, Money Tracker uses Werkzeug's security functions to hash passwords before storing them in the database. The original password is never stored, only a secure hash.

## Transactions and Categories

### How do I add a new transaction?

1. Log in to your account
2. Click "Add Transaction" on the dashboard
3. Select the transaction type (Credit/Debit)
4. Enter the amount, category, description, and date
5. Click "Add" to save the transaction

### Can I edit a transaction after creating it?

Currently, direct editing of transactions is not supported. To modify a transaction:

1. Delete the incorrect transaction
2. Create a new transaction with the correct information

You can update the category of a transaction directly from the dashboard by clicking on the category name.

### What's the difference between Credit and Debit transactions?

- **Credit (CR)**: Represents money coming in (income, refunds, etc.)
- **Debit (DR)**: Represents money going out (expenses, payments, etc.)

### How do I create custom categories?

1. Click "Manage Categories" on the dashboard
2. Enter a new category name in the input field
3. Click "Add Category"

### Can I delete default categories?

No, default (global) categories cannot be deleted. These categories are available to all users and provide a consistent base for categorization. You can create your own custom categories in addition to the default ones.

## Data and Privacy

### Is my financial data secure?

Money Tracker uses secure authentication and stores passwords as hashed values. Your data is stored in MongoDB with access controls. The security of your deployment depends on how you configure your hosting environment and database.

### Can other users see my transactions?

No, Money Tracker implements user isolation. Each user can only see their own transactions, categories, and salary information. The application enforces this separation at the database query level.

### How can I back up my data?

You can export your transactions as CSV files using the "Export as CSV" feature on the Transactions page. For a complete backup, you would need to back up your MongoDB database.

### Does Money Tracker share my data with third parties?

No, Money Tracker does not share your data with any third parties. The application runs entirely on your own infrastructure, and data remains within your control.

## Technical Questions

### What technologies does Money Tracker use?

Money Tracker is built with:

- **Backend**: Python, Flask
- **Database**: MongoDB
- **Frontend**: HTML, CSS, Bootstrap 5
- **Authentication**: Flask-Login
- **Data Visualization**: Chart.js

### Can I import data from other financial apps?

Direct import is not currently supported. You can manually add transactions or consider contributing this feature to the project.

### Can I run Money Tracker offline?

Yes, you can run Money Tracker locally with a local MongoDB instance for completely offline usage. Follow the installation instructions in the README, using a local MongoDB URI.

### Is there an API for integrating with other applications?

Currently, Money Tracker does not provide a public API. This feature may be added in future updates.

## Troubleshooting

### I can't log in to my account

If you're having trouble logging in:

1. Ensure you're using the correct email address
2. Check that your password is correct
3. Clear your browser cookies and cache
4. Try using a different browser

If you still can't log in, you may need to reset your password through your deployment administrator.

### My transactions aren't showing up in the dashboard

If your transactions aren't appearing:

1. Check that you're logged in with the correct account
2. Verify that the transactions were successfully added
3. Clear your browser cache and reload the page
4. Check for any error messages in the browser console

### The spending chart is not displaying correctly

If the spending chart isn't rendering properly:

1. Ensure you have at least one debit transaction
2. Check that your transactions have valid categories
3. Try selecting different time periods using the filters
4. Check for JavaScript errors in your browser console

### How do I fix "Unknown" categories in my transactions?

If your transactions show "Unknown" category:

1. Go to the dashboard
2. Click on the "Unknown" category name
3. Select a valid category from the dropdown
4. Click "Update"

This issue can occur if categories were deleted or if there were database migration issues.

### The application is running slowly

If Money Tracker is performing slowly:

1. Check your internet connection
2. Consider upgrading your hosting plan if using a cloud provider
3. Optimize your MongoDB database (add indexes, etc.)
4. Reduce the number of transactions by archiving old data
