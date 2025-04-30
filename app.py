from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Expense, Salary

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))

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
    expenses = Expense.get_by_user(current_user.id)
    salaries = Salary.get_by_user(current_user.id)
    
    # Calculate totals based on transaction type
    total_credit = sum(expense.amount for expense in expenses if expense.transaction_type == 'CR')
    total_debit = sum(expense.amount for expense in expenses if expense.transaction_type == 'DR')
    total_salary = sum(salary.amount for salary in salaries)
    
    # Balance = Salary + Credits - Debits
    balance = total_salary + total_credit - total_debit

    # Calculate category-wise spending
    category_spending = {}
    for expense in expenses:
        if expense.transaction_type == 'DR':  # Only count debits for spending
            category = expense.category
            if category not in category_spending:
                category_spending[category] = 0
            category_spending[category] += expense.amount
    
    # Convert to lists for the chart
    categories = list(category_spending.keys())
    amounts = list(category_spending.values())
    
    return render_template('index.html', 
                         expenses=expenses, 
                         salaries=salaries, 
                         total_credit=total_credit,
                         total_debit=total_debit,
                         total_salary=total_salary, 
                         balance=balance,
                         spending_categories=categories,
                         spending_amounts=amounts)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category = request.form['category']
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        transaction_type = request.form['transaction_type']
        
        Expense.create(amount, category, description, date, transaction_type, current_user.id)
        flash('Expense added successfully!')
        return redirect(url_for('index'))
    return render_template('add_expense.html')

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
    
    return render_template('salary_visualization.html', salary_data=salary_data)

if __name__ == '__main__':
    app.run(debug=True) 