from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.money_tracker

def migrate_users_to_add_email():
    """
    Add email field to existing users who don't have it.
    For existing users, we'll set the email to username@example.com as a placeholder.
    """
    users_without_email = db.users.find({'email': {'$exists': False}})
    
    for user in users_without_email:
        username = user.get('username', 'user')
        # Create a placeholder email using the username
        placeholder_email = f"{username}@example.com"
        
        # Update the user document to include the email field
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'email': placeholder_email}}
        )
        print(f"Added placeholder email for user: {username}")

def migrate_users_to_add_registration_date():
    """
    Add registration date to existing users who don't have it.
    For existing users, we'll use the ObjectId creation time as an approximate registration date.
    """
    users_without_reg_date = db.users.find({'registered_on': {'$exists': False}})
    
    for user in users_without_reg_date:
        username = user.get('username', 'unknown')
        
        # Use the ObjectId creation time as an approximate registration date
        # or fall back to current time if that's not possible
        try:
            reg_date = user['_id'].generation_time
        except:
            reg_date = datetime.now()
            
        # Update the user document to include the registration date
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'registered_on': reg_date}}
        )
        print(f"Added registration date for user: {username}")

def run_all_migrations():
    """Run all user migrations"""
    print("Starting user migrations...")
    migrate_users_to_add_email()
    migrate_users_to_add_registration_date()
    print("All migrations completed!")

if __name__ == "__main__":
    run_all_migrations()