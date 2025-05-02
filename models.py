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
        self.username = user_data['username']
        self.password = user_data['password']

    @staticmethod
    def get(user_id):
        user_data = db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None

    @staticmethod
    def get_by_username(username):
        user_data = db.users.find_one({'username': username})
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
    def create(username, password):
        user_data = {
            'username': username,
            'password': password
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
        self.category = expense_data['category']
        self.description = expense_data.get('description', '')
        self.date = expense_data['date']
        self.transaction_type = expense_data['transaction_type']
        self.user_id = expense_data['user_id']
        self.timestamp = expense_data.get('timestamp', datetime.now())

    @staticmethod
    def create(amount, category, description, date, transaction_type, user_id):
        expense_data = {
            'amount': amount,
            'category': category,
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
    def update_category(expense_id, new_category, user_id):
        db.expenses.update_one(
            {'_id': ObjectId(expense_id), 'user_id': user_id},
            {'$set': {'category': new_category}}
        )

    @staticmethod
    def add_timestamp_to_existing():
        # Update all existing expenses that don't have a timestamp
        db.expenses.update_many(
            {'timestamp': {'$exists': False}},
            {'$set': {'timestamp': datetime.now()}}
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
        self.user_id = category_data['user_id']
        self.is_global = category_data.get('is_global', False)

    @staticmethod
    def create(name, user_id, is_global=False):
        category_data = {
            'name': name,
            'user_id': user_id
        }
        if is_global:
            category_data['is_global'] = True
        result = db.categories.insert_one(category_data)
        category_data['_id'] = result.inserted_id
        return Category(category_data)

    @staticmethod
    def get_by_user(user_id):
        categories = db.categories.find({'user_id': user_id})
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