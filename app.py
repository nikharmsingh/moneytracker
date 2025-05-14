# Import warning suppression module first
import suppress_warnings

import os
import csv
import calendar
import uuid
import re
import pyotp
import qrcode
import base64
from io import StringIO, BytesIO
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, Expense, Salary, db, Category, Budget
from bson import ObjectId
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail, Message
import re

app = Flask(__name__)

# Initialize Flask-Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Password strength validation function
def is_password_strong(password):
    """
    Check if a password meets the strength requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if not password or len(password) < 8:
        return False
    
    # Check for uppercase, lowercase, digit, and special character
    has_uppercase = bool(re.search(r'[A-Z]', password))
    has_lowercase = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    return has_uppercase and has_lowercase and has_digit and has_special
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))

# Enhanced session security
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Restrict cookie sending to same-site requests
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Session expiration

# Configure Flask-Mail
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', 'yes', '1']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@moneytracker.com')
mail = Mail(app)

# Rate limiting to prevent brute force attacks
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Make calendar module and built-in functions available to templates
app.jinja_env.globals['calendar'] = calendar
app.jinja_env.globals['min'] = min
app.jinja_env.globals['max'] = max
app.jinja_env.globals['round'] = round
app.jinja_env.globals['len'] = len
app.jinja_env.globals['range'] = range
app.jinja_env.globals['int'] = int
app.jinja_env.globals['str'] = str

# Add custom Jinja2 filter for currency formatting
@app.template_filter('format_currency')
def format_currency(value):
    if value is None:
        return "0"
    return f"{int(value):,}"
        
# Add custom Jinja2 filter for zip function
@app.template_filter('zip')
def zip_lists(a, b):
    return zip(a, b)
    
# Add custom Jinja2 filter for summing lists
@app.template_filter('sum')
def sum_list(value):
    return sum(value)
        
# Function to send password reset email
def send_password_reset_email(user, token):
    """Send password reset email to user"""
    reset_url = url_for('reset_password_token', token=token, _external=True)
    
    msg = Message(
        subject="Money Tracker - Password Reset",
        recipients=[user.email],
        html=render_template('email/reset_password.html', user=user, reset_url=reset_url),
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
        
# Add custom Jinja2 filter for date formatting
@app.template_filter('format_date')
def format_date(value):
    if value is None:
        return ""
    return value.strftime('%b %d, %Y')

# Add custom Jinja2 filter for percentage formatting
@app.template_filter('format_percentage')
def format_percentage(value):
    if value is None:
        return "0%"
    return f"{int(value)}%"

# Add custom Jinja2 filter for date formatting
@app.template_filter('format_date')
def format_date(value):
    if value is None:
        return ""
    return value.strftime('%Y-%m-%d')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Login Routes
@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Check if user is in 2FA verification process
    if 'awaiting_2fa' in session:
        return redirect(url_for('verify_2fa'))
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember_me = 'remember_me' in request.form
        
        user = User.get_by_email(email)
        
        # Record IP and user agent for security logs
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        if not user:
            flash('Invalid email or password', 'danger')
            return render_template('login.html')
        
        # Check if account is locked
        if user.is_account_locked():
            flash('Account is temporarily locked due to too many failed login attempts. Please try again later.', 'danger')
            return render_template('login.html')
        
        # Verify password
        if check_password_hash(user.password, password):
            # If 2FA is enabled, redirect to 2FA verification
            if user.two_factor_enabled:
                # Store user ID in session for 2FA verification
                session['awaiting_2fa'] = True
                session['user_id_2fa'] = user.id
                session['remember_me'] = remember_me
                
                # Record successful password verification
                user.record_login_attempt(True, ip_address, user_agent)
                
                return redirect(url_for('verify_2fa'))
            
            # If 2FA is not enabled, complete login
            login_user(user, remember=remember_me)
            
            # Generate a unique session ID and store it
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            user.add_session(session_id, ip_address, user_agent)
            
            # Record successful login
            user.record_login_attempt(True, ip_address, user_agent)
            
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            # Record failed login attempt
            user.record_login_attempt(False, ip_address, user_agent)
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/verify_2fa', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def verify_2fa():
    # Ensure user has completed first step of login
    if 'awaiting_2fa' not in session or 'user_id_2fa' not in session:
        return redirect(url_for('login'))
    
    user = User.get(session['user_id_2fa'])
    if not user:
        session.pop('awaiting_2fa', None)
        session.pop('user_id_2fa', None)
        session.pop('remember_me', None)
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        token = request.form['token']
        
        # Record IP and user agent for security logs
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Verify the token
        if user.verify_2fa_token(token):
            # Complete login
            login_user(user, remember=session.get('remember_me', False))
            
            # Generate a unique session ID and store it
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
            user.add_session(session_id, ip_address, user_agent)
            
            # Clean up 2FA session data
            session.pop('awaiting_2fa', None)
            session.pop('user_id_2fa', None)
            session.pop('remember_me', None)
            
            flash('Two-factor authentication successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
    
    return render_template('verify_2fa.html')

@app.route('/register', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate password strength
        if not is_password_strong(password):
            flash('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character', 'danger')
            return render_template('register.html', username=username, email=email)
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html', username=username, email=email)
        
        if User.get_by_username(username):
            flash('Username already exists', 'danger')
            return render_template('register.html', username='', email=email)
            
        if User.get_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('register.html', username=username, email='')
        
        # Record IP and user agent for security logs
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        hashed_password = generate_password_hash(password)
        user = User.create(username, email, hashed_password)
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

def is_password_strong(password):
    """Check if password meets strength requirements"""
    # At least 8 characters
    if len(password) < 8:
        return False
    
    # Check for at least one uppercase, lowercase, digit, and special character
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

@app.route('/profile')
@login_required
def profile():
    try:
        # Get all expenses for the user
        expenses = Expense.get_by_user(current_user.id)
        
        # Get all salaries for the user
        salaries = Salary.get_by_user(current_user.id)
        
        # Calculate totals with safe defaults
        total_transactions = len(expenses) if expenses else 0
        total_credit = sum(expense.amount for expense in expenses if expense.transaction_type == 'CR') if expenses else 0
        total_debit = sum(expense.amount for expense in expenses if expense.transaction_type == 'DR') if expenses else 0
        total_salary = sum(salary.amount for salary in salaries) if salaries else 0
        
        # Get count of user's own categories (excluding global ones)
        user_categories = Category.count_user_categories(current_user.id)
        
        # Calculate account balance
        account_balance = total_credit - total_debit + total_salary
        
        # Get current month's transactions
        current_date = datetime.now()
        current_month = current_date.strftime('%Y-%m')
        
        current_month_expenses = [
            expense for expense in expenses 
            if expense.date.strftime('%Y-%m') == current_month
        ] if expenses else []
        
        current_month_debits = sum(
            expense.amount for expense in current_month_expenses 
            if expense.transaction_type == 'DR'
        ) if current_month_expenses else 0
        
        # Calculate days passed in current month
        days_in_month = current_date.day
        
        # Calculate average daily spend for current month
        avg_daily_spend = current_month_debits / days_in_month if days_in_month > 0 else 0
        
        return render_template('profile.html', 
                              total_transactions=total_transactions,
                              total_credit=total_credit,
                              total_debit=total_debit,
                              total_salary=total_salary,
                              user_categories=user_categories,
                              account_balance=account_balance,
                              current_month_debits=current_month_debits,
                              avg_daily_spend=avg_daily_spend)
    except Exception as e:
        # Log the error and return a simple profile page with minimal data
        print(f"Error in profile route: {str(e)}")
        return render_template('profile.html',
                              total_transactions=0,
                              total_credit=0,
                              total_debit=0,
                              total_salary=0,
                              user_categories=0,
                              account_balance=0,
                              current_month_debits=0,
                              avg_daily_spend=0)

# Budget Management Routes
@app.route('/budgets')
@login_required
def manage_budgets():
    """View all budgets"""
    budgets = Budget.get_by_user(current_user.id)
    categories = Category.get_by_user(current_user.id)
    
    # Calculate spending and percentage for each budget
    for budget in budgets:
        budget.spent = budget.get_spending()
        budget.remaining = budget.get_remaining()
        budget.percentage = budget.get_percentage_used()
        
        # Get category name if this is a category budget
        if budget.category_id:
            for category in categories:
                if category.id == budget.category_id:
                    budget.category_name = category.name
                    break
        else:
            budget.category_name = 'All Categories'
    
    return render_template('budgets.html', 
                          budgets=budgets, 
                          categories=categories)

@app.route('/budgets/add', methods=['GET', 'POST'])
@login_required
def add_budget():
    """Add a new budget"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '')
            amount = float(request.form.get('amount', 0))
            category_id = request.form.get('category_id')
            period = request.form.get('period', 'monthly')
            
            # Handle empty category (means all categories)
            if category_id == '':
                category_id = None
                
            # Parse dates
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
            
            # Get notification threshold
            notification_threshold = int(request.form.get('notification_threshold', 80))
            
            # Get color
            color = request.form.get('color', '#4B6CB7')
            
            # Create the budget
            Budget.create(
                amount=amount,
                user_id=current_user.id,
                name=name,
                category_id=category_id,
                period=period,
                start_date=start_date,
                end_date=end_date,
                notification_threshold=notification_threshold,
                color=color
            )
            
            flash('Budget created successfully!', 'success')
            return redirect(url_for('manage_budgets'))
        except Exception as e:
            flash(f'Error creating budget: {str(e)}', 'danger')
    
    # For GET request, show the form
    categories = Category.get_by_user(current_user.id)
    
    # Set default dates (current month)
    today = datetime.now()
    start_date = today.replace(day=1).strftime('%Y-%m-%d')
    next_month = today.replace(day=28) + timedelta(days=4)
    end_date = (next_month - timedelta(days=next_month.day)).strftime('%Y-%m-%d')
    
    return render_template('add_budget.html', 
                          categories=categories,
                          start_date=start_date,
                          end_date=end_date)

