from models import User, Salary
from datetime import datetime
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client.money_tracker

def check_and_remove_duplicates():
    # Get the user
    user = User.get_by_username('nik2000')
    if not user:
        print("User not found")
        return

    # Get all salaries for the user
    salaries = db.salaries.find({'user_id': user.id})
    
    # Create a dictionary to track unique month-year combinations
    unique_salaries = {}
    duplicates = []
    
    for salary in salaries:
        month_year = salary['date'].strftime('%B %Y')
        if month_year in unique_salaries:
            duplicates.append(salary['_id'])
        else:
            unique_salaries[month_year] = salary['_id']
    
    # Remove duplicates
    if duplicates:
        print(f"Found {len(duplicates)} duplicate entries")
        db.salaries.delete_many({'_id': {'$in': duplicates}})
        print("Removed duplicate entries")
    else:
        print("No duplicates found")

if __name__ == '__main__':
    check_and_remove_duplicates() 