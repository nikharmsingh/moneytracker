from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
import csv
from io import StringIO
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Expense, Salary, db, Category

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))

# Add custom Jinja2 filter for currency formatting
@app.template_filter('format_currency')
def format_currency(value):
    if value is None:
        return "0"
    return f"{int(value):,}"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Login Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.get_by_username(username)
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if User.get_by_username(username):
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        User.create(username, hashed_password)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Existing Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def index():
    # Fix any categories missing the is_global flag
    Category.fix_missing_is_global()
    
    # Ensure user has default categories
    categories = Category.get_by_user(current_user.id)
    if not categories:
        User.create_default_categories(current_user.id)
        categories = Category.get_by_user(current_user.id)
    # Deduplicate by name, prefer user-specific over global
    unique_categories = {}
    for c in categories:
        if c.name not in unique_categories or not c.is_global:
            unique_categories[c.name] = c
    categories = list(unique_categories.values())
    
    # Fix any transactions with invalid category IDs
    Expense.fix_invalid_categories(current_user.id)
    
    # Get all expenses sorted by date in descending order
    expenses = Expense.get_by_user(current_user.id)
    
    # Build a lookup dictionary for category_id to name
    category_dict = {c.id: c.name for c in categories}
    for expense in expenses:
        expense.category_name = category_dict.get(expense.category_id, 'Unknown')
    
    # Get 5 most recent transactions
    recent_transactions = sorted(expenses, key=lambda x: x.date, reverse=True)[:5]
    
    # Calculate totals based on transaction type
    total_credit = sum(expense.amount for expense in expenses if expense.transaction_type == 'CR')
    total_debit = sum(expense.amount for expense in expenses if expense.transaction_type == 'DR')
    
    # Calculate current month's debits for average daily spend
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')
    current_month_name = current_date.strftime('%B %Y')  # Format: "April 2024"
    
    current_month_debits = sum(
        expense.amount for expense in expenses 
        if expense.date.strftime('%Y-%m') == current_month 
        and expense.transaction_type == 'DR'
    )
    
    # Calculate days passed in current month
    days_in_month = current_date.day
    
    # Calculate average daily spend
    avg_daily_spend = current_month_debits / days_in_month if days_in_month > 0 else 0

    # Calculate category-wise spending
    category_spending = {}
    for expense in expenses:
        if expense.transaction_type == 'DR':  # Only count debits for spending
            category = expense.category_name
            if category not in category_spending:
                category_spending[category] = 0
            category_spending[category] += expense.amount
    
    # Filter out "Unknown" category for the chart
    filtered_spending = {k: v for k, v in category_spending.items() if k != 'Unknown'}
    
    # If there are any expenses with "Unknown" category, add an "Other" category
    if 'Unknown' in category_spending and category_spending['Unknown'] > 0:
        filtered_spending['Other'] = category_spending['Unknown']
    
    # Convert to lists for the chart
    spending_categories = list(filtered_spending.keys())
    spending_amounts = list(filtered_spending.values())
    
    return render_template('index.html', 
                         expenses=expenses, 
                         total_credit=total_credit,
                         total_debit=total_debit,
                         avg_daily_spend=avg_daily_spend,
                         current_month_name=current_month_name,
                         spending_categories=spending_categories,
                         spending_amounts=spending_amounts,
                         recent_transactions=recent_transactions,
                         categories=categories)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category_id = request.form['category']  # Now this is the category's _id
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        transaction_type = request.form['transaction_type']
        
        Expense.create(amount, category_id, description, date, transaction_type, current_user.id)
        flash('Expense added successfully!')
        return redirect(url_for('index'))
    
    # Get both global and user-specific categories
    categories = Category.get_by_user(current_user.id)
    # Deduplicate by name, prefer user-specific over global
    unique_categories = {}
    for c in categories:
        if c.name not in unique_categories or not c.is_global:
            unique_categories[c.name] = c
    categories = list(unique_categories.values())
    return render_template('add_expense.html', categories=categories)

@app.route('/add_salary', methods=['GET', 'POST'])
@login_required
def add_salary():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        
        Salary.create(amount, date, current_user.id)
        flash('Salary added successfully!')
        return redirect(url_for('index'))
    return render_template('add_salary.html')

@app.route('/delete_expense/<id>')
@login_required
def delete_expense(id):
    Expense.delete(id, current_user.id)
    flash('Expense deleted successfully!')
    return redirect(url_for('index'))

@app.route('/delete_salary/<id>')
@login_required
def delete_salary(id):
    Salary.delete(id, current_user.id)
    flash('Salary deleted successfully!')
    return redirect(url_for('index'))

