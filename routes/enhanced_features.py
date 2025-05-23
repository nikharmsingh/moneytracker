import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Expense, Category, Budget, Salary, db
from bson import ObjectId
import calendar

# Create a Blueprint for enhanced features
enhanced_features = Blueprint('enhanced_features', __name__)

@enhanced_features.route('/reports_dashboard')
@login_required
def reports_dashboard():
    """Enhanced reports dashboard with advanced visualizations"""
    # Get all user expenses
    expenses = Expense.get_by_user(current_user.id)
    
    # Get all user categories
    categories = Category.get_by_user(current_user.id)
    
    # Create a mapping of category IDs to category objects
    category_dict = {str(c.id): c for c in categories}
    
    # Add category_name attribute to each expense for easier display
    for expense in expenses:
        expense.category_name = category_dict.get(expense.category_id, 'Uncategorized')
    
    # Get all user budgets
    budgets = Budget.get_by_user(current_user.id)
    
    # Get all user salaries
    salaries = Salary.get_by_user(current_user.id)
    
    # Calculate min and max amounts for the filter
    amounts = [expense.amount for expense in expenses] if expenses else [0]
    min_amount = min(amounts) if amounts else 0
    max_amount = max(amounts) if amounts else 10000
    
    # Prepare data for expense vs income chart
    expense_chart_data = prepare_expense_income_chart_data(expenses, salaries)
    
    # Prepare data for category distribution chart
    category_chart_data = prepare_category_chart_data(expenses)
    
    # Create a mapping of category IDs to names for better display
    category_dict = {str(c.id): c.name for c in categories}
    
    # Replace category IDs with category names in the chart data
    category_chart_data['labels'] = [category_dict.get(label, 'Uncategorized') for label in category_chart_data['labels']]
    
    # Prepare data for trend analysis chart
    trend_chart_data = prepare_trend_chart_data(expenses, salaries)
    
    # Prepare data for budget performance chart
    budget_chart_data = prepare_budget_chart_data(expenses, budgets)
    
    # Prepare data for savings progress chart
    savings_chart_data = prepare_savings_chart_data(expenses, salaries)
    
    return render_template('reports_dashboard.html',
                          expenses=expenses,
                          categories=categories,
                          min_amount=min_amount,
                          max_amount=max_amount,
                          expense_chart_data=expense_chart_data,
                          category_chart_data=category_chart_data,
                          trend_chart_data=trend_chart_data,
                          budget_chart_data=budget_chart_data,
                          savings_chart_data=savings_chart_data)

@enhanced_features.route('/report_cards')
@login_required
def report_cards():
    """Report cards page showing different financial insights"""
    # Get all user expenses
    expenses = Expense.get_by_user(current_user.id)
    
    # Get all user categories
    categories = Category.get_by_user(current_user.id)
    
    # Get all user budgets
    budgets = Budget.get_by_user(current_user.id)
    
    # Get all user salaries
    salaries = Salary.get_by_user(current_user.id)
    
    # Prepare data for trend analysis chart
    trend_chart_data = prepare_trend_chart_data(expenses, salaries)
    
    # Prepare data for category distribution chart
    category_chart_data = prepare_category_chart_data(expenses)
    
    # Create a mapping of category IDs to names for better display
    category_dict = {str(c.id): c.name for c in categories}
    
    # Replace category IDs with category names in the chart data
    category_chart_data['labels'] = [category_dict.get(label, 'Uncategorized') for label in category_chart_data['labels']]
    
    # Calculate total income and expenses for the current month
    today = datetime.now()
    current_month = today.strftime('%Y-%m')
    
    current_month_expenses = sum(expense.amount for expense in expenses 
                               if expense.date.strftime('%Y-%m') == current_month 
                               and expense.transaction_type == 'DR')
    
    current_month_income = sum(salary.amount for salary in salaries 
                             if salary.date.strftime('%Y-%m') == current_month)
    
    current_month_income += sum(expense.amount for expense in expenses 
                              if expense.date.strftime('%Y-%m') == current_month 
                              and expense.transaction_type == 'CR')
    
    # Calculate savings rate
    savings_rate = ((current_month_income - current_month_expenses) / current_month_income * 100) if current_month_income > 0 else 0
    
    # Calculate budget status
    budget_status = []
    for budget in budgets:
        category_name = category_dict.get(budget.category_id, 'Uncategorized')
        category_expenses = sum(expense.amount for expense in expenses 
                              if expense.category_id == budget.category_id 
                              and expense.date.strftime('%Y-%m') == current_month
                              and expense.transaction_type == 'DR')
        
        percentage = (category_expenses / budget.amount * 100) if budget.amount > 0 else 0
        status = 'success' if percentage <= 75 else 'warning' if percentage <= 100 else 'danger'
        
        budget_status.append({
            'category': category_name,
            'budget': budget.amount,
            'spent': category_expenses,
            'percentage': percentage,
            'status': status
        })
    
    # Sort budget status by percentage (descending)
    budget_status.sort(key=lambda x: x['percentage'], reverse=True)
    
    # Calculate month-over-month changes
    if len(trend_chart_data['expenses']) >= 2:
        expense_change = ((trend_chart_data['expenses'][-1] - trend_chart_data['expenses'][-2]) / 
                         trend_chart_data['expenses'][-2] * 100) if trend_chart_data['expenses'][-2] > 0 else 0
        income_change = ((trend_chart_data['income'][-1] - trend_chart_data['income'][-2]) / 
                        trend_chart_data['income'][-2] * 100) if trend_chart_data['income'][-2] > 0 else 0
    else:
        expense_change = 0
        income_change = 0
    
    return render_template('report_cards.html',
                          expenses=expenses,
                          categories=categories,
                          trend_chart_data=trend_chart_data,
                          category_chart_data=category_chart_data,
                          current_month_expenses=current_month_expenses,
                          current_month_income=current_month_income,
                          savings_rate=savings_rate,
                          budget_status=budget_status,
                          expense_change=expense_change,
                          income_change=income_change)

@enhanced_features.route('/api/filter_expenses', methods=['POST'])
@login_required
def filter_expenses():
    """API endpoint for filtering expenses"""
    # Get filter parameters from request
    data = request.get_json()
    
    # Date range filter
    start_date = datetime.strptime(data.get('start_date', '2000-01-01'), '%Y-%m-%d')
    end_date = datetime.strptime(data.get('end_date', '2100-12-31'), '%Y-%m-%d')
    
    # Category filter
    categories = data.get('categories', [])
    
    # Amount range filter
    min_amount = data.get('min_amount', 0)
    max_amount = data.get('max_amount', float('inf'))
    
    # Transaction type filter
    transaction_type = data.get('transaction_type', 'all')
    
    # Get all expenses
    expenses = Expense.get_by_user(current_user.id)
    
    # Apply filters
    filtered_expenses = []
    for expense in expenses:
        # Date filter
        if not (start_date <= expense.date <= end_date):
            continue
        
        # Category filter
        if categories and expense.category_id not in categories and 'All Categories' not in categories:
            continue
        
        # Amount filter
        if not (min_amount <= expense.amount <= max_amount):
            continue
        
        # Transaction type filter
        if transaction_type != 'all' and expense.transaction_type != transaction_type:
            continue
        
        # Add to filtered list
        filtered_expenses.append(expense)
    
    # Convert to JSON-serializable format
    result = []
    for expense in filtered_expenses:
        result.append({
            'id': str(expense.id),
            'date': expense.date.strftime('%Y-%m-%d'),
            'description': expense.description,
            'amount': expense.amount,
            'category_id': expense.category_id,
            'transaction_type': expense.transaction_type
        })
    
    return jsonify(result)

@enhanced_features.route('/user_preferences', methods=['GET', 'POST'])
@login_required
def user_preferences():
    """User preferences page for customizing the app"""
    if request.method == 'POST':
        # Get preferences from form
        dark_mode = 'dark_mode' in request.form
        
        # Update user preferences in database
        db.users.update_one(
            {'_id': ObjectId(current_user.id)},
            {'$set': {'preferences.dark_mode': dark_mode}}
        )
        
        flash('Preferences updated successfully', 'success')
        return redirect(url_for('enhanced_features.user_preferences'))
    
    # Get current user preferences
    user_data = db.users.find_one({'_id': ObjectId(current_user.id)})
    preferences = user_data.get('preferences', {})
    
    return render_template('user_preferences.html', preferences=preferences)

# Helper functions for chart data preparation
def prepare_expense_income_chart_data(expenses, salaries):
    """Prepare data for expense vs income chart"""
    # Get the last 6 months
    today = datetime.now()
    months = []
    for i in range(5, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=i*30)
        months.append(month_date.strftime('%Y-%m'))
    
    # Initialize data
    expense_data = [0] * 6
    income_data = [0] * 6
    
    # Calculate expenses by month
    for expense in expenses:
        month_str = expense.date.strftime('%Y-%m')
        if month_str in months:
            month_index = months.index(month_str)
            if expense.transaction_type == 'DR':
                expense_data[month_index] += expense.amount
            elif expense.transaction_type == 'CR':
                income_data[month_index] += expense.amount
    
    # Add salary data to income
    for salary in salaries:
        month_str = salary.date.strftime('%Y-%m')
        if month_str in months:
            month_index = months.index(month_str)
            income_data[month_index] += salary.amount
    
    # Format month labels
    labels = []
    for month in months:
        year, month = month.split('-')
        month_name = calendar.month_abbr[int(month)]
        labels.append(f"{month_name} {year}")
    
    return {
        'labels': labels,
        'expenses': expense_data,
        'income': income_data
    }

