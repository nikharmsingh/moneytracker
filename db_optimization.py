"""
Database Optimization Script for Money Tracker

This script creates indexes for MongoDB collections to improve query performance.
Run this script after setting up the database or when updating the database schema.
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Connect to MongoDB
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI found in environment variables")

# Get database name from environment or use default
DB_NAME = os.getenv('DB_NAME', 'moneytracker')

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

logger.info(f"Connected to database: {DB_NAME}")

def create_indexes():
    """Create indexes for all collections to optimize query performance."""
    
    # Track index creation status
    created_indexes = []
    
    try:
        # Users collection indexes
        logger.info("Creating indexes for users collection...")
        created_indexes.append(("users", "username", db.users.create_index("username", unique=True)))
        created_indexes.append(("users", "email", db.users.create_index("email", unique=True)))
        created_indexes.append(("users", "password_reset_token", db.users.create_index("password_reset_token")))
        
        # Expenses collection indexes
        logger.info("Creating indexes for expenses collection...")
        # Compound index for user_id + timestamp (most common query pattern)
        created_indexes.append(("expenses", "user_id_timestamp", 
                               db.expenses.create_index([("user_id", 1), ("timestamp", -1)])))
        
        # Index for recurring transactions
        created_indexes.append(("expenses", "recurring", 
                               db.expenses.create_index([("is_recurring", 1), ("next_date", 1)])))
        
        # Index for category-based queries
        created_indexes.append(("expenses", "user_category", 
                               db.expenses.create_index([("user_id", 1), ("category_id", 1)])))
        
        # Index for date range queries
        created_indexes.append(("expenses", "user_date", 
                               db.expenses.create_index([("user_id", 1), ("date", 1)])))
        
        # Salaries collection indexes
        logger.info("Creating indexes for salaries collection...")
        # Compound index for user_id + date (most common query pattern)
        created_indexes.append(("salaries", "user_id_date", 
                               db.salaries.create_index([("user_id", 1), ("date", -1)])))
        
        # Index for recurring salaries
        created_indexes.append(("salaries", "recurring", 
                               db.salaries.create_index([("is_recurring", 1), ("next_date", 1)])))
        
        # Categories collection indexes
        logger.info("Creating indexes for categories collection...")
        # Index for user-specific categories
        created_indexes.append(("categories", "user_id", db.categories.create_index("user_id")))
        # Index for global categories
        created_indexes.append(("categories", "is_global", db.categories.create_index("is_global")))
        
        # Budgets collection indexes
        logger.info("Creating indexes for budgets collection...")
        # Compound index for user_id + active status + period
        created_indexes.append(("budgets", "user_active_period", 
                               db.budgets.create_index([("user_id", 1), ("is_active", 1), ("period", 1)])))
        
        # Index for date-based budget queries
        created_indexes.append(("budgets", "user_start_end", 
                               db.budgets.create_index([("user_id", 1), ("start_date", 1), ("end_date", 1)])))
        
        # Index for category-based budget queries
        created_indexes.append(("budgets", "user_category", 
                               db.budgets.create_index([("user_id", 1), ("category_id", 1)])))
        
        logger.info("All indexes created successfully!")
        
        # List all created indexes
        logger.info("Summary of created indexes:")
        for collection, index_name, result in created_indexes:
            logger.info(f"Collection: {collection}, Index: {index_name}")
            
    except Exception as e:
        logger.error(f"Error creating indexes: {str(e)}")
        raise

def list_existing_indexes():
    """List all existing indexes in the database."""
    
    logger.info("Existing indexes in the database:")
    
    collections = db.list_collection_names()
    for collection in collections:
        logger.info(f"\nCollection: {collection}")
        indexes = db[collection].list_indexes()
        for index in indexes:
            logger.info(f"  - {index['name']}: {index['key']}")

if __name__ == "__main__":
    # List existing indexes before creating new ones
    list_existing_indexes()
    
    # Create indexes
    create_indexes()
    
    # List indexes after creation to verify
    logger.info("\nVerifying indexes after creation:")
    list_existing_indexes()