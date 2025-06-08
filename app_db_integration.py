"""
Script to update app.py with database optimizations

This script demonstrates how to integrate the database optimizations
into the main application file.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import section to add at the top of app.py
IMPORT_SECTION = """
# Import optimized database modules
from database import db, check_database_connection, close_connection
from query_cache import get_cache_stats, invalidate_expense_cache, invalidate_salary_cache, invalidate_budget_cache, invalidate_category_cache
from aggregation_pipelines import (
    get_monthly_spending_aggregated,
    get_spending_by_category_aggregated,
    get_budget_performance_aggregated,
    get_income_expense_ratio,
    get_daily_spending_trend
)
"""

# Health check function to replace in app.py
HEALTH_CHECK_FUNCTION = """
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    db_status = check_database_connection()
    cache_stats = get_cache_stats()
    
    health_data = {
        'status': 'healthy' if db_status else 'unhealthy',
        'timestamp': datetime.now().isoformat(),
        'database': {
            'connected': db_status
        },
        'cache': cache_stats,
        'version': '1.2.0'  # Update with your app version
    }
    
    status_code = 200 if db_status else 503
    return jsonify(health_data), status_code
"""

# Example of how to update a route to use optimized aggregation
SPENDING_ANALYSIS_FUNCTION = """
@app.route('/reports/spending-analysis')
@login_required
def spending_analysis():
    """Spending analysis report with optimized database queries."""
    # Get query parameters
    year = request.args.get('year', datetime.now().year)
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
    
    # Get available years for the filter
    available_years = Expense.get_available_years(current_user.id)
    
    # Use optimized aggregation pipeline for monthly spending
    monthly_spending = get_monthly_spending_aggregated(current_user.id, year)
    
    # Calculate current month's spending
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    start_of_month = datetime(current_year, current_month, 1)
    end_of_month = (datetime(current_year, current_month + 1, 1) if current_month < 12 
                    else datetime(current_year + 1, 1, 1)) - timedelta(days=1)
    
    # Use optimized aggregation for category spending
    category_spending = get_spending_by_category_aggregated(
        current_user.id, start_of_month, end_of_month
    )
    
    # Format data for charts
    months = ['January', 'February', 'March', 'April', 'May', 'June', 
              'July', 'August', 'September', 'October', 'November', 'December']
    
    spending_data = []
    for item in monthly_spending:
        month_index = item['month'] - 1  # Convert 1-based to 0-based index
        spending_data.append({
            'month': months[month_index],
            'amount': item['total']
        })
    
    # Format category data
    category_data = []
    for item in category_spending:
        category_data.append({
            'category': item.get('category_name', 'Uncategorized'),
            'amount': item['total']
        })
    
    # Get daily spending trend for current month
    daily_spending = get_daily_spending_trend(
        current_user.id, start_of_month, end_of_month
    )
    
    return render_template(
        'reports/spending_analysis.html',
        spending_data=spending_data,
        category_data=category_data,
        daily_spending=daily_spending,
        available_years=available_years,
        selected_year=year
    )
"""

# Instructions for integrating the optimizations
INTEGRATION_INSTRUCTIONS = """
To integrate these database optimizations into your Money Tracker application:

1. Add the import section at the top of app.py after the existing imports
2. Replace the health_check function with the optimized version
3. Update the spending_analysis route to use the optimized aggregation pipelines
4. Add cache invalidation to routes that modify data:
   - After adding/updating/deleting expenses: invalidate_expense_cache(user_id)
   - After adding/updating/deleting salaries: invalidate_salary_cache(user_id)
   - After adding/updating/deleting budgets: invalidate_budget_cache(user_id)
   - After adding/updating/deleting categories: invalidate_category_cache(user_id)

5. Update other reporting routes to use the optimized aggregation pipelines:
   - income_expense_report: use get_income_expense_ratio
   - budget_analysis: use get_budget_performance_aggregated
   - spending_trends: use get_daily_spending_trend

6. Add database connection cleanup to app shutdown:
   @app.teardown_appcontext
   def shutdown_session(exception=None):
       close_connection()

7. Run the db_optimization.py script to create the necessary indexes:
   python db_optimization.py
"""

# Print the integration instructions
logger.info("Database Optimization Integration Guide")
logger.info("======================================")
logger.info("\nImport Section to Add:")
print(IMPORT_SECTION)
logger.info("\nOptimized Health Check Function:")
print(HEALTH_CHECK_FUNCTION)
logger.info("\nExample of Optimized Spending Analysis Route:")
print(SPENDING_ANALYSIS_FUNCTION)
logger.info("\nIntegration Instructions:")
print(INTEGRATION_INSTRUCTIONS)