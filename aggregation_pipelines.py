"""
Optimized Aggregation Pipelines for Money Tracker

This module provides optimized MongoDB aggregation pipelines for common
reporting and analysis queries.
"""

from datetime import datetime, timedelta
from bson import ObjectId
from database import db
from query_cache import cache_query

# Cache TTL constants (in seconds)
HOUR_TTL = 3600
DAY_TTL = 86400
WEEK_TTL = 604800

@cache_query(ttl=DAY_TTL, prefix="expense:monthly")
def get_monthly_spending_aggregated(user_id, year):
    """
    Get monthly spending using optimized aggregation pipeline.
    
    Args:
        user_id: User ID
        year: Year to get data for
    
    Returns:
        List of monthly spending data
    """
    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31, 23, 59, 59)
    
    pipeline = [
        # Match documents for the specific user and year
        {
            '$match': {
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date},
                'transaction_type': 'expense'
            }
        },
        # Extract month from date and group by month
        {
            '$group': {
                '_id': {'$month': '$date'},
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }
        },
        # Sort by month
        {
            '$sort': {'_id': 1}
        },
        # Reshape output
        {
            '$project': {
                'month': '$_id',
                'total': 1,
                'count': 1,
                '_id': 0
            }
        }
    ]
    
    result = list(db.expenses.aggregate(pipeline))
    
    # Fill in missing months with zero values
    months = {item['month']: item for item in result}
    complete_result = []
    
    for month in range(1, 13):
        if month in months:
            complete_result.append(months[month])
        else:
            complete_result.append({'month': month, 'total': 0, 'count': 0})
    
    return complete_result

@cache_query(ttl=DAY_TTL, prefix="expense:category")
def get_spending_by_category_aggregated(user_id, start_date, end_date):
    """
    Get spending by category using optimized aggregation pipeline.
    
    Args:
        user_id: User ID
        start_date: Start date for the period
        end_date: End date for the period
    
    Returns:
        List of spending by category
    """
    pipeline = [
        # Match documents for the specific user and date range
        {
            '$match': {
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date},
                'transaction_type': 'expense'
            }
        },
        # Group by category
        {
            '$group': {
                '_id': '$category_id',
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }
        },
        # Sort by total amount (descending)
        {
            '$sort': {'total': -1}
        }
    ]
    
    # Execute the aggregation pipeline
    category_spending = list(db.expenses.aggregate(pipeline))
    
    # Get category details in a single query
    if category_spending:
        category_ids = [ObjectId(item['_id']) for item in category_spending if item['_id']]
        categories = {
            str(cat['_id']): cat['name'] 
            for cat in db.categories.find({'_id': {'$in': category_ids}})
        }
        
        # Add category names to results
        for item in category_spending:
            category_id = item['_id']
            if category_id and str(category_id) in categories:
                item['category_name'] = categories[str(category_id)]
            else:
                item['category_name'] = 'Uncategorized'
    
    return category_spending

@cache_query(ttl=WEEK_TTL, prefix="budget:performance")
def get_budget_performance_aggregated(user_id, start_date, end_date):
    """
    Get budget performance using optimized aggregation pipeline.
    
    Args:
        user_id: User ID
        start_date: Start date for the period
        end_date: End date for the period
    
    Returns:
        Dictionary with budget performance data
    """
    # First, get all active budgets for the period
    budget_pipeline = [
        {
            '$match': {
                'user_id': user_id,
                'is_active': True,
                '$or': [
                    {'end_date': {'$gte': start_date}},
                    {'end_date': None}
                ]
            }
        }
    ]
    
    budgets = list(db.budgets.aggregate(budget_pipeline))
    
    # For each budget, calculate spending
    for budget in budgets:
        budget_id = budget['_id']
        category_id = budget.get('category_id')
        
        # Build match criteria for expenses
        match_criteria = {
            'user_id': user_id,
            'date': {'$gte': start_date, '$lte': end_date},
            'transaction_type': 'expense'
        }
        
        # Add category filter if this is a category-specific budget
        if category_id:
            match_criteria['category_id'] = str(category_id)
        
        # Aggregate expenses for this budget
        expense_pipeline = [
            {'$match': match_criteria},
            {'$group': {
                '_id': None,
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }}
        ]
        
        expense_result = list(db.expenses.aggregate(expense_pipeline))
        
        # Add spending data to budget
        if expense_result and expense_result[0]['total']:
            budget['spent'] = expense_result[0]['total']
            budget['transaction_count'] = expense_result[0]['count']
        else:
            budget['spent'] = 0
            budget['transaction_count'] = 0
        
        # Calculate remaining amount and percentage
        budget['remaining'] = budget['amount'] - budget['spent']
        if budget['amount'] > 0:
            budget['percentage_used'] = (budget['spent'] / budget['amount']) * 100
        else:
            budget['percentage_used'] = 0
    
    return budgets

