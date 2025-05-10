from flask_login import UserMixin
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os
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
            'registered_on': datetime.now()
        }
        result = db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        
        # Create default categories for the new user
        User.create_default_categories(str(user_data['_id']))
        
        return User(user_data)

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

    @staticmethod
    def create(amount, category_id, description, date, transaction_type, user_id):
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
            'timestamp': datetime.now()
        }
        result = db.expenses.insert_one(expense_data)
        expense_data['_id'] = result.inserted_id
        return Expense(expense_data)

    @staticmethod
    def get_by_user(user_id):
        expenses = db.expenses.find({'user_id': user_id}).sort('timestamp', -1)
        return [Expense(expense) for expense in expenses]

    @staticmethod
    def delete(expense_id, user_id):
        db.expenses.delete_one({'_id': ObjectId(expense_id), 'user_id': user_id})

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

    @staticmethod
    def create(amount, date, user_id):
        salary_data = {
            'amount': amount,
            'date': date,
            'user_id': user_id
        }
        result = db.salaries.insert_one(salary_data)
        salary_data['_id'] = result.inserted_id
        return Salary(salary_data)

    @staticmethod
    def get_by_user(user_id):
        salaries = db.salaries.find({'user_id': user_id}).sort('date', -1)
        return [Salary(salary) for salary in salaries]

    @staticmethod
    def delete(salary_id, user_id):
        db.salaries.delete_one({'_id': ObjectId(salary_id), 'user_id': user_id})

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