@app.route('/budgets/edit/<budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    """Edit an existing budget"""
    budget = Budget.get_by_id(budget_id, current_user.id)
    if not budget:
        flash('Budget not found', 'danger')
        return redirect(url_for('manage_budgets'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '')
            amount = float(request.form.get('amount', 0))
            category_id = request.form.get('category_id')
            period = request.form.get('period', 'monthly')
            
            # Handle empty category (means all categories)
            if category_id == '':
                category_id = None
                
            # Parse dates
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d')
            
            # Get notification threshold
            notification_threshold = int(request.form.get('notification_threshold', 80))
            
            # Get color
            color = request.form.get('color', '#4B6CB7')
            
            # Update the budget
            Budget.update(
                budget_id=budget_id,
                user_id=current_user.id,
                amount=amount,
                name=name,
                category_id=category_id,
                period=period,
                start_date=start_date,
                end_date=end_date,
                notification_threshold=notification_threshold,
                color=color
            )
            
            flash('Budget updated successfully!', 'success')
            return redirect(url_for('manage_budgets'))
        except Exception as e:
            flash(f'Error updating budget: {str(e)}', 'danger')
    
    # For GET request, show the form with current values
    categories = Category.get_by_user(current_user.id)
    
    return render_template('edit_budget.html', 
                          budget=budget,
                          categories=categories)

@app.route('/budgets/delete/<budget_id>')
@login_required
def delete_budget(budget_id):
    """Delete a budget"""
    try:
        Budget.delete(budget_id, current_user.id)
        flash('Budget deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting budget: {str(e)}', 'danger')
    
    return redirect(url_for('manage_budgets'))

@app.route('/budgets/deactivate/<budget_id>')
@login_required
def deactivate_budget(budget_id):
    """Deactivate a budget"""
    try:
        Budget.deactivate(budget_id, current_user.id)
        flash('Budget deactivated successfully!', 'success')
    except Exception as e:
        flash(f'Error deactivating budget: {str(e)}', 'danger')
    
    return redirect(url_for('manage_budgets'))

@app.route('/budgets/overview')
@login_required
def budget_overview():
    """Show an overview of all active budgets"""
    active_budgets = Budget.get_active_budgets(current_user.id)
    categories = Category.get_by_user(current_user.id)
    
    # Calculate spending and percentage for each budget
    for budget in active_budgets:
        budget.spent = budget.get_spending()
        budget.remaining = budget.get_remaining()
        budget.percentage = budget.get_percentage_used()
        
        # Get category name if this is a category budget
        if budget.category_id:
            for category in categories:
                if category.id == budget.category_id:
                    budget.category_name = category.name
                    break
        else:
            budget.category_name = 'All Categories'
    
    return render_template('budget_overview.html', 
                          budgets=active_budgets)

@app.route('/logout')
@login_required
def logout():
    # Get the current session ID
    session_id = session.get('session_id')
    
    # Remove the session from the user's active sessions
    if session_id:
        current_user.remove_session(session_id)
    
    # Log the user out
    logout_user()
    
    # Clear the session
    session.clear()
    
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

# Security Routes
@app.route('/security', methods=['GET'])
@login_required
def security_settings():
    """Security settings page"""
    # Get user's active sessions
    user_data = db.users.find_one({'_id': ObjectId(current_user.id)})
    active_sessions = user_data.get('active_sessions', [])
    
    # Get security logs
    security_logs = current_user.get_security_logs(limit=20)
    
    return render_template('security.html', 
                          active_sessions=active_sessions,
                          security_logs=security_logs,
                          two_factor_enabled=current_user.two_factor_enabled)

@app.route('/security/setup_2fa', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """Setup two-factor authentication"""
    if request.method == 'POST':
        verification_code = request.form.get('verification_code')
        
        # Verify the code
        if current_user.verify_2fa_token(verification_code):
            # Enable 2FA
            current_user.enable_2fa()
            flash('Two-factor authentication has been enabled for your account', 'success')
            return redirect(url_for('security_settings'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
    
    # Generate new 2FA secret if not already set up
    if not current_user.two_factor_secret:
        secret, backup_codes = current_user.setup_2fa()
    else:
        secret = current_user.two_factor_secret
        backup_codes = current_user.two_factor_backup_codes
    
    # Generate QR code
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name="Money Tracker"
    )
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('setup_2fa.html', 
                          secret=secret,
                          qr_code=img_str,
                          backup_codes=backup_codes)

@app.route('/security/disable_2fa', methods=['POST'])
@login_required
def disable_2fa():
    """Disable two-factor authentication"""
    password = request.form.get('password')
    
    # Verify password
    if check_password_hash(current_user.password, password):
        current_user.disable_2fa()
        flash('Two-factor authentication has been disabled', 'success')
    else:
        flash('Incorrect password', 'danger')
    
    return redirect(url_for('security_settings'))

@app.route('/security/sessions/revoke/<session_id>', methods=['POST'])
@login_required
def revoke_session(session_id):
    """Revoke a specific session"""
    # Don't allow revoking the current session
    if session_id == session.get('session_id'):
        flash('You cannot revoke your current session', 'danger')
        return redirect(url_for('security_settings'))
    
    current_user.remove_session(session_id)
    flash('Session has been revoked', 'success')
    return redirect(url_for('security_settings'))

@app.route('/security/sessions/revoke_all', methods=['POST'])
@login_required
def revoke_all_sessions():
    """Revoke all sessions except the current one"""
    current_session_id = session.get('session_id')
    
    # Get all user sessions
    user_data = db.users.find_one({'_id': ObjectId(current_user.id)})
    active_sessions = user_data.get('active_sessions', [])
    
    # Keep only the current session
    db.users.update_one(
        {'_id': ObjectId(current_user.id)},
        {'$set': {'active_sessions': [s for s in active_sessions if s.get('session_id') == current_session_id]}}
    )
    
    flash('All other sessions have been revoked', 'success')
    return redirect(url_for('security_settings'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Verify current password
    if not check_password_hash(current_user.password, current_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('security_settings'))
    
    # Validate new password
    if not is_password_strong(new_password):
        flash('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character', 'danger')
        return redirect(url_for('security_settings'))
    
    # Confirm passwords match
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('security_settings'))
    
    # Update password
    hashed_password = generate_password_hash(new_password)
    current_user.update_password(hashed_password)
    
    flash('Your password has been updated successfully', 'success')
    return redirect(url_for('security_settings'))

@app.route('/reset_password', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def reset_password_request():
    """Request a password reset"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.get_by_email(email)
        
        if user:
            # Generate a reset token
            token = user.generate_password_reset_token()
            
            # Send the password reset email
            email_sent = send_password_reset_email(user, token)
            
            if email_sent:
                flash('A password reset link has been sent to your email address.', 'info')
                return redirect(url_for('login'))
            else:
                # Fallback if email sending fails
                reset_url = url_for('reset_password_token', token=token, _external=True)
                flash(f'Email sending failed. Use this link to reset your password: {reset_url}', 'warning')
                return render_template('reset_password_link.html', reset_url=reset_url)
        else:
            # Don't reveal that the user doesn't exist
            flash('If your email is registered, you will receive a password reset link', 'info')
    
    return render_template('reset_password_request.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
@limiter.limit("10 per hour")
def reset_password_token(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    user = User.get_by_reset_token(token)
    
    if not user:
        flash('Invalid or expired reset link', 'danger')
        return redirect(url_for('reset_password_request'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not is_password_strong(password):
            flash('Password must be at least 8 characters long and include uppercase, lowercase, number, and special character', 'danger')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('reset_password.html', token=token)
        
        # Update the password
        hashed_password = generate_password_hash(password)
        user.update_password(hashed_password)
        
        flash('Your password has been reset. You can now log in with your new password.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

# Recurring Transactions Routes
@app.route('/recurring_transactions')
@login_required
def recurring_transactions():
    """View all recurring transactions"""
    recurring_expenses = Expense.get_recurring_transactions(current_user.id)
    recurring_salaries = Salary.get_recurring_salaries(current_user.id)
    
    # Get categories for expense display
    categories = Category.get_by_user(current_user.id)
    category_dict = {str(c.id): c.name for c in categories}
    
    # Add category names to expenses
    for expense in recurring_expenses:
        expense.category_name = category_dict.get(expense.category_id, 'Unknown')
    
    return render_template('recurring_transactions.html',
                          recurring_expenses=recurring_expenses,
                          recurring_salaries=recurring_salaries)

@app.route('/edit_recurring_expense/<id>', methods=['GET', 'POST'])
@login_required
def edit_recurring_expense(id):
    """Edit a recurring expense"""
    # Get the expense
    expense = db.expenses.find_one({'_id': ObjectId(id), 'user_id': current_user.id})
    if not expense or not expense.get('is_recurring', False):
        flash('Recurring expense not found', 'danger')
        return redirect(url_for('recurring_transactions'))
    
    expense_obj = Expense(expense)
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            category_id = request.form['category']
            description = request.form['description']
            recurrence_type = request.form['recurrence_type']
            
            # Get recurrence day for monthly transactions
            recurrence_day = None
            if recurrence_type == 'monthly' and 'recurrence_day' in request.form:
                recurrence_day = int(request.form['recurrence_day'])
            
            # Get end date if specified
            recurrence_end_date = None
            if 'recurrence_end_date' in request.form and request.form['recurrence_end_date']:
                recurrence_end_date = datetime.strptime(request.form['recurrence_end_date'], '%Y-%m-%d')
            
            # Update the recurring expense
            Expense.update_recurring(
                expense_id=id,
                user_id=current_user.id,
                amount=amount,
                category_id=category_id,
                description=description,
                recurrence_type=recurrence_type,
                recurrence_day=recurrence_day,
                recurrence_end_date=recurrence_end_date
            )
            
            flash('Recurring expense updated successfully!', 'success')
            return redirect(url_for('recurring_transactions'))
        except Exception as e:
            flash(f'Error updating recurring expense: {str(e)}', 'danger')
    
    # Get categories for the form
    categories = Category.get_by_user(current_user.id)
    
    # Format dates for the form
    if expense_obj.recurrence_end_date:
        end_date = expense_obj.recurrence_end_date.strftime('%Y-%m-%d')
    else:
        end_date = ''
    
    return render_template('edit_recurring_expense.html',
                          expense=expense_obj,
                          categories=categories,
                          end_date=end_date)

@app.route('/edit_recurring_salary/<id>', methods=['GET', 'POST'])
@login_required
def edit_recurring_salary(id):
    """Edit a recurring salary"""
    # Get the salary
    salary = db.salaries.find_one({'_id': ObjectId(id), 'user_id': current_user.id})
    if not salary or not salary.get('is_recurring', False):
        flash('Recurring salary not found', 'danger')
        return redirect(url_for('recurring_transactions'))
    
    salary_obj = Salary(salary)
    
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            description = request.form['description']
            recurrence_type = request.form['recurrence_type']
            
            # Get recurrence day for monthly transactions
            recurrence_day = None
            if recurrence_type == 'monthly' and 'recurrence_day' in request.form:
                recurrence_day = int(request.form['recurrence_day'])
            
            # Get end date if specified
            recurrence_end_date = None
            if 'recurrence_end_date' in request.form and request.form['recurrence_end_date']:
                recurrence_end_date = datetime.strptime(request.form['recurrence_end_date'], '%Y-%m-%d')
            
            # Update the recurring salary
            Salary.update_recurring(
                salary_id=id,
                user_id=current_user.id,
                amount=amount,
                description=description,
                recurrence_type=recurrence_type,
                recurrence_day=recurrence_day,
                recurrence_end_date=recurrence_end_date
            )
            
            flash('Recurring salary updated successfully!', 'success')
            return redirect(url_for('recurring_transactions'))
        except Exception as e:
            flash(f'Error updating recurring salary: {str(e)}', 'danger')
    
    # Format dates for the form
    if salary_obj.recurrence_end_date:
        end_date = salary_obj.recurrence_end_date.strftime('%Y-%m-%d')
    else:
        end_date = ''
    
    return render_template('edit_recurring_salary.html',
                          salary=salary_obj,
                          end_date=end_date)

# Process recurring transactions on each request
@app.before_request
def process_recurring_transactions():
    if current_user.is_authenticated:
        # Only process once per day per user
        today = datetime.now().strftime('%Y-%m-%d')
        last_processed = session.get('last_processed_recurring')
        
        if last_processed != today:
            try:
                # Process recurring transactions
                Expense.process_recurring_transactions()
                Salary.process_recurring_salaries()
                
                # Update session
                session['last_processed_recurring'] = today
            except Exception as e:
                print(f"Error processing recurring transactions: {str(e)}")

# Enhanced Analytics and Reporting Routes
@app.route('/reports')
@login_required
def reports_dashboard():
    """Main reports dashboard with links to different report types"""
    return render_template('reports/dashboard.html')

@app.route('/reports/spending_analysis')
@login_required
def spending_analysis():
    """Detailed spending analysis by category and time period"""
    # Get filter parameters
    year = request.args.get('year', datetime.now().year)
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
        
    period_type = request.args.get('period_type', 'monthly')  # monthly, quarterly, yearly
    
    # Get all years with data for the filter dropdown
    all_years = Expense.get_available_years(current_user.id)
    
    # Get spending data based on period type
    if period_type == 'monthly':
        spending_data = Expense.get_monthly_spending_by_category(current_user.id, year)
        period_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    elif period_type == 'quarterly':
        spending_data = Expense.get_quarterly_spending_by_category(current_user.id, year)
        period_labels = ['Q1', 'Q2', 'Q3', 'Q4']
    else:  # yearly
        spending_data = Expense.get_yearly_spending_by_category(current_user.id)
        period_labels = [str(y) for y in all_years]
    
    # Get category details for better display
    categories = Category.get_by_user(current_user.id)
    category_dict = {str(c.id): c for c in categories}
    
    # Create a mapping of category names to avoid duplicates
    category_name_to_id = {}
    for c in categories:
        # If we haven't seen this category name before, or if this is a user-specific category
        # (which should take precedence over global categories)
        if c.name not in category_name_to_id or c.user_id == current_user.id:
            category_name_to_id[c.name] = c.id
    
    # Prepare data for charts
    chart_data = {
        'labels': period_labels,
        'datasets': []
    }
    
    # Assign colors to categories
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', 
        '#FF9F40', '#8AC249', '#EA5F89', '#00D8B6', '#FFB7B2'
    ]
    
    # Aggregate spending data by category name to avoid duplicates
    aggregated_spending = {}
    for category_id, values in spending_data.items():
        if category_id in category_dict:
            category_name = category_dict[category_id].name
            if category_name not in aggregated_spending:
                aggregated_spending[category_name] = values.copy()
            else:
                # Add values to existing category
                for i in range(len(values)):
                    aggregated_spending[category_name][i] += values[i]
    
    # Create datasets for each category
    color_index = 0
    for category_name, values in aggregated_spending.items():
        chart_data['datasets'].append({
            'label': category_name,
            'data': values,
            'backgroundColor': colors[color_index % len(colors)],
            'borderColor': colors[color_index % len(colors)],
            'borderWidth': 1,
            'fill': False
        })
        color_index += 1
    
    # Calculate total spending per period
    total_spending = [0] * len(period_labels)
    for dataset in chart_data['datasets']:
        for i, value in enumerate(dataset['data']):
            total_spending[i] += value
    
    return render_template('reports/spending_analysis.html', 
                          chart_data=chart_data,
                          total_spending=total_spending,
                          period_labels=period_labels,
                          all_years=all_years,
                          selected_year=year,
                          period_type=period_type)

@app.route('/reports/income_expense')
@login_required
def income_expense_report():
    """Income vs Expense analysis over time"""
    # Get filter parameters
    year = request.args.get('year', datetime.now().year)
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
        
    period_type = request.args.get('period_type', 'monthly')  # monthly, quarterly, yearly
    
    # Get all years with data for the filter dropdown
    expense_years = Expense.get_available_years(current_user.id)
    salary_years = Salary.get_available_years(current_user.id)
    all_years = sorted(list(set(expense_years + salary_years)))
    
    # Get income and expense data based on period type
    if period_type == 'monthly':
        income_data = Salary.get_monthly_income(current_user.id, year)
        expense_data = Expense.get_monthly_spending(current_user.id, year)
        period_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    elif period_type == 'quarterly':
        income_data = Salary.get_quarterly_income(current_user.id, year)
        expense_data = Expense.get_quarterly_spending(current_user.id, year)
        period_labels = ['Q1', 'Q2', 'Q3', 'Q4']
    else:  # yearly
        income_data = Salary.get_yearly_income(current_user.id)
        expense_data = Expense.get_yearly_spending(current_user.id)
        period_labels = [str(y) for y in all_years]
    
    # Calculate savings (income - expense)
    savings_data = [income - expense for income, expense in zip(income_data, expense_data)]
    
    # Calculate savings rate (savings / income) when income > 0
    savings_rate = []
    for income, saving in zip(income_data, savings_data):
        if income > 0:
            savings_rate.append(round((saving / income) * 100, 1))
        else:
            savings_rate.append(0)
    
    # Prepare chart data
    chart_data = {
        'labels': period_labels,
        'datasets': [
            {
                'label': 'Income',
                'data': income_data,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1,
                'fill': True
            },
            {
                'label': 'Expenses',
                'data': expense_data,
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
                'fill': True
            },
            {
                'label': 'Savings',
                'data': savings_data,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1,
                'fill': True
            }
        ]
    }
    
    return render_template('reports/income_expense.html',
                          chart_data=chart_data,
                          income_data=income_data,
                          expense_data=expense_data,
                          savings_data=savings_data,
                          savings_rate=savings_rate,
                          period_labels=period_labels,
                          all_years=all_years,
                          selected_year=year,
                          period_type=period_type)

@app.route('/reports/spending_trends')
@login_required
def spending_trends():
    """Analyze spending trends over time"""
    # Get filter parameters
    months = request.args.get('months', '12')
    try:
        months = int(months)
    except ValueError:
        months = 12
    
    category_id = request.args.get('category', 'all')
    
    # Get categories for filter dropdown
    categories = Category.get_by_user(current_user.id)
    
    # Get spending trend data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)
    
    if category_id == 'all':
        trend_data = Expense.get_spending_trend(current_user.id, start_date, end_date)
    else:
        trend_data = Expense.get_spending_trend_by_category(current_user.id, category_id, start_date, end_date)
    
    # Prepare data for trend chart
    dates = []
    amounts = []
    
    for date, amount in trend_data:
        dates.append(date.strftime('%Y-%m'))
        amounts.append(amount)
    
    # Calculate trend statistics
    avg_spending = sum(amounts) / len(amounts) if amounts else 0
    
    # Calculate month-over-month change
    mom_changes = []
    for i in range(1, len(amounts)):
        if amounts[i-1] > 0:
            change = ((amounts[i] - amounts[i-1]) / amounts[i-1]) * 100
            mom_changes.append(change)
    
    avg_mom_change = sum(mom_changes) / len(mom_changes) if mom_changes else 0
    
    # Prepare chart data
    chart_label = 'Spending Trend'
    if category_id != 'all':
        # Find the category name
        for category in categories:
            if str(category.id) == category_id:
                chart_label = f'{category.name} Spending'
                break
    
    chart_data = {
        'labels': dates,
        'datasets': [
            {
                'label': chart_label,
                'data': amounts,
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 2,
                'fill': True,
                'tension': 0.4  # Smooth curve
            }
        ]
    }
    
    return render_template('reports/spending_trends.html',
                          chart_data=chart_data,
                          categories=categories,
                          selected_category=category_id,
                          months=months,
                          avg_spending=avg_spending,
                          avg_mom_change=avg_mom_change)

@app.route('/reports/budget_analysis')
@login_required
def budget_analysis():
    """Analyze budget performance over time"""
    # Get filter parameters
    year = request.args.get('year', datetime.now().year)
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
        
    month = request.args.get('month', datetime.now().month)
    try:
        month = int(month)
    except ValueError:
        month = datetime.now().month
    
    # Get all years with data for the filter dropdown
    all_years = Budget.get_available_years(current_user.id)
    
    # Get budget performance data
    budget_performance = Budget.get_budget_performance(current_user.id, year, month)
    
    # Prepare data for charts
    categories = []
    budgeted = []
    actual = []
    remaining = []
    percentages = []
    
    for item in budget_performance:
        categories.append(item['category_name'])
        budgeted.append(item['budget_amount'])
        actual.append(item['spent_amount'])
        remaining.append(max(0, item['budget_amount'] - item['spent_amount']))
        
        if item['budget_amount'] > 0:
            percentage = min(100, (item['spent_amount'] / item['budget_amount']) * 100)
        else:
            percentage = 0
        percentages.append(percentage)
    
    # Prepare chart data for budget vs actual
    comparison_chart = {
        'labels': categories,
        'datasets': [
            {
                'label': 'Budgeted',
                'data': budgeted,
                'backgroundColor': 'rgba(54, 162, 235, 0.5)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Actual',
                'data': actual,
                'backgroundColor': 'rgba(255, 99, 132, 0.5)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1
            }
        ]
    }
    
    # Prepare chart data for percentage used
    # Generate colors based on percentage values
    background_colors = []
    border_colors = []
    for p in percentages:
        if p > 100:
            background_colors.append('rgba(255, 99, 132, 0.5)')
            border_colors.append('rgba(255, 99, 132, 1)')
        elif p > 75:
            background_colors.append('rgba(255, 159, 64, 0.5)')
            border_colors.append('rgba(255, 159, 64, 1)')
        else:
            background_colors.append('rgba(75, 192, 192, 0.5)')
            border_colors.append('rgba(75, 192, 192, 1)')
    
    percentage_chart = {
        'labels': categories,
        'datasets': [
            {
                'label': 'Percentage Used',
                'data': percentages,
                'backgroundColor': background_colors,
                'borderColor': border_colors,
                'borderWidth': 1
            }
        ]
    }
    
    # Get historical budget performance
    historical_data = Budget.get_historical_budget_performance(current_user.id, year)
    
    # Prepare historical chart data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    historical_chart = {
        'labels': months,
        'datasets': [
            {
                'label': 'Total Budgeted',
                'data': [data['total_budgeted'] for data in historical_data],
                'backgroundColor': 'rgba(54, 162, 235, 0.2)',
                'borderColor': 'rgba(54, 162, 235, 1)',
                'borderWidth': 1,
                'fill': True
            },
            {
                'label': 'Total Spent',
                'data': [data['total_spent'] for data in historical_data],
                'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                'borderColor': 'rgba(255, 99, 132, 1)',
                'borderWidth': 1,
                'fill': True
            }
        ]
    }
    
    return render_template('reports/budget_analysis.html',
                          comparison_chart=comparison_chart,
                          percentage_chart=percentage_chart,
                          historical_chart=historical_chart,
                          budget_performance=budget_performance,
                          all_years=all_years,
                          selected_year=year,
                          selected_month=month,
                          month_name=calendar.month_name[month])

# The reports_dashboard route is already defined above

# The spending_analysis route is already defined above

# The income_expense_report route is already defined above

# Existing Routes
@app.route('/')
@app.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/offline')
def offline():
    """Serve the offline page when the user is offline."""
    return render_template('offline.html')

@app.route('/service-worker.js')
def service_worker():
    """Serve the service worker at the root path for proper scope."""
    return app.send_static_file('js/service-worker.js')

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
    
    # Calculate current month's credits and debits
    current_date = datetime.now()
    current_month = current_date.strftime('%Y-%m')
    current_month_name = current_date.strftime('%B %Y')  # Format: "April 2024"
    
    current_month_debits = sum(
        expense.amount for expense in expenses 
        if expense.date.strftime('%Y-%m') == current_month 
        and expense.transaction_type == 'DR'
    )
    
    current_month_credits = sum(
        expense.amount for expense in expenses 
        if expense.date.strftime('%Y-%m') == current_month 
        and expense.transaction_type == 'CR'
    )
    
    # Calculate days passed in current month
    days_in_month = current_date.day
    
    # Calculate average daily spend
    avg_daily_spend = current_month_debits / days_in_month if days_in_month > 0 else 0

    # Get available years and months for filtering
    date_range = {}
    for expense in expenses:
        if expense.transaction_type == 'DR':  # Only count debits for spending
            year = expense.date.year
            month = expense.date.month
            if year not in date_range:
                date_range[year] = set()
            date_range[year].add(month)
    
    # Sort years and months
    available_years = sorted(date_range.keys(), reverse=True)
    available_months = {year: sorted(months) for year, months in date_range.items()}
    
    # Get filter parameters
    filter_year = request.args.get('year', 'all')
    filter_month = request.args.get('month', 'all')
    
    # Calculate category-wise spending with optional filtering
    category_spending = {}
    for expense in expenses:
        if expense.transaction_type == 'DR':  # Only count debits for spending
            # Apply filters if set
            if filter_year != 'all' and str(expense.date.year) != filter_year:
                continue
            if filter_month != 'all' and filter_year != 'all' and expense.date.month != int(filter_month):
                continue
                
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
    
    # Get month name for display
    month_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
    filter_month_name = month_names[int(filter_month) - 1] if filter_month != 'all' and filter_month.isdigit() else 'All'
    
    # Get active budgets for the current period
    active_budgets = Budget.get_active_budgets(current_user.id)
    
    # Calculate spending and percentage for each budget
    for budget in active_budgets:
        budget.spent = budget.get_spending()
        budget.remaining = budget.get_remaining()
        budget.percentage = budget.get_percentage_used()
        
        # Get category name if this is a category budget
        if budget.category_id:
            for category in categories:
                if category.id == budget.category_id:
                    budget.category_name = category.name
                    break
        else:
            budget.category_name = 'All Categories'
    
    # Sort budgets by percentage used (descending)
    active_budgets.sort(key=lambda x: x.percentage, reverse=True)
    
    # Limit to top 3 budgets for the dashboard
    top_budgets = active_budgets[:3]
    
    return render_template('index.html', 
                         expenses=expenses, 
                         total_credit=total_credit,
                         total_debit=total_debit,
                         current_month_credits=current_month_credits,
                         current_month_debits=current_month_debits,
                         avg_daily_spend=avg_daily_spend,
                         current_month_name=current_month_name,
                         spending_categories=spending_categories,
                         spending_amounts=spending_amounts,
                         recent_transactions=recent_transactions,
                         categories=categories,
                         available_years=available_years,
                         available_months=available_months,
                         filter_year=filter_year,
                         filter_month=filter_month,
                         filter_month_name=filter_month_name,
                         active_budgets=active_budgets,
                         top_budgets=top_budgets)

@app.route('/add_expense', methods=['GET', 'POST'])
@login_required
def add_expense():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        category_id = request.form['category']  # Now this is the category's _id
        description = request.form['description']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        transaction_type = request.form['transaction_type']
        
        # Check if this is a recurring transaction
        is_recurring = 'is_recurring' in request.form
        
        if is_recurring:
            recurrence_type = request.form.get('recurrence_type')
            
            # Get recurrence day for monthly transactions
            recurrence_day = None
            if recurrence_type == 'monthly' and 'recurrence_day' in request.form:
                recurrence_day = int(request.form.get('recurrence_day'))
            
            # Get end date if specified
            recurrence_end_date = None
            if 'recurrence_end_date' in request.form and request.form.get('recurrence_end_date'):
                recurrence_end_date = datetime.strptime(request.form.get('recurrence_end_date'), '%Y-%m-%d')
            
            # Create recurring transaction
            Expense.create(
                amount=amount, 
                category_id=category_id, 
                description=description, 
                date=date, 
                transaction_type=transaction_type, 
                user_id=current_user.id,
                is_recurring=True,
                recurrence_type=recurrence_type,
                recurrence_day=recurrence_day,
                recurrence_end_date=recurrence_end_date
            )
            flash('Recurring expense added successfully!', 'success')
        else:
            # Create regular transaction
            Expense.create(
                amount=amount, 
                category_id=category_id, 
                description=description, 
                date=date, 
                transaction_type=transaction_type, 
                user_id=current_user.id
            )
            flash('Expense added successfully!', 'success')
            
        return redirect(url_for('index'))
    
    # Get both global and user-specific categories
    categories = Category.get_by_user(current_user.id)
    # Deduplicate by name, prefer user-specific over global
    unique_categories = {}
    for c in categories:
        if c.name not in unique_categories or not c.is_global:
            unique_categories[c.name] = c
    categories = list(unique_categories.values())
    
    # Set default date to today
    default_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('add_expense.html', categories=categories, default_date=default_date)

@app.route('/add_salary', methods=['GET', 'POST'])
@login_required
def add_salary():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        description = request.form.get('description', 'Salary')
        
        # Check if this is a recurring salary
        is_recurring = 'is_recurring' in request.form
        
        if is_recurring:
            recurrence_type = request.form.get('recurrence_type')
            
            # Get recurrence day for monthly transactions
            recurrence_day = None
            if recurrence_type == 'monthly' and 'recurrence_day' in request.form:
                recurrence_day = int(request.form.get('recurrence_day'))
            
            # Get end date if specified
            recurrence_end_date = None
            if 'recurrence_end_date' in request.form and request.form.get('recurrence_end_date'):
                recurrence_end_date = datetime.strptime(request.form.get('recurrence_end_date'), '%Y-%m-%d')
            
            # Create recurring salary
            Salary.create(
                amount=amount, 
                date=date, 
                user_id=current_user.id,
                description=description,
                is_recurring=True,
                recurrence_type=recurrence_type,
                recurrence_day=recurrence_day,
                recurrence_end_date=recurrence_end_date
            )
            flash('Recurring salary added successfully!', 'success')
        else:
            # Create regular salary
            Salary.create(
                amount=amount, 
                date=date, 
                user_id=current_user.id,
                description=description
            )
            flash('Salary added successfully!', 'success')
            
        return redirect(url_for('index'))
    
    # Set default date to today
    default_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('add_salary.html', default_date=default_date)

@app.route('/delete_expense/<id>')
@login_required
def delete_expense(id):
    # Check if this is a recurring transaction
    expense = db.expenses.find_one({'_id': ObjectId(id), 'user_id': current_user.id})
    if expense and expense.get('is_recurring', False):
        # Ask if user wants to delete just this one or the entire series
        return render_template('delete_recurring.html', 
                              transaction_id=id, 
                              transaction_type='expense',
                              description=expense.get('description', 'Expense'))
    
    # Regular delete for non-recurring transactions
    Expense.delete(id, current_user.id)
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_expense_series/<id>')
@login_required
def delete_expense_series(id):
    """Delete a recurring expense and all its future occurrences"""
    Expense.delete_recurring_series(id, current_user.id)
    flash('Recurring expense and all future occurrences deleted successfully!', 'success')
    return redirect(url_for('recurring_transactions'))

@app.route('/delete_salary/<id>')
@login_required
def delete_salary(id):
    # Check if this is a recurring salary
    salary = db.salaries.find_one({'_id': ObjectId(id), 'user_id': current_user.id})
    if salary and salary.get('is_recurring', False):
        # Ask if user wants to delete just this one or the entire series
        return render_template('delete_recurring.html', 
                              transaction_id=id, 
                              transaction_type='salary',
                              description=salary.get('description', 'Salary'))
    
    # Regular delete for non-recurring salaries
    Salary.delete(id, current_user.id)
    flash('Salary deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_salary_series/<id>')
@login_required
def delete_salary_series(id):
    """Delete a recurring salary and all its future occurrences"""
    Salary.delete_recurring_series(id, current_user.id)
    flash('Recurring salary and all future occurrences deleted successfully!', 'success')
    return redirect(url_for('recurring_transactions'))

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

# Import migration functions
from migrate_users import migrate_users_to_add_email, migrate_users_to_add_registration_date

# Run migrations for existing users
def migrate_users():
    """Add missing fields to existing users."""
    try:
        # Add email field to users who don't have it
        migrate_users_to_add_email()
        
        # Add registration date to users who don't have it
        migrate_users_to_add_registration_date()
        
        print("User migrations completed successfully")
    except Exception as e:
        print(f"Error during user migrations: {str(e)}")

if __name__ == '__main__':
    # Run migrations
    migrate_users()
    app.run(debug=True)