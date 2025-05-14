# Import warning suppression module first
import suppress_warnings

import os
import calendar
from datetime import datetime, timedelta
from flask_login import UserMixin
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.money_tracker

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data.get('username', '')
        self.email = user_data.get('email', '')
        self.password = user_data['password']
        self.registered_on = user_data.get('registered_on', None)
        self.last_login = user_data.get('last_login', None)
        self.login_attempts = user_data.get('login_attempts', 0)
        self.account_locked_until = user_data.get('account_locked_until', None)
        self.password_reset_token = user_data.get('password_reset_token', None)
        self.password_reset_expires = user_data.get('password_reset_expires', None)
        self.password_changed_on = user_data.get('password_changed_on', None)
        
        # 2FA fields
        self.two_factor_enabled = user_data.get('two_factor_enabled', False)
        self.two_factor_secret = user_data.get('two_factor_secret', None)
        self.two_factor_backup_codes = user_data.get('two_factor_backup_codes', [])
        
        # Session management fields
        self.active_sessions = user_data.get('active_sessions', [])
        
        # Security log fields
        self.security_logs = user_data.get('security_logs', [])

    @staticmethod
    def get(user_id):
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_username(username):
        user_data = db.users.find_one({'username': username})
        return User(user_data) if user_data else None
        
    @staticmethod
    def get_by_email(email):
        user_data = db.users.find_one({'email': email})
        return User(user_data) if user_data else None
    
    @staticmethod
    def get_by_reset_token(token):
        user_data = db.users.find_one({
            'password_reset_token': token,
            'password_reset_expires': {'$gt': datetime.now()}
        })
        return User(user_data) if user_data else None

    @staticmethod
    def create_default_categories(user_id):
        default_categories = [
            'Food',
            'Transport',
            'Entertainment',
            'Bills',
            'Shopping',
            'Salary',
            'Other'
        ]
        for category_name in default_categories:
            Category.create(category_name, user_id, is_global=True)

    @staticmethod
    def create(username, email, password):
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'registered_on': datetime.now(),
            'password_changed_on': datetime.now(),
            'login_attempts': 0,
            'two_factor_enabled': False,
            'active_sessions': [],
            'security_logs': [{
                'action': 'account_created',
                'timestamp': datetime.now(),
                'ip_address': None,
                'user_agent': None
            }]
        }
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        
        # Create default categories for the new user
        User.create_default_categories(str(user_data['_id']))
        
        return User(user_data)
    
    def update_password(self, new_password):
        """Update user's password and reset related security fields"""
        db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {
                'password': new_password,
                'password_changed_on': datetime.now(),
                'password_reset_token': None,
                'password_reset_expires': None,
                'login_attempts': 0,
                'account_locked_until': None
            },
            '$push': {
                'security_logs': {
                    'action': 'password_changed',
                    'timestamp': datetime.now(),
                    'ip_address': None,
                    'user_agent': None
                }
            }}
        )
    
    def generate_password_reset_token(self):
        """Generate a password reset token valid for 24 hours"""
        import secrets
        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=24)
        
        db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {
                'password_reset_token': token,
                'password_reset_expires': expires
            },
            '$push': {
                'security_logs': {
                    'action': 'password_reset_requested',
                    'timestamp': datetime.now(),
                    'ip_address': None,
                    'user_agent': None
                }
            }}
        )
        return token
    
    def record_login_attempt(self, success, ip_address=None, user_agent=None):
        """Record a login attempt and handle account locking"""
        if success:
            # Successful login
            db.users.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': {
                    'last_login': datetime.now(),
                    'login_attempts': 0,
                    'account_locked_until': None
                },
                '$push': {
                    'security_logs': {
                        'action': 'login_success',
                        'timestamp': datetime.now(),
                        'ip_address': ip_address,
                        'user_agent': user_agent
                    }
                }}
            )
        else:
            # Failed login
            new_attempts = self.login_attempts + 1
            update_data = {
                'login_attempts': new_attempts,
                'security_logs': {
                    'action': 'login_failed',
                    'timestamp': datetime.now(),
                    'ip_address': ip_address,
                    'user_agent': user_agent
                }
            }
            
            # Lock account after 5 failed attempts
            if new_attempts >= 5:
                locked_until = datetime.now() + timedelta(minutes=15)
                update_data['account_locked_until'] = locked_until
                update_data['security_logs']['action'] = 'account_locked'
            
            db.users.update_one(
                {'_id': ObjectId(self.id)},
                {'$set': {k: v for k, v in update_data.items() if k != 'security_logs'},
                 '$push': {'security_logs': update_data['security_logs']}}
            )
    
    def is_account_locked(self):
        """Check if the account is currently locked"""
        if not self.account_locked_until:
            return False
        return datetime.now() < self.account_locked_until
    
    def setup_2fa(self):
        """Generate and store a new 2FA secret"""
        import pyotp
        secret = pyotp.random_base32()
        backup_codes = []
        
        # Generate 10 backup codes
        import secrets
        for _ in range(10):
            backup_codes.append(secrets.token_hex(4).upper())
        
        db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {
                'two_factor_secret': secret,
                'two_factor_backup_codes': backup_codes
            },
            '$push': {
                'security_logs': {
                    'action': '2fa_setup_initiated',
                    'timestamp': datetime.now(),
                    'ip_address': None,
                    'user_agent': None
                }
            }}
        )
        return secret, backup_codes
    
    def enable_2fa(self):
        """Enable 2FA after setup and verification"""
        db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {'two_factor_enabled': True},
            '$push': {
                'security_logs': {
                    'action': '2fa_enabled',
                    'timestamp': datetime.now(),
                    'ip_address': None,
                    'user_agent': None
                }
            }}
        )
    
    def disable_2fa(self):
        """Disable 2FA"""
        db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$set': {
                'two_factor_enabled': False,
                'two_factor_secret': None,
                'two_factor_backup_codes': []
            },
            '$push': {
                'security_logs': {
                    'action': '2fa_disabled',
                    'timestamp': datetime.now(),
                    'ip_address': None,
                    'user_agent': None
                }
            }}
        )
    
    def verify_2fa_token(self, token):
        """Verify a 2FA token or backup code"""
        if not self.two_factor_secret:
            return False
            
        # Check if it's a backup code
        if token in self.two_factor_backup_codes:
            # Remove the used backup code
            db.users.update_one(
                {'_id': ObjectId(self.id)},
                {'$pull': {'two_factor_backup_codes': token},
                '$push': {
                    'security_logs': {
                        'action': '2fa_backup_code_used',
                        'timestamp': datetime.now(),
                        'ip_address': None,
                        'user_agent': None
                    }
                }}
            )
            return True
            
        # Verify TOTP
        import pyotp
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(token)
    
    def add_session(self, session_id, ip_address=None, user_agent=None):
        """Add a new session for the user"""
        session_data = {
            'session_id': session_id,
            'created_at': datetime.now(),
            'last_active': datetime.now(),
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$push': {
                'active_sessions': session_data,
                'security_logs': {
                    'action': 'session_created',
                    'timestamp': datetime.now(),
                    'ip_address': ip_address,
                    'user_agent': user_agent,
                    'session_id': session_id
                }
            }}
        )
    
    def remove_session(self, session_id):
        """Remove a session for the user"""
        db.users.update_one(
            {'_id': ObjectId(self.id)},
            {'$pull': {'active_sessions': {'session_id': session_id}},
            '$push': {
                'security_logs': {
                    'action': 'session_terminated',
                    'timestamp': datetime.now(),
                    'session_id': session_id
                }
            }}
        )
    
    def update_session_activity(self, session_id):
        """Update the last active timestamp for a session"""
        db.users.update_one(
            {'_id': ObjectId(self.id), 'active_sessions.session_id': session_id},
            {'$set': {'active_sessions.$.last_active': datetime.now()}}
        )
    
    def get_security_logs(self, limit=50):
        """Get the user's security logs"""
        user_data = db.users.find_one({'_id': ObjectId(self.id)})
        if not user_data or 'security_logs' not in user_data:
            return []
            
        # Sort logs by timestamp (newest first) and limit
        logs = sorted(
            user_data['security_logs'], 
            key=lambda x: x.get('timestamp', datetime.min), 
            reverse=True
        )
        return logs[:limit]

