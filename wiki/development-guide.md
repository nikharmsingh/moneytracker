# Development Guide

[Home](index.md) | [User Guide](user-guide.md) | [Technical Docs](technical-docs.md) | [Development Guide](development-guide.md) | [Deployment Guide](deployment-guide.md) | [FAQ](faq.md)

This guide provides information for developers who want to contribute to or extend the Money Tracker application.

## Table of Contents

- [Project Structure](#project-structure)
- [Setting Up Development Environment](#setting-up-development-environment)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Common Issues](#common-issues)
- [Contributing](#contributing)

## Project Structure

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

### Key Files

- **app.py**: Contains all route definitions and application logic
- **models.py**: Defines data models and database interactions
- **templates/base.html**: Base template that all other templates extend
- **static/css/style.css**: Custom CSS styles

## Setting Up Development Environment

### Prerequisites

- Python 3.9 or higher
- MongoDB (local instance or Atlas)
- Git

### Setup Steps

1. **Fork and clone the repository**:

   ```bash
   git clone https://github.com/your-username/moneytracker.git
   cd moneytracker
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Create a .env file**:

   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your-dev-secret-key
   MONGODB_URI=mongodb://localhost:27017/money_tracker
   ```

5. **Run the application in development mode**:
   ```bash
   python app.py
   ```

### Development Tools

Consider using these tools to enhance your development workflow:

- **Flask Debug Toolbar**: For debugging Flask applications
- **MongoDB Compass**: GUI for MongoDB
- **Visual Studio Code**: With Python and MongoDB extensions
- **Postman**: For testing API endpoints

## Adding New Features

When adding new features to Money Tracker, follow these steps:

### 1. Plan the Feature

- Define the user story and acceptance criteria
- Design the UI/UX flow
- Identify database changes needed

### 2. Implement the Model

If your feature requires new data structures:

1. Add new classes or methods to `models.py`
2. Create methods for CRUD operations
3. Test database interactions

Example of adding a new model:

```python
class Budget:
    def __init__(self, budget_data):
        self.id = str(budget_data['_id'])
        self.amount = budget_data['amount']
        self.category_id = str(budget_data['category_id'])
        self.month = budget_data['month']
        self.year = budget_data['year']
        self.user_id = budget_data['user_id']

    @staticmethod
    def create(amount, category_id, month, year, user_id):
        budget_data = {
            'amount': amount,
            'category_id': ObjectId(category_id),
            'month': month,
            'year': year,
            'user_id': user_id
        }
        result = db.budgets.insert_one(budget_data)
        budget_data['_id'] = result.inserted_id
        return Budget(budget_data)

    @staticmethod
    def get_by_user(user_id):
        budgets = db.budgets.find({'user_id': user_id})
        return [Budget(budget) for budget in budgets]
```

### 3. Create the Routes

Add new routes to `app.py`:

```python
@app.route('/budgets', methods=['GET'])
@login_required
def budgets():
    user_budgets = Budget.get_by_user(current_user.id)
    categories = Category.get_by_user(current_user.id)
    return render_template('budgets.html',
                          budgets=user_budgets,
                          categories=categories)

@app.route('/add_budget', methods=['POST'])
@login_required
def add_budget():
    amount = float(request.form['amount'])
    category_id = request.form['category']
    month = int(request.form['month'])
    year = int(request.form['year'])

    Budget.create(amount, category_id, month, year, current_user.id)
    flash('Budget added successfully!')
    return redirect(url_for('budgets'))
```

### 4. Design the Templates

Create or modify HTML templates in the `templates/` directory:

```html
{% extends "base.html" %} {% block content %}
<div class="container mt-4">
  <h1>Manage Budgets</h1>

  <div class="card mb-4">
    <div class="card-header">Add New Budget</div>
    <div class="card-body">
      <form action="{{ url_for('add_budget') }}" method="post">
        <!-- Form fields -->
        <button type="submit" class="btn btn-primary">Add Budget</button>
      </form>
    </div>
  </div>

  <div class="card">
    <div class="card-header">Your Budgets</div>
    <div class="card-body">
      <!-- Display budgets -->
    </div>
  </div>
</div>
{% endblock %}
```

### 5. Update Navigation

Add links to your new feature in the navigation menu:

```html
<li class="nav-item">
  <a class="nav-link" href="{{ url_for('budgets') }}">Budgets</a>
</li>
```

### 6. Test the Feature

- Test manually across different scenarios
- Ensure it works on mobile devices
- Check for edge cases and error handling

## Testing

Currently, Money Tracker does not have automated tests. When implementing tests, consider:

### Unit Tests

For testing individual functions and methods:

```python
# test_models.py
import unittest
from models import User, Category
from bson import ObjectId

class TestCategoryModel(unittest.TestCase):
    def setUp(self):
        # Setup test database connection
        # Create test user
        pass

    def test_create_category(self):
        # Test category creation
        category = Category.create("Test Category", "test_user_id")
        self.assertEqual(category.name, "Test Category")
        self.assertEqual(category.user_id, "test_user_id")

    def tearDown(self):
        # Clean up test data
        pass
```

### Integration Tests

For testing interactions between components:

```python
# test_routes.py
import unittest
from app import app
from models import db

class TestAuthRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
```

### Testing Framework

Consider using pytest for Python testing:

```bash
pip install pytest
pytest
```

## Common Issues

### MongoDB Connection Issues

**Problem**: Unable to connect to MongoDB

**Solutions**:

- Check your MongoDB URI in the `.env` file
- Ensure MongoDB is running if using a local instance
- Verify network connectivity
- Check IP whitelist settings in MongoDB Atlas

### Category Assignment Problems

**Problem**: Transactions show "Unknown" category

**Solutions**:

- Run the `fix_invalid_categories` function
- Ensure categories exist before adding transactions
- Check for ObjectId conversion issues

```python
# Fix invalid categories manually
Expense.fix_invalid_categories(current_user.id)
```

### Date Filtering Issues

**Problem**: Date filters not working correctly

**Solutions**:

- Check date format consistency
- Ensure timezone handling is consistent
- Debug date comparison logic

### Chart Rendering Problems

**Problem**: Charts not displaying correctly

**Solutions**:

- Check for JavaScript console errors
- Ensure data is properly formatted for Chart.js
- Verify that the chart container has a height

## Contributing

### Code Style

When contributing to Money Tracker, please follow these style guidelines:

#### Python Code

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes

```python
def calculate_monthly_spending(expenses, year, month):
    """
    Calculate the total spending for a specific month.

    Args:
        expenses (list): List of Expense objects
        year (int): Year to filter by
        month (int): Month to filter by (1-12)

    Returns:
        float: Total spending amount
    """
    total = 0
    for expense in expenses:
        if (expense.date.year == year and
            expense.date.month == month and
            expense.transaction_type == 'DR'):
            total += expense.amount
    return total
```

#### HTML/CSS

- Use consistent indentation (2 or 4 spaces)
- Follow Bootstrap conventions for components
- Keep CSS organized in the style.css file

#### JavaScript

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

### Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Example:

```
Add budget management feature

- Add Budget model in models.py
- Create routes for viewing and adding budgets
- Add budget templates
- Update navigation to include budget link

Fixes #42
```