@app.route('/salary_visualization')
@login_required
def salary_visualization():
    salaries = Salary.get_by_user(current_user.id)
    expenses = Expense.get_by_user(current_user.id)
    
    # Group salaries by month
    monthly_salaries = {}
    for salary in salaries:
        month = salary.date.strftime('%Y-%m')
        if month not in monthly_salaries:
            monthly_salaries[month] = 0
        monthly_salaries[month] += salary.amount
    
    # Sort by month and prepare data for the chart
    sorted_months = sorted(monthly_salaries.keys())
    salary_data = {
        'months': [datetime.strptime(month, '%Y-%m').strftime('%b %Y') for month in sorted_months],
        'amounts': [monthly_salaries[month] for month in sorted_months]
    }

    # Get current month
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')
    current_month_name = current_date.strftime('%B %Y')
    
    # Get current month's salary
    current_month_salary = monthly_salaries.get(current_month, 0)
    display_month = current_month_name
    
    # If current month salary is zero, show last non-zero month
    if current_month_salary == 0 and sorted_months:
        for prev_month in reversed(sorted_months):
            if monthly_salaries[prev_month] > 0:
                current_month_salary = monthly_salaries[prev_month]
                display_month = datetime.strptime(prev_month, '%Y-%m').strftime('%B %Y')
                break
    
    # Calculate current month's transactions
    current_month_credits = sum(
        expense.amount for expense in expenses 
        if expense.date.strftime('%Y-%m') == current_month 
        and expense.transaction_type == 'CR'
    )
    
    current_month_debits = sum(
        expense.amount for expense in expenses 
        if expense.date.strftime('%Y-%m') == current_month 
        and expense.transaction_type == 'DR'
    )
    
    return render_template('salary_visualization.html', 
                         salary_data=salary_data,
                         current_salary=current_month_salary,
                         current_month_name=display_month,
                         total_credits=current_month_credits,
                         total_debits=current_month_debits)

@app.route('/health')
def health_check():
    try:
        # Check database connection
        db.command('ping')
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    health_data = {
        "status": "up",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "version": "1.0.0"
    }
    
    return jsonify(health_data)

@app.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    # Fix any categories missing the is_global flag
    Category.fix_missing_is_global()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            name = request.form['name']
            Category.create(name, current_user.id, is_global=False)  # New categories are always non-global
            flash('Category added successfully!', 'success')
        elif action == 'update':
            category_id = request.form['category_id']
            new_name = request.form['name']
            # Only allow updating user's own categories
            Category.update(category_id, new_name, current_user.id)
            flash('Category updated successfully!', 'success')
        elif action == 'delete':
            category_id = request.form['category_id']
            # Only allow deleting user's own categories
            Category.delete(category_id, current_user.id)
            flash('Category deleted successfully!', 'success')
        
        return redirect(url_for('manage_categories'))
    
    # Get both user-specific and global categories
    categories = Category.get_by_user(current_user.id)
    # Deduplicate by name, prefer user-specific over global
    unique_categories = {}
    for c in categories:
        if c.name not in unique_categories or not c.is_global:
            unique_categories[c.name] = c
    categories = list(unique_categories.values())
    return render_template('categories.html', categories=categories)

@app.route('/update_transaction_category/<id>', methods=['POST'])
@login_required
def update_transaction_category(id):
    new_category_id = request.form['category']
    Expense.update_category(id, new_category_id, current_user.id)
    flash('Transaction category updated successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/transactions')
@login_required
def view_transactions():
    # Get date range parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Fix any transactions with invalid category IDs
    Expense.fix_invalid_categories(current_user.id)
    
    # Build query based on date range
    query = {'user_id': current_user.id}
    if start_date and end_date:
        query['date'] = {
            '$gte': datetime.strptime(start_date, '%Y-%m-%d'),
            '$lte': datetime.strptime(end_date, '%Y-%m-%d')
        }
    elif start_date:
        query['date'] = {'$gte': datetime.strptime(start_date, '%Y-%m-%d')}
    elif end_date:
        query['date'] = {'$lte': datetime.strptime(end_date, '%Y-%m-%d')}
    
    # Get all expenses sorted by timestamp in descending order
    expenses = list(db.expenses.find(query).sort('timestamp', -1))
    
    # Get both global and user-specific categories
    categories = Category.get_by_user(current_user.id)
    # Deduplicate by name, prefer user-specific over global
    unique_categories = {}
    for c in categories:
        if c.name not in unique_categories or not c.is_global:
            unique_categories[c.name] = c
    categories = list(unique_categories.values())
    category_dict = {c.id: c.name for c in categories}
    
    # Convert expenses to Expense objects for consistent handling
    expenses = [Expense(expense) for expense in expenses]
    
    # Attach category name to each expense
    for expense in expenses:
        expense.category_name = category_dict.get(expense.category_id, 'Unknown')
    
    # Handle CSV download
    if request.args.get('download') == 'csv':
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Date', 'Type', 'Category', 'Amount', 'Description', 'Added On'])
        
        # Write data
        for expense in expenses:
            writer.writerow([
                expense.date.strftime('%Y-%m-%d'),
                'Credit' if expense.transaction_type == 'CR' else 'Debit',
                expense.category_name,
                expense.amount,
                expense.description,
                expense.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Create response
        output.seek(0)
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=transactions.csv'
        response.headers['Content-type'] = 'text/csv'
        return response
    
    return render_template('transactions.html', expenses=expenses, categories=categories)

if __name__ == '__main__':
    app.run(debug=True) 