class Expense:
    def __init__(self, expense_data):
        self.id = str(expense_data['_id'])
        self.amount = expense_data['amount']
        self.category_id = str(expense_data['category_id']) if 'category_id' in expense_data else None
        self.description = expense_data.get('description', '')
        self.date = expense_data['date']
        self.transaction_type = expense_data['transaction_type']
        self.user_id = expense_data['user_id']
        self.timestamp = expense_data.get('timestamp', datetime.now())
        
        # Recurring transaction fields
        self.is_recurring = expense_data.get('is_recurring', False)
        self.recurrence_type = expense_data.get('recurrence_type', None)  # daily, weekly, monthly, yearly
        self.recurrence_day = expense_data.get('recurrence_day', None)  # day of month for monthly, day of week for weekly
        self.recurrence_count = expense_data.get('recurrence_count', 0)  # how many times it has recurred
        self.recurrence_end_date = expense_data.get('recurrence_end_date', None)  # when to stop recurring
        self.parent_id = expense_data.get('parent_id', None)  # for generated recurring transactions
        self.next_date = expense_data.get('next_date', None)  # next occurrence date

    @staticmethod
    def create(amount, category_id, description, date, transaction_type, user_id, 
               is_recurring=False, recurrence_type=None, recurrence_day=None, 
               recurrence_end_date=None, parent_id=None):
        # Convert category_id to ObjectId if needed
        if isinstance(category_id, str):
            category_id = ObjectId(category_id)
            
        expense_data = {
            'amount': amount,
            'category_id': category_id,
            'description': description,
            'date': date,
            'transaction_type': transaction_type,
            'user_id': user_id,
            'timestamp': datetime.now(),
            'is_recurring': is_recurring
        }
        
        # Add recurring fields if this is a recurring transaction
        if is_recurring:
            expense_data['recurrence_type'] = recurrence_type
            expense_data['recurrence_day'] = recurrence_day
            expense_data['recurrence_count'] = 0
            expense_data['recurrence_end_date'] = recurrence_end_date
            
            # Calculate next occurrence date
            next_date = Expense.calculate_next_date(date, recurrence_type, recurrence_day)
            expense_data['next_date'] = next_date
        
        # If this is a generated recurring transaction, add parent_id
        if parent_id:
            expense_data['parent_id'] = parent_id
        
        result = db.expenses.insert_one(expense_data)
        expense_data['_id'] = result.inserted_id
        return Expense(expense_data)

    @staticmethod
    def calculate_next_date(current_date, recurrence_type, recurrence_day=None):
        """Calculate the next occurrence date based on recurrence type"""
        if recurrence_type == 'daily':
            return current_date + timedelta(days=1)
        elif recurrence_type == 'weekly':
            return current_date + timedelta(weeks=1)
        elif recurrence_type == 'monthly':
            # Move to the same day next month
            next_month = current_date.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)  # First day of next month
            
            # If recurrence_day is specified, use that day
            if recurrence_day:
                try:
                    return next_month.replace(day=recurrence_day)
                except ValueError:
                    # Handle case where the day doesn't exist in the next month (e.g., Feb 30)
                    # Use the last day of the month instead
                    last_day = (next_month.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    return last_day
            else:
                # Try to use the same day as the current date
                try:
                    return next_month.replace(day=current_date.day)
                except ValueError:
                    # Handle case where the day doesn't exist in the next month
                    last_day = (next_month.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    return last_day
        elif recurrence_type == 'yearly':
            # Move to the same day next year
            try:
                return current_date.replace(year=current_date.year + 1)
            except ValueError:
                # Handle Feb 29 in leap years
                if current_date.month == 2 and current_date.day == 29:
                    return current_date.replace(month=3, day=1, year=current_date.year + 1)
                else:
                    raise
        else:
            return None

    @staticmethod
    def get_by_user(user_id):
        expenses = db.expenses.find({'user_id': user_id}).sort('timestamp', -1)
        return [Expense(expense) for expense in expenses]

    @staticmethod
    def get_recurring_transactions(user_id):
        """Get all recurring transactions for a user"""
        expenses = db.expenses.find({
            'user_id': user_id,
            'is_recurring': True,
            'parent_id': {'$exists': False}  # Only get parent transactions, not generated ones
        }).sort('next_date', 1)
        return [Expense(expense) for expense in expenses]
        
    @staticmethod
    def get_available_years(user_id):
        """Get all years for which expenses exist"""
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$project': {'year': {'$year': '$date'}}},
            {'$group': {'_id': '$year'}},
            {'$sort': {'_id': 1}}
        ]
        # Execute the pipeline and convert to a list to ensure we can iterate over it
        result = list(db.expenses.aggregate(pipeline))
        return [doc['_id'] for doc in result]
        
    @staticmethod
    def get_monthly_spending(user_id, year):
        """Get total spending by month for a specific year"""
        # Initialize array with zeros for all months
        monthly_spending = [0] * 12
        
        # Get spending data from database
        pipeline = [
            {'$match': {
                'user_id': user_id,
                'transaction_type': 'DR',
                'date': {
                    '$gte': datetime(int(year), 1, 1),
                    '$lt': datetime(int(year) + 1, 1, 1)
                }
            }},
            {'$project': {
                'month': {'$month': '$date'},
                'amount': 1
            }},
            {'$group': {
                '_id': '$month',
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        # Execute the pipeline and convert to a list to ensure we can iterate over it
        result = list(db.expenses.aggregate(pipeline))
        
        # Fill in the data
        for doc in result:
            month_index = doc['_id'] - 1  # MongoDB months are 1-indexed
            monthly_spending[month_index] = doc['total']
            
        return monthly_spending
        
    @staticmethod
    def get_quarterly_spending(user_id, year):
        """Get total spending by quarter for a specific year"""
        # Initialize array with zeros for all quarters
        quarterly_spending = [0] * 4
        
        # Get monthly spending
        monthly_spending = Expense.get_monthly_spending(user_id, year)
        
        # Aggregate into quarters
        for i in range(4):
            quarterly_spending[i] = sum(monthly_spending[i*3:(i+1)*3])
            
        return quarterly_spending
        
    @staticmethod
    def get_yearly_spending(user_id):
        """Get total spending by year"""
        years = Expense.get_available_years(user_id)
        yearly_spending = []
        
        for year in years:
            pipeline = [
                {'$match': {
                    'user_id': user_id,
                    'transaction_type': 'DR',
                    'date': {
                        '$gte': datetime(int(year), 1, 1),
                        '$lt': datetime(int(year) + 1, 1, 1)
                    }
                }},
                {'$group': {
                    '_id': None,
                    'total': {'$sum': '$amount'}
                }}
            ]
            
            # Execute the pipeline and convert to a list to ensure we can iterate over it
            result = list(db.expenses.aggregate(pipeline))
            if result:
                yearly_spending.append(result[0]['total'])
            else:
                yearly_spending.append(0)
                
        return yearly_spending
        
    @staticmethod
    def get_monthly_spending_by_category(user_id, year):
        """Get monthly spending broken down by category"""
        # Get all categories for this user
        categories = Category.get_by_user(user_id)
        category_ids = [str(c.id) for c in categories]
        
        # Initialize result dictionary
        result = {category_id: [0] * 12 for category_id in category_ids}
        
        # Get spending data from database
        pipeline = [
            {'$match': {
                'user_id': user_id,
                'transaction_type': 'DR',
                'date': {
                    '$gte': datetime(int(year), 1, 1),
                    '$lt': datetime(int(year) + 1, 1, 1)
                }
            }},
            {'$project': {
                'month': {'$month': '$date'},
                'amount': 1,
                'category_id': 1
            }},
            {'$group': {
                '_id': {
                    'month': '$month',
                    'category_id': '$category_id'
                },
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'_id.month': 1}}
        ]
        
        # Execute the pipeline and convert to a list to ensure we can iterate over it
        data = list(db.expenses.aggregate(pipeline))
        
        # Fill in the data
        for doc in data:
            month_index = doc['_id']['month'] - 1  # MongoDB months are 1-indexed
            category_id = str(doc['_id']['category_id'])  # Convert ObjectId to string
            if category_id in result:
                result[category_id][month_index] = doc['total']
                
        return result
        
    @staticmethod
    def get_quarterly_spending_by_category(user_id, year):
        """Get quarterly spending broken down by category"""
        # Get monthly spending by category
        monthly_data = Expense.get_monthly_spending_by_category(user_id, year)
        
        # Initialize result dictionary
        result = {category_id: [0] * 4 for category_id in monthly_data.keys()}
        
        # Aggregate into quarters
        for category_id, monthly_values in monthly_data.items():
            for i in range(4):
                result[category_id][i] = sum(monthly_values[i*3:(i+1)*3])
                
        return result
        
    @staticmethod
    def get_yearly_spending_by_category(user_id):
        """Get yearly spending broken down by category"""
        # Get all categories for this user
        categories = Category.get_by_user(user_id)
        category_ids = [str(c.id) for c in categories]
        
        # Get all years
        years = Expense.get_available_years(user_id)
        
        # Initialize result dictionary
        result = {category_id: [0] * len(years) for category_id in category_ids}
        
        # Get spending data from database
        pipeline = [
            {'$match': {
                'user_id': user_id,
                'transaction_type': 'DR'
            }},
            {'$project': {
                'year': {'$year': '$date'},
                'amount': 1,
                'category_id': 1
            }},
            {'$group': {
                '_id': {
                    'year': '$year',
                    'category_id': '$category_id'
                },
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'_id.year': 1}}
        ]
        
        # Execute the pipeline and convert to a list to ensure we can iterate over it
        data = list(db.expenses.aggregate(pipeline))
        
        # Fill in the data
        for doc in data:
            year = doc['_id']['year']
            category_id = str(doc['_id']['category_id'])  # Convert ObjectId to string
            if category_id in result and year in years:
                year_index = years.index(year)
                result[category_id][year_index] = doc['total']
                
        return result
        
    @staticmethod
    def get_spending_trend(user_id, start_date, end_date):
        """Get spending trend over time"""
        pipeline = [
            {'$match': {
                'user_id': user_id,
                'transaction_type': 'DR',
                'date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }},
            {'$project': {
                'year': {'$year': '$date'},
                'month': {'$month': '$date'},
                'amount': 1
            }},
            {'$group': {
                '_id': {
                    'year': '$year',
                    'month': '$month'
                },
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'_id.year': 1, '_id.month': 1}}
        ]
        
        # Execute the pipeline and convert to a list to ensure we can iterate over it
        data = list(db.expenses.aggregate(pipeline))
        
        # Convert to list of (date, amount) tuples
        result = []
        for doc in data:
            year = doc['_id']['year']
            month = doc['_id']['month']
            date = datetime(year, month, 1)
            result.append((date, doc['total']))
            
        return result
        
    @staticmethod
    def get_spending_trend_by_category(user_id, category_id, start_date, end_date):
        """Get spending trend for a specific category over time"""
        pipeline = [
            {'$match': {
                'user_id': user_id,
                'category_id': ObjectId(category_id),  # Convert string ID to ObjectId
                'transaction_type': 'DR',
                'date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }},
            {'$project': {
                'year': {'$year': '$date'},
                'month': {'$month': '$date'},
                'amount': 1
            }},
            {'$group': {
                '_id': {
                    'year': '$year',
                    'month': '$month'
                },
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'_id.year': 1, '_id.month': 1}}
        ]
        
        # Execute the pipeline and convert to a list to ensure we can iterate over it
        data = list(db.expenses.aggregate(pipeline))
        
        # Convert to list of (date, amount) tuples
        result = []
        for doc in data:
            year = doc['_id']['year']
            month = doc['_id']['month']
            date = datetime(year, month, 1)
            result.append((date, doc['total']))
            
        return result

    @staticmethod
    def process_recurring_transactions():
        """Process all recurring transactions that are due"""
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find all recurring transactions that are due
        due_transactions = db.expenses.find({
            'is_recurring': True,
            'next_date': {'$lte': current_date},
            'parent_id': {'$exists': False}  # Only process parent transactions
        })
        
        for transaction in due_transactions:
            # Create a new transaction based on the recurring one
            expense = Expense(transaction)
            
            # Skip if we've reached the end date
            if expense.recurrence_end_date and expense.next_date > expense.recurrence_end_date:
                continue
                
            # Create the new transaction
            new_transaction = Expense.create(
                amount=expense.amount,
                category_id=expense.category_id,
                description=f"{expense.description} (Recurring)",
                date=expense.next_date,
                transaction_type=expense.transaction_type,
                user_id=expense.user_id,
                parent_id=expense.id
            )
            
            # Calculate the next occurrence date
            next_date = Expense.calculate_next_date(
                expense.next_date, 
                expense.recurrence_type,
                expense.recurrence_day
            )
            
            # Update the recurring transaction with the new next_date and increment count
            db.expenses.update_one(
                {'_id': ObjectId(expense.id)},
                {
                    '$set': {'next_date': next_date},
                    '$inc': {'recurrence_count': 1}
                }
            )

    @staticmethod
    def delete(expense_id, user_id):
        db.expenses.delete_one({'_id': ObjectId(expense_id), 'user_id': user_id})

    @staticmethod
    def delete_recurring_series(expense_id, user_id):
        """Delete a recurring transaction and all its future occurrences"""
        # First, delete the parent transaction
        db.expenses.delete_one({'_id': ObjectId(expense_id), 'user_id': user_id})
        
        # Then delete all child transactions that haven't occurred yet
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        db.expenses.delete_many({
            'parent_id': expense_id,
            'user_id': user_id,
            'date': {'$gte': current_date}
        })

    @staticmethod
    def update_category(expense_id, new_category_id, user_id):
        # Convert new_category_id to ObjectId if needed
        if isinstance(new_category_id, str):
            new_category_id = ObjectId(new_category_id)
        db.expenses.update_one(
            {'_id': ObjectId(expense_id), 'user_id': user_id},
            {'$set': {'category_id': new_category_id}}
        )

    @staticmethod
    def update_recurring(expense_id, user_id, amount=None, category_id=None, description=None,
                        recurrence_type=None, recurrence_day=None, recurrence_end_date=None):
        """Update a recurring transaction and recalculate its next occurrence"""
        # Build update dictionary
        update_data = {}
        if amount is not None:
            update_data['amount'] = amount
        if category_id is not None:
            if isinstance(category_id, str):
                category_id = ObjectId(category_id)
            update_data['category_id'] = category_id
        if description is not None:
            update_data['description'] = description
        if recurrence_type is not None:
            update_data['recurrence_type'] = recurrence_type
        if recurrence_day is not None:
            update_data['recurrence_day'] = recurrence_day
        if recurrence_end_date is not None:
            update_data['recurrence_end_date'] = recurrence_end_date
            
        # Get the current transaction to calculate next date
        transaction = db.expenses.find_one({'_id': ObjectId(expense_id), 'user_id': user_id})
        if transaction:
            expense = Expense(transaction)
            
            # Use new values or existing ones
            current_date = expense.next_date or expense.date
            r_type = recurrence_type or expense.recurrence_type
            r_day = recurrence_day or expense.recurrence_day
            
            # Calculate next date based on current date and recurrence settings
            next_date = Expense.calculate_next_date(current_date, r_type, r_day)
            update_data['next_date'] = next_date
            
            # Update the transaction
            db.expenses.update_one(
                {'_id': ObjectId(expense_id), 'user_id': user_id},
                {'$set': update_data}
            )

    @staticmethod
    def add_timestamp_to_existing():
        # Update all existing expenses that don't have a timestamp
        db.expenses.update_many(
            {'timestamp': {'$exists': False}},
            {'$set': {'timestamp': datetime.now()}}
        )
        
    @staticmethod
    def fix_invalid_categories(user_id):
        """Fix expenses with invalid category IDs by setting them to a default category"""
        # Get all valid category IDs for the user
        categories = Category.get_by_user(user_id)
        valid_category_ids = [ObjectId(c.id) for c in categories]
        
        # Find a default category (preferably 'Other' or the first available)
        default_category = None
        for category in categories:
            if category.name == 'Other':
                default_category = category
                break
        
        # If 'Other' category doesn't exist, use the first category or create 'Other'
        if not default_category and categories:
            default_category = categories[0]
        elif not default_category:
            # Create 'Other' category if no categories exist
            default_category = Category.create('Other', user_id, is_global=True)
        
        # Update expenses with invalid category IDs
        db.expenses.update_many(
            {
                'user_id': user_id,
                '$or': [
                    {'category_id': {'$nin': valid_category_ids}},
                    {'category_id': {'$exists': False}}
                ]
            },
            {'$set': {'category_id': ObjectId(default_category.id)}}
        )

class Salary:
    def __init__(self, salary_data):
        self.id = str(salary_data['_id'])
        self.amount = salary_data['amount']
        self.date = salary_data['date']
        self.user_id = salary_data['user_id']
        self.description = salary_data.get('description', 'Salary')
        self.timestamp = salary_data.get('timestamp', datetime.now())
        
        # Recurring salary fields
        self.is_recurring = salary_data.get('is_recurring', False)
        self.recurrence_type = salary_data.get('recurrence_type', None)  # monthly, bi-weekly, weekly
        self.recurrence_day = salary_data.get('recurrence_day', None)  # day of month for monthly
        self.recurrence_count = salary_data.get('recurrence_count', 0)  # how many times it has recurred
        self.recurrence_end_date = salary_data.get('recurrence_end_date', None)  # when to stop recurring
        self.parent_id = salary_data.get('parent_id', None)  # for generated recurring salaries
        self.next_date = salary_data.get('next_date', None)  # next occurrence date

    @staticmethod
    def create(amount, date, user_id, description='Salary', is_recurring=False, 
               recurrence_type=None, recurrence_day=None, recurrence_end_date=None, parent_id=None):
        salary_data = {
            'amount': amount,
            'date': date,
            'user_id': user_id,
            'description': description,
            'timestamp': datetime.now(),
            'is_recurring': is_recurring
        }
        
        # Add recurring fields if this is a recurring salary
        if is_recurring:
            salary_data['recurrence_type'] = recurrence_type
            salary_data['recurrence_day'] = recurrence_day
            salary_data['recurrence_count'] = 0
            salary_data['recurrence_end_date'] = recurrence_end_date
            
            # Calculate next occurrence date
            next_date = Salary.calculate_next_date(date, recurrence_type, recurrence_day)
            salary_data['next_date'] = next_date
        
        # If this is a generated recurring salary, add parent_id
        if parent_id:
            salary_data['parent_id'] = parent_id
        
        result = db.salaries.insert_one(salary_data)
        salary_data['_id'] = result.inserted_id
        return Salary(salary_data)

    @staticmethod
    def calculate_next_date(current_date, recurrence_type, recurrence_day=None):
        """Calculate the next occurrence date based on recurrence type"""
        if recurrence_type == 'weekly':
            return current_date + timedelta(weeks=1)
        elif recurrence_type == 'bi-weekly':
            return current_date + timedelta(weeks=2)
        elif recurrence_type == 'monthly':
            # Move to the same day next month
            next_month = current_date.replace(day=1) + timedelta(days=32)
            next_month = next_month.replace(day=1)  # First day of next month
            
            # If recurrence_day is specified, use that day
            if recurrence_day:
                try:
                    return next_month.replace(day=recurrence_day)
                except ValueError:
                    # Handle case where the day doesn't exist in the next month (e.g., Feb 30)
                    # Use the last day of the month instead
                    last_day = (next_month.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    return last_day
            else:
                # Try to use the same day as the current date
                try:
                    return next_month.replace(day=current_date.day)
                except ValueError:
                    # Handle case where the day doesn't exist in the next month
                    last_day = (next_month.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    return last_day
        else:
            return None

    @staticmethod
    def get_by_user(user_id):
        salaries = db.salaries.find({'user_id': user_id}).sort('date', -1)
        return [Salary(salary) for salary in salaries]

    @staticmethod
    def get_recurring_salaries(user_id):
        """Get all recurring salaries for a user"""
        salaries = db.salaries.find({
            'user_id': user_id,
            'is_recurring': True,
            'parent_id': {'$exists': False}  # Only get parent salaries, not generated ones
        }).sort('next_date', 1)
        return [Salary(salary) for salary in salaries]
        
    @staticmethod
    def get_available_years(user_id):
        """Get all years for which salaries exist"""
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$project': {'year': {'$year': '$date'}}},
            {'$group': {'_id': '$year'}},
            {'$sort': {'_id': 1}}
        ]
        # Execute the pipeline and convert to a list to ensure we can iterate over it
        result = list(db.salaries.aggregate(pipeline))
        return [doc['_id'] for doc in result]
        
    @staticmethod
    def get_monthly_income(user_id, year):
        """Get total income by month for a specific year"""
        # Initialize array with zeros for all months
        monthly_income = [0] * 12
        
        # Get income data from database
        pipeline = [
            {'$match': {
                'user_id': user_id,
                'date': {
                    '$gte': datetime(int(year), 1, 1),
                    '$lt': datetime(int(year) + 1, 1, 1)
                }
            }},
            {'$project': {
                'month': {'$month': '$date'},
                'amount': 1
            }},
            {'$group': {
                '_id': '$month',
                'total': {'$sum': '$amount'}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        # Execute the pipeline and convert to a list to ensure we can iterate over it
        result = list(db.salaries.aggregate(pipeline))
        
        # Fill in the data
        for doc in result:
            month_index = doc['_id'] - 1  # MongoDB months are 1-indexed
            monthly_income[month_index] = doc['total']
            
        return monthly_income
        
    @staticmethod
    def get_quarterly_income(user_id, year):
        """Get total income by quarter for a specific year"""
        # Initialize array with zeros for all quarters
        quarterly_income = [0] * 4
        
        # Get monthly income
        monthly_income = Salary.get_monthly_income(user_id, year)
        
        # Aggregate into quarters
        for i in range(4):
            quarterly_income[i] = sum(monthly_income[i*3:(i+1)*3])
            
        return quarterly_income
        
    @staticmethod
    def get_yearly_income(user_id):
        """Get total income by year"""
        years = Salary.get_available_years(user_id)
        yearly_income = []
        
        for year in years:
            pipeline = [
                {'$match': {
                    'user_id': user_id,
                    'date': {
                        '$gte': datetime(int(year), 1, 1),
                        '$lt': datetime(int(year) + 1, 1, 1)
                    }
                }},
                {'$group': {
                    '_id': None,
                    'total': {'$sum': '$amount'}
                }}
            ]
            
            result = list(db.salaries.aggregate(pipeline))
            if result:
                yearly_income.append(result[0]['total'])
            else:
                yearly_income.append(0)
                
        return yearly_income

    @staticmethod
    def process_recurring_salaries():
        """Process all recurring salaries that are due"""
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find all recurring salaries that are due
        due_salaries = db.salaries.find({
            'is_recurring': True,
            'next_date': {'$lte': current_date},
            'parent_id': {'$exists': False}  # Only process parent salaries
        })
        
        for salary in due_salaries:
            # Create a new salary based on the recurring one
            salary_obj = Salary(salary)
            
            # Skip if we've reached the end date
            if salary_obj.recurrence_end_date and salary_obj.next_date > salary_obj.recurrence_end_date:
                continue
                
            # Create the new salary
            new_salary = Salary.create(
                amount=salary_obj.amount,
                date=salary_obj.next_date,
                user_id=salary_obj.user_id,
                description=f"{salary_obj.description} (Recurring)",
                parent_id=salary_obj.id
            )
            
            # Calculate the next occurrence date
            next_date = Salary.calculate_next_date(
                salary_obj.next_date, 
                salary_obj.recurrence_type,
                salary_obj.recurrence_day
            )
            
            # Update the recurring salary with the new next_date and increment count
            db.salaries.update_one(
                {'_id': ObjectId(salary_obj.id)},
                {
                    '$set': {'next_date': next_date},
                    '$inc': {'recurrence_count': 1}
                }
            )

    @staticmethod
    def delete(salary_id, user_id):
        db.salaries.delete_one({'_id': ObjectId(salary_id), 'user_id': user_id})

    @staticmethod
    def delete_recurring_series(salary_id, user_id):
        """Delete a recurring salary and all its future occurrences"""
        # First, delete the parent salary
        db.salaries.delete_one({'_id': ObjectId(salary_id), 'user_id': user_id})
        
        # Then delete all child salaries that haven't occurred yet
        current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        db.salaries.delete_many({
            'parent_id': salary_id,
            'user_id': user_id,
            'date': {'$gte': current_date}
        })

    @staticmethod
    def update_recurring(salary_id, user_id, amount=None, description=None,
                        recurrence_type=None, recurrence_day=None, recurrence_end_date=None):
        """Update a recurring salary and recalculate its next occurrence"""
        # Build update dictionary
        update_data = {}
        if amount is not None:
            update_data['amount'] = amount
        if description is not None:
            update_data['description'] = description
        if recurrence_type is not None:
            update_data['recurrence_type'] = recurrence_type
        if recurrence_day is not None:
            update_data['recurrence_day'] = recurrence_day
        if recurrence_end_date is not None:
            update_data['recurrence_end_date'] = recurrence_end_date
            
        # Get the current salary to calculate next date
        salary = db.salaries.find_one({'_id': ObjectId(salary_id), 'user_id': user_id})
        if salary:
            salary_obj = Salary(salary)
            
            # Use new values or existing ones
            current_date = salary_obj.next_date or salary_obj.date
            r_type = recurrence_type or salary_obj.recurrence_type
            r_day = recurrence_day or salary_obj.recurrence_day
            
            # Calculate next date based on current date and recurrence settings
            next_date = Salary.calculate_next_date(current_date, r_type, r_day)
            update_data['next_date'] = next_date
            
            # Update the salary
            db.salaries.update_one(
                {'_id': ObjectId(salary_id), 'user_id': user_id},
                {'$set': update_data}
            )

class Category:
    def __init__(self, category_data):
        self.id = str(category_data['_id'])
        self.name = category_data['name']
        self.user_id = category_data.get('user_id')
        self.is_global = category_data.get('is_global', False)

    @staticmethod
    def create(name, user_id, is_global=False):
        category_data = {
            'name': name,
            'is_global': is_global  # Always include is_global flag
        }
        
        # Add user_id for non-global categories
        if not is_global:
            # Convert string user_id to ObjectId if needed
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            category_data['user_id'] = user_id
            
        result = db.categories.insert_one(category_data)
        category_data['_id'] = result.inserted_id
        return Category(category_data)

    @staticmethod
    def get_by_user(user_id):
        # Convert string user_id to ObjectId if needed
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        # Get both user-specific and global categories
        categories = db.categories.find({
            '$or': [
                {'user_id': user_id},
                {'is_global': True}
            ]
        }).sort('name', 1)  # Sort by name for consistent ordering
        
        return [Category(category) for category in categories]

    @staticmethod
    def delete(category_id, user_id):
        db.categories.delete_one({'_id': ObjectId(category_id), 'user_id': user_id, 'is_global': {'$ne': True}})

    @staticmethod
    def update(category_id, name, user_id):
        db.categories.update_one(
            {'_id': ObjectId(category_id), 'user_id': user_id},
            {'$set': {'name': name}}
        )
        
    @staticmethod
    def fix_missing_is_global():
        """Add is_global=False to any categories that don't have the flag"""
        db.categories.update_many(
            {'is_global': {'$exists': False}},
            {'$set': {'is_global': False}}
        )
        
    @staticmethod
    def count_user_categories(user_id):
        """Count only the categories created by this user (not global ones)"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return db.categories.count_documents({'user_id': user_id, 'is_global': {'$ne': True}})


class Budget:
    def __init__(self, budget_data):
        self.id = str(budget_data['_id'])
        self.amount = budget_data['amount']
        self.category_id = str(budget_data['category_id']) if budget_data.get('category_id') else None
        self.name = budget_data.get('name', '')
        self.period = budget_data.get('period', 'monthly')  # monthly, quarterly, yearly
        self.start_date = budget_data.get('start_date')
        self.end_date = budget_data.get('end_date')
        self.user_id = budget_data['user_id']
        self.created_at = budget_data.get('created_at', datetime.now())
        self.updated_at = budget_data.get('updated_at', datetime.now())
        self.is_active = budget_data.get('is_active', True)
        self.notification_threshold = budget_data.get('notification_threshold', 80)  # percentage
        self.color = budget_data.get('color', '#4B6CB7')  # default color

    @staticmethod
    def create(amount, user_id, name='', category_id=None, period='monthly', 
               start_date=None, end_date=None, notification_threshold=80, color='#4B6CB7'):
        """Create a new budget"""
        # Set default dates if not provided
        if not start_date:
            start_date = datetime.now().replace(day=1)  # First day of current month
        if not end_date and period == 'monthly':
            # Last day of current month
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        elif not end_date and period == 'quarterly':
            end_date = start_date + timedelta(days=90)
        elif not end_date:  # yearly
            end_date = start_date.replace(year=start_date.year + 1) - timedelta(days=1)

        # Convert category_id to ObjectId if provided
        if category_id and isinstance(category_id, str):
            category_id = ObjectId(category_id)

        budget_data = {
            'amount': amount,
            'name': name,
            'category_id': category_id,
            'period': period,
            'start_date': start_date,
            'end_date': end_date,
            'user_id': user_id,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'is_active': True,
            'notification_threshold': notification_threshold,
            'color': color
        }
        
        result = db.budgets.insert_one(budget_data)
        budget_data['_id'] = result.inserted_id
        return Budget(budget_data)

    @staticmethod
    def get_by_user(user_id, include_inactive=False):
        """Get all budgets for a user"""
        query = {'user_id': user_id}
        if not include_inactive:
            query['is_active'] = True
            
        budgets = db.budgets.find(query).sort('created_at', -1)
        return [Budget(budget) for budget in budgets]

    @staticmethod
    def get_by_id(budget_id, user_id):
        """Get a specific budget by ID"""
        budget_data = db.budgets.find_one({'_id': ObjectId(budget_id), 'user_id': user_id})
        return Budget(budget_data) if budget_data else None

    @staticmethod
    def get_active_budgets(user_id):
        """Get all active budgets for the current period"""
        current_date = datetime.now()
        budgets = db.budgets.find({
            'user_id': user_id,
            'is_active': True,
            'start_date': {'$lte': current_date},
            'end_date': {'$gte': current_date}
        }).sort('created_at', -1)
        return [Budget(budget) for budget in budgets]

    @staticmethod
    def update(budget_id, user_id, **kwargs):
        """Update a budget with the provided fields"""
        # Ensure only the budget owner can update it
        update_data = {
            'updated_at': datetime.now()
        }
        
        # Add all provided fields to the update
        for key, value in kwargs.items():
            if key == 'category_id' and value and isinstance(value, str):
                update_data[key] = ObjectId(value)
            else:
                update_data[key] = value
                
        db.budgets.update_one(
            {'_id': ObjectId(budget_id), 'user_id': user_id},
            {'$set': update_data}
        )
        
    @staticmethod
    def delete(budget_id, user_id):
        """Delete a budget"""
        db.budgets.delete_one({'_id': ObjectId(budget_id), 'user_id': user_id})
        
    @staticmethod
    def deactivate(budget_id, user_id):
        """Deactivate a budget instead of deleting it"""
        db.budgets.update_one(
            {'_id': ObjectId(budget_id), 'user_id': user_id},
            {'$set': {'is_active': False, 'updated_at': datetime.now()}}
        )
        
    def get_spending(self):
        """Calculate current spending for this budget period"""
        query = {
            'user_id': self.user_id,
            'date': {'$gte': self.start_date, '$lte': self.end_date},
            'transaction_type': 'expense'
        }
        
        # If this is a category-specific budget, filter by category
        if self.category_id:
            query['category_id'] = ObjectId(self.category_id)
            
        # Aggregate total spending
        result = db.expenses.aggregate([
            {'$match': query},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ])
        
        try:
            return next(result)['total']
        except (StopIteration, KeyError):
            return 0
            
    def get_remaining(self):
        """Calculate remaining budget"""
        spent = self.get_spending()
        return max(0, self.amount - spent)
        
    def get_percentage_used(self):
        """Calculate percentage of budget used"""
        if self.amount == 0:
            return 100
        spent = self.get_spending()
        return min(100, round((spent / self.amount) * 100))
        
    def is_over_threshold(self):
        """Check if spending has crossed the notification threshold"""
        percentage_used = self.get_percentage_used()
        return percentage_used >= self.notification_threshold
        
    @staticmethod
    def get_available_years(user_id):
        """Get all years for which budgets exist"""
        pipeline = [
            {'$match': {'user_id': user_id}},
            {'$project': {'year': {'$year': '$start_date'}}},
            {'$group': {'_id': '$year'}},
            {'$sort': {'_id': 1}}
        ]
        result = db.budgets.aggregate(pipeline)
        return [doc['_id'] for doc in result]
        
    @staticmethod
    def get_budget_performance(user_id, year, month):
        """Get budget performance for a specific month"""
        # Get the start and end dates for the month
        start_date = datetime(int(year), int(month), 1)
        if month == 12:
            end_date = datetime(int(year) + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(int(year), int(month) + 1, 1) - timedelta(days=1)
        
        # Get all active budgets for this month
        budgets = db.budgets.find({
            'user_id': user_id,
            'is_active': True,
            'start_date': {'$lte': end_date},
            'end_date': {'$gte': start_date}
        })
        
        # Get all categories
        categories = Category.get_by_user(user_id)
        category_dict = {str(c.id): c.name for c in categories}
        
        # Calculate performance for each budget
        performance = []
        for budget_data in budgets:
            budget = Budget(budget_data)
            
            # Get category name
            category_name = "Overall" if not budget.category_id else category_dict.get(str(budget.category_id), "Unknown")
            
            # Get spending for this budget during the month
            query = {
                'user_id': user_id,
                'transaction_type': 'DR',
                'date': {'$gte': start_date, '$lte': end_date}
            }
            
            # If this is a category-specific budget, filter by category
            if budget.category_id:
                query['category_id'] = str(budget.category_id)
                
            # Aggregate total spending
            result = db.expenses.aggregate([
                {'$match': query},
                {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
            ])
            
            try:
                spent_amount = next(result)['total']
            except (StopIteration, KeyError):
                spent_amount = 0
            
            # Calculate performance metrics
            remaining = max(0, budget.amount - spent_amount)
            percentage = (spent_amount / budget.amount * 100) if budget.amount > 0 else 0
            
            performance.append({
                'budget_id': str(budget.id),
                'budget_name': budget.name,
                'category_id': str(budget.category_id) if budget.category_id else None,
                'category_name': category_name,
                'budget_amount': budget.amount,
                'spent_amount': spent_amount,
                'remaining_amount': remaining,
                'percentage': min(100, percentage),
                'period': budget.period,
                'start_date': budget.start_date,
                'end_date': budget.end_date,
                'color': budget.color
            })
        
        return performance
        
    @staticmethod
    def get_historical_budget_performance(user_id, year):
        """Get historical budget performance for a year"""
        # Initialize result array
        result = []
        
        # Calculate performance for each month
        for month in range(1, 13):
            # Get the start and end dates for the month
            start_date = datetime(int(year), month, 1)
            if month == 12:
                end_date = datetime(int(year) + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(int(year), month + 1, 1) - timedelta(days=1)
            
            # Get all budgets for this month
            budgets = db.budgets.find({
                'user_id': user_id,
                'start_date': {'$lte': end_date},
                'end_date': {'$gte': start_date}
            })
            
            # Calculate total budgeted amount
            total_budgeted = sum(budget['amount'] for budget in budgets)
            
            # Get total spending for the month
            query = {
                'user_id': user_id,
                'transaction_type': 'DR',
                'date': {'$gte': start_date, '$lte': end_date}
            }
            
            # Aggregate total spending
            spending_result = db.expenses.aggregate([
                {'$match': query},
                {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
            ])
            
            try:
                total_spent = next(spending_result)['total']
            except (StopIteration, KeyError):
                total_spent = 0
            
            # Add to result
            result.append({
                'month': month,
                'month_name': calendar.month_name[month],
                'total_budgeted': total_budgeted,
                'total_spent': total_spent,
                'remaining': max(0, total_budgeted - total_spent),
                'percentage': (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0
            })
        
        return result