@cache_query(ttl=WEEK_TTL, prefix="income:expense:ratio")
def get_income_expense_ratio(user_id, start_date, end_date):
    """
    Get income to expense ratio using optimized aggregation pipeline.
    
    Args:
        user_id: User ID
        start_date: Start date for the period
        end_date: End date for the period
    
    Returns:
        Dictionary with income and expense totals and ratio
    """
    # Get total expenses
    expense_pipeline = [
        {
            '$match': {
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date},
                'transaction_type': 'expense'
            }
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }
        }
    ]
    
    expense_result = list(db.expenses.aggregate(expense_pipeline))
    total_expenses = expense_result[0]['total'] if expense_result else 0
    
    # Get total income (salaries)
    income_pipeline = [
        {
            '$match': {
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date}
            }
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }
        }
    ]
    
    income_result = list(db.salaries.aggregate(income_pipeline))
    total_income = income_result[0]['total'] if income_result else 0
    
    # Calculate ratio and savings
    ratio = total_income / total_expenses if total_expenses > 0 else float('inf')
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0
    
    return {
        'income': total_income,
        'expenses': total_expenses,
        'ratio': ratio,
        'savings': savings,
        'savings_rate': savings_rate
    }

@cache_query(ttl=DAY_TTL, prefix="expense:daily")
def get_daily_spending_trend(user_id, start_date, end_date):
    """
    Get daily spending trend using optimized aggregation pipeline.
    
    Args:
        user_id: User ID
        start_date: Start date for the period
        end_date: End date for the period
    
    Returns:
        List of daily spending data
    """
    pipeline = [
        # Match documents for the specific user and date range
        {
            '$match': {
                'user_id': user_id,
                'date': {'$gte': start_date, '$lte': end_date},
                'transaction_type': 'expense'
            }
        },
        # Group by date
        {
            '$group': {
                '_id': {
                    'year': {'$year': '$date'},
                    'month': {'$month': '$date'},
                    'day': {'$dayOfMonth': '$date'}
                },
                'total': {'$sum': '$amount'},
                'count': {'$sum': 1}
            }
        },
        # Reshape output and sort by date
        {
            '$project': {
                'date': {
                    '$dateFromParts': {
                        'year': '$_id.year',
                        'month': '$_id.month',
                        'day': '$_id.day'
                    }
                },
                'total': 1,
                'count': 1,
                '_id': 0
            }
        },
        {
            '$sort': {'date': 1}
        }
    ]
    
    result = list(db.expenses.aggregate(pipeline))
    
    # Fill in missing days with zero values
    current_date = start_date
    daily_spending = {}
    
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        daily_spending[date_str] = {'date': date_str, 'total': 0, 'count': 0}
        current_date += timedelta(days=1)
    
    # Update with actual values
    for item in result:
        date_str = item['date'].strftime('%Y-%m-%d')
        if date_str in daily_spending:
            daily_spending[date_str] = {
                'date': date_str,
                'total': item['total'],
                'count': item['count']
            }
    
    return list(daily_spending.values())