def prepare_category_chart_data(expenses):
    """Prepare data for category distribution chart"""
    # Only include expenses (DR transactions)
    dr_expenses = [expense for expense in expenses if expense.transaction_type == 'DR']
    
    # Group by category_id
    categories = {}
    for expense in dr_expenses:
        if expense.category_id in categories:
            categories[expense.category_id] += expense.amount
        else:
            categories[expense.category_id] = expense.amount
    
    # Sort by amount (descending)
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    
    # Limit to top 10 categories
    top_categories = sorted_categories[:10]
    
    # Prepare chart data
    labels = [category_id for category_id, _ in top_categories]
    data = [amount for _, amount in top_categories]
    
    return {
        'labels': labels,
        'data': data
    }

def prepare_trend_chart_data(expenses, salaries):
    """Prepare data for trend analysis chart"""
    # Get the last 12 months
    today = datetime.now()
    months = []
    for i in range(11, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=i*30)
        months.append(month_date.strftime('%Y-%m'))
    
    # Initialize data
    expense_data = [0] * 12
    income_data = [0] * 12
    savings_data = [0] * 12
    
    # Calculate expenses and income by month
    for expense in expenses:
        month_str = expense.date.strftime('%Y-%m')
        if month_str in months:
            month_index = months.index(month_str)
            if expense.transaction_type == 'DR':
                expense_data[month_index] += expense.amount
            elif expense.transaction_type == 'CR':
                income_data[month_index] += expense.amount
    
    # Add salary data to income
    for salary in salaries:
        month_str = salary.date.strftime('%Y-%m')
        if month_str in months:
            month_index = months.index(month_str)
            income_data[month_index] += salary.amount
    
    # Calculate savings (income - expenses)
    for i in range(12):
        savings_data[i] = income_data[i] - expense_data[i]
    
    # Format month labels
    labels = []
    for month in months:
        year, month = month.split('-')
        month_name = calendar.month_abbr[int(month)]
        labels.append(f"{month_name} {year}")
    
    return {
        'labels': labels,
        'expenses': expense_data,
        'income': income_data,
        'savings': savings_data
    }

def prepare_budget_chart_data(expenses, budgets):
    """Prepare data for budget performance chart"""
    # Get current month
    today = datetime.now()
    current_month = today.strftime('%Y-%m')
    
    # Filter expenses for current month
    current_month_expenses = [
        expense for expense in expenses 
        if expense.date.strftime('%Y-%m') == current_month and expense.transaction_type == 'DR'
    ]
    
    # Group expenses by category_id
    category_expenses = {}
    for expense in current_month_expenses:
        if expense.category_id in category_expenses:
            category_expenses[expense.category_id] += expense.amount
        else:
            category_expenses[expense.category_id] = expense.amount
    
    # Get budget amounts for each category_id
    budget_amounts = {}
    for budget in budgets:
        budget_amounts[budget.category_id] = budget.amount
    
    # Prepare chart data (only for categories with budgets)
    labels = []
    actual_data = []
    budget_data = []
    
    # Create a mapping of category IDs to names for better display
    category_dict = {str(c.id): c.name for c in Category.get_by_user(current_user.id)}
    
    for category_id, budget_amount in budget_amounts.items():
        # Use category name for display, or "Uncategorized" if not found
        category_name = category_dict.get(category_id, 'Uncategorized')
        labels.append(category_name)
        actual_data.append(category_expenses.get(category_id, 0))
        budget_data.append(budget_amount)
    
    return {
        'labels': labels,
        'actual': actual_data,
        'budget': budget_data
    }

def prepare_savings_chart_data(expenses, salaries):
    """Prepare data for savings progress chart"""
    # Get the last 12 months
    today = datetime.now()
    months = []
    for i in range(11, -1, -1):
        month_date = today.replace(day=1) - timedelta(days=i*30)
        months.append(month_date.strftime('%Y-%m'))
    
    # Initialize data
    monthly_savings = [0] * 12
    
    # Calculate monthly income
    monthly_income = {}
    for salary in salaries:
        month_str = salary.date.strftime('%Y-%m')
        if month_str in months:
            if month_str in monthly_income:
                monthly_income[month_str] += salary.amount
            else:
                monthly_income[month_str] = salary.amount
    
    # Add other income (CR transactions)
    for expense in expenses:
        if expense.transaction_type == 'CR':
            month_str = expense.date.strftime('%Y-%m')
            if month_str in months:
                if month_str in monthly_income:
                    monthly_income[month_str] += expense.amount
                else:
                    monthly_income[month_str] = expense.amount
    
    # Calculate monthly expenses
    monthly_expenses = {}
    for expense in expenses:
        if expense.transaction_type == 'DR':
            month_str = expense.date.strftime('%Y-%m')
            if month_str in months:
                if month_str in monthly_expenses:
                    monthly_expenses[month_str] += expense.amount
                else:
                    monthly_expenses[month_str] = expense.amount
    
    # Calculate monthly savings
    for i, month in enumerate(months):
        income = monthly_income.get(month, 0)
        expense = monthly_expenses.get(month, 0)
        monthly_savings[i] = income - expense
    
    # Format month labels
    labels = []
    for month in months:
        year, month = month.split('-')
        month_name = calendar.month_abbr[int(month)]
        labels.append(f"{month_name} {year}")
    
    return {
        'labels': labels,
        'data': monthly_savings
    }