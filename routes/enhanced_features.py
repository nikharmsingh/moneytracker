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
        if categories and expense.category not in categories and 'All Categories' not in categories:
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
            'category': expense.category,
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
    
    # Group by category
    categories = {}
    for expense in dr_expenses:
        if expense.category in categories:
            categories[expense.category] += expense.amount
        else:
            categories[expense.category] = expense.amount
    
    # Sort by amount (descending)
    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    
    # Limit to top 10 categories
    top_categories = sorted_categories[:10]
    
    # Prepare chart data
    labels = [category for category, _ in top_categories]
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
    
    # Group expenses by category
    category_expenses = {}
    for expense in current_month_expenses:
        if expense.category in category_expenses:
            category_expenses[expense.category] += expense.amount
        else:
            category_expenses[expense.category] = expense.amount
    
    # Get budget amounts for each category
    budget_amounts = {}
    for budget in budgets:
        budget_amounts[budget.category] = budget.amount
    
    # Prepare chart data (only for categories with budgets)
    labels = []
    actual_data = []
    budget_data = []
    
    for category, budget_amount in budget_amounts.items():
        labels.append(category)
        actual_data.append(category_expenses.get(category, 0))
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