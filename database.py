"""
Database Connection Module for Money Tracker

This module provides optimized MongoDB connection handling with connection pooling,
retry logic, and monitoring capabilities.
"""

import os
import time
import logging
from functools import wraps
from pymongo import MongoClient, monitoring
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI found in environment variables")

# Get database name from environment or use default
DB_NAME = os.getenv('DB_NAME', 'moneytracker')

# Connection pooling settings
MAX_POOL_SIZE = 50  # Maximum number of connections in the pool
MIN_POOL_SIZE = 10  # Minimum number of connections in the pool
MAX_IDLE_TIME_MS = 60000  # Maximum time a connection can remain idle (1 minute)
CONNECT_TIMEOUT_MS = 5000  # Connection timeout in milliseconds

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY_MS = 500

# MongoDB Command Monitoring
class CommandLogger(monitoring.CommandListener):
    def started(self, event):
        logger.debug(f"Command {event.command_name} started on server {event.connection_id}")
    
    def succeeded(self, event):
        logger.debug(f"Command {event.command_name} succeeded in {event.duration_micros / 1000}ms")
    
    def failed(self, event):
        logger.warning(f"Command {event.command_name} failed in {event.duration_micros / 1000}ms")

# Register the command logger (only in development)
if os.getenv('FLASK_ENV') == 'development':
    monitoring.register(CommandLogger())

# Create MongoDB client with optimized settings
client = MongoClient(
    MONGODB_URI,
    maxPoolSize=MAX_POOL_SIZE,
    minPoolSize=MIN_POOL_SIZE,
    maxIdleTimeMS=MAX_IDLE_TIME_MS,
    connectTimeoutMS=CONNECT_TIMEOUT_MS,
    retryWrites=True,
    w='majority'  # Write concern for data durability
)

# Get database instance
db = client[DB_NAME]
logger.info(f"Connected to database: {DB_NAME}")

# Retry decorator for database operations
def with_retry(max_retries=MAX_RETRIES, delay_ms=RETRY_DELAY_MS):
    """Decorator to retry database operations on connection failures."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(f"Failed after {max_retries} retries: {str(e)}")
                        raise
                    logger.warning(f"Connection error, retrying ({retries}/{max_retries}): {str(e)}")
                    time.sleep(delay_ms / 1000)
        return wrapper
    return decorator

# Health check function
@with_retry()
def check_database_connection():
    """Check if the database connection is working."""
    try:
        # The ismaster command is cheap and does not require auth
        client.admin.command('ismaster')
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False

# Get collection with retry capability
def get_collection(collection_name):
    """Get a MongoDB collection with retry capability."""
    @with_retry()
    def find(*args, **kwargs):
        return db[collection_name].find(*args, **kwargs)
    
    @with_retry()
    def find_one(*args, **kwargs):
        return db[collection_name].find_one(*args, **kwargs)
    
    @with_retry()
    def insert_one(*args, **kwargs):
        return db[collection_name].insert_one(*args, **kwargs)
    
    @with_retry()
    def update_one(*args, **kwargs):
        return db[collection_name].update_one(*args, **kwargs)
    
    @with_retry()
    def delete_one(*args, **kwargs):
        return db[collection_name].delete_one(*args, **kwargs)
    
    @with_retry()
    def aggregate(*args, **kwargs):
        return db[collection_name].aggregate(*args, **kwargs)
    
    # Create a wrapper object with retry methods
    collection = db[collection_name]
    collection.find_with_retry = find
    collection.find_one_with_retry = find_one
    collection.insert_one_with_retry = insert_one
    collection.update_one_with_retry = update_one
    collection.delete_one_with_retry = delete_one
    collection.aggregate_with_retry = aggregate
    
    return collection

# Close database connection properly
def close_connection():
    """Close the MongoDB connection properly."""
    if client:
        client.close()
        logger.info("MongoDB connection closed")