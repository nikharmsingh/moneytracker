# Money Tracker

A Flask-based web application for tracking personal finances, expenses, and income. Built with MongoDB for data storage.

📚 **[Check out our comprehensive Wiki](wiki/index.md)** for detailed documentation, guides, and FAQs.

## Features

- **User Authentication**

  - Secure login and registration system
  - User-specific data isolation

- **Transaction Management**

  - Track both expenses (debits) and income (credits)
  - Categorize transactions with customizable categories
  - Add, edit, and delete transactions
  - Update transaction categories directly from the dashboard

- **Financial Dashboard**

  - Overall financial summary (total credits and debits)
  - Current month summary with average daily spend
  - Interactive pie chart for spending by category
  - Recent transactions list

- **Category Management**

  - Create, edit, and delete custom categories
  - Global and user-specific categories
  - Assign categories to transactions

- **Data Filtering & Export**

  - Filter transactions by date range
  - Filter spending chart by year and month
  - Download transactions as CSV for custom date ranges

- **Salary Tracking**

  - Track monthly salary/income
  - Visualize salary history
  - Automatic display of previous month's salary when current month is zero

- **Responsive Design**
  - Bootstrap 5 UI components
  - Mobile-friendly interface
  - Clean, intuitive user experience

## Tech Stack

- **Backend**: Python, Flask
- **Database**: MongoDB
- **Frontend**: HTML, CSS, Bootstrap 5
- **Authentication**: Flask-Login
- **Data Visualization**: Chart.js

## Prerequisites

- Python 3.9 or higher
- MongoDB Atlas account (or local MongoDB instance)
- pip (Python package manager)

## Installation

1. Clone the repository:

```bash
git clone <your-repository-url>
cd money-tracker
```

2. Create and activate a virtual environment:

```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   Create a `.env` file in the root directory with the following content:

```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
MONGODB_URI=your-mongodb-uri-here
```

5. Run the application:

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
money-tracker/
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
```

## Usage

1. **Registration & Login**

   - Create a new account with a unique username
   - Log in with your credentials
   - Automatic redirection to dashboard after login

2. **Dashboard Overview**

   - View financial summary cards (total credits/debits)
   - See current month's summary with average daily spend
   - Visualize spending by category with interactive pie chart
   - Access recent transactions list

3. **Managing Transactions**

   - Add new transactions with the "Add Transaction" button
   - Select transaction type (Credit/Debit)
   - Assign a category and enter amount and description
   - Choose transaction date (defaults to current date)
   - Update transaction categories directly from the dashboard
   - Delete transactions as needed

4. **Category Management**

   - Access category management via "Manage Categories" button
   - Create new custom categories
   - Edit existing categories (user-specific only)
   - Delete categories (user-specific only)

5. **Filtering & Data Export**

   - Filter spending chart by year and month
   - View transactions list with date range filters
   - Export filtered transactions as CSV file

6. **Salary Tracking**
   - Add monthly salary entries
   - View salary history visualization
   - Track salary trends over time

## Health Check Endpoint

The application includes a `/health` endpoint that returns the status of the application and database connection, useful for monitoring in production environments.

## Deployment

The application is configured for deployment on Render.com:

1. **Create a Render.com Account**

   - Sign up at [Render.com](https://render.com)
   - Connect your GitHub account

2. **Create a New Web Service**

   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Select the branch to deploy (usually `main` or `master`)

3. **Configure the Service**

   - Name: `money-tracker` (or your preferred name)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Set Environment Variables**

   - Click on "Environment" tab
   - Add the following variables:
     ```
     FLASK_APP=app.py
     FLASK_ENV=production
     MONGODB_URI=your-mongodb-uri-here
     ```
   - For `SECRET_KEY`, you can use Render's "Generate Value" feature
   - For `MONGODB_URI`, paste your MongoDB Atlas connection string

5. **Deploy**

   - Click "Create Web Service"
   - Render will automatically deploy your application
   - The deployment URL will be provided once complete

6. **Post-Deployment**
   - Monitor the deployment logs for any issues
   - Test the application using the provided URL
   - Set up automatic deployments for future updates

Note: Make sure your MongoDB Atlas database allows connections from Render's IP addresses. You may need to:

- Add `0.0.0.0/0` to your MongoDB Atlas IP whitelist
- Or add specific Render IP addresses to your whitelist

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask for the web framework
- MongoDB for the database
- Bootstrap for the UI components
- Chart.js for data visualization
