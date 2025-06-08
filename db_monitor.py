"""
Database Monitoring Script for Money Tracker

This script provides tools to monitor database performance and identify
slow queries or potential issues.
"""

import os
import time
import logging
import argparse
from datetime import datetime, timedelta
from pymongo import MongoClient
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("db_monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# MongoDB connection settings
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError("No MONGODB_URI found in environment variables")

# Get database name from environment or use default
DB_NAME = os.getenv('DB_NAME', 'moneytracker')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

logger.info(f"Connected to database: {DB_NAME}")

def analyze_collection_stats():
    """Analyze collection statistics."""
    logger.info("Analyzing collection statistics...")
    
    collections = db.list_collection_names()
    stats = {}
    
    for collection in collections:
        coll_stats = db.command("collStats", collection)
        stats[collection] = {
            "count": coll_stats.get("count", 0),
            "size": coll_stats.get("size", 0) / (1024 * 1024),  # Convert to MB
            "avg_obj_size": coll_stats.get("avgObjSize", 0) / 1024,  # Convert to KB
            "storage_size": coll_stats.get("storageSize", 0) / (1024 * 1024),  # Convert to MB
            "index_size": coll_stats.get("totalIndexSize", 0) / (1024 * 1024),  # Convert to MB
            "indexes": coll_stats.get("nindexes", 0)
        }
    
    # Print collection statistics
    logger.info("Collection Statistics:")
    logger.info("=====================")
    
    for collection, stat in stats.items():
        logger.info(f"\nCollection: {collection}")
        logger.info(f"  Document Count: {stat['count']:,}")
        logger.info(f"  Data Size: {stat['size']:.2f} MB")
        logger.info(f"  Avg Object Size: {stat['avg_obj_size']:.2f} KB")
        logger.info(f"  Storage Size: {stat['storage_size']:.2f} MB")
        logger.info(f"  Index Size: {stat['index_size']:.2f} MB")
        logger.info(f"  Number of Indexes: {stat['indexes']}")
    
    return stats

def analyze_indexes():
    """Analyze index usage and effectiveness."""
    logger.info("Analyzing index usage...")
    
    collections = db.list_collection_names()
    for collection in collections:
        logger.info(f"\nIndexes for collection: {collection}")
        
        # Get indexes
        indexes = list(db[collection].list_indexes())
        for idx, index in enumerate(indexes):
            logger.info(f"  Index {idx+1}: {index['name']}")
            logger.info(f"    Key: {index['key']}")
            if 'unique' in index:
                logger.info(f"    Unique: {index['unique']}")
    
    logger.info("\nIndex Recommendations:")
    
    # Check for missing indexes on common query patterns
    if 'expenses' in collections:
        # Check if we have an index on user_id + timestamp
        has_user_timestamp_idx = any(
            'user_id_1_timestamp_-1' in idx['name'] 
            for idx in db.expenses.list_indexes()
        )
        if not has_user_timestamp_idx:
            logger.info("  Missing index on expenses: (user_id, timestamp)")
    
    if 'salaries' in collections:
        # Check if we have an index on user_id + date
        has_user_date_idx = any(
            'user_id_1_date_-1' in idx['name'] 
            for idx in db.salaries.list_indexes()
        )
        if not has_user_date_idx:
            logger.info("  Missing index on salaries: (user_id, date)")
    
    if 'budgets' in collections:
        # Check if we have an index on user_id + is_active
        has_user_active_idx = any(
            'user_id_1_is_active_1' in idx['name'] 
            for idx in db.budgets.list_indexes()
        )
        if not has_user_active_idx:
            logger.info("  Missing index on budgets: (user_id, is_active)")

def analyze_query_performance(duration_ms=100):
    """
    Analyze slow queries using the MongoDB profiler.
    
    Args:
        duration_ms: Minimum query duration to consider as slow (in milliseconds)
    """
    logger.info(f"Analyzing slow queries (>{duration_ms}ms)...")
    
    try:
        # Enable profiling for slow queries
        db.command(
            "profile", 2,
            filter={"op": {"$in": ["query", "update", "remove", "insert"]}},
            slowms=duration_ms
        )
        
        logger.info("Profiling enabled. Please run your application for a while to collect data.")
        logger.info("Press Ctrl+C to stop profiling and view results.")
        
        try:
            # Wait for user to generate some traffic
            time.sleep(60)  # Wait for 1 minute by default
        except KeyboardInterrupt:
            logger.info("Profiling stopped by user.")
        
        # Get profiling results
        logger.info("Retrieving profiling results...")
        
        # Query the system.profile collection
        profile_data = list(db.system.profile.find().sort("millis", -1).limit(20))
        
        if not profile_data:
            logger.info("No slow queries found during the profiling period.")
        else:
            logger.info(f"Found {len(profile_data)} slow queries:")
            
            for idx, query in enumerate(profile_data):
                logger.info(f"\nSlow Query {idx+1}:")
                logger.info(f"  Collection: {query.get('ns', '').split('.')[-1]}")
                logger.info(f"  Operation: {query.get('op')}")
                logger.info(f"  Duration: {query.get('millis')}ms")
                logger.info(f"  Query: {query.get('query') or query.get('filter')}")
                if 'command' in query:
                    logger.info(f"  Command: {query.get('command')}")
                logger.info(f"  Timestamp: {query.get('ts')}")
        
        # Disable profiling
        db.command("profile", 0)
        logger.info("Profiling disabled.")
        
    except Exception as e:
        logger.warning(f"Profiling not available: {str(e)}")
        logger.info("Note: MongoDB Atlas does not support the profile command.")
        logger.info("To analyze slow queries, you can:")
        logger.info("1. Use MongoDB Atlas Performance Advisor in the Atlas dashboard")
        logger.info("2. Enable query logging in your application code")
        logger.info("3. Use MongoDB Atlas Data Explorer to analyze query patterns")

def analyze_data_distribution():
    """Analyze data distribution across collections."""
    logger.info("Analyzing data distribution...")
    
    collections = db.list_collection_names()
    
    for collection in collections:
        if collection in ['expenses', 'salaries', 'budgets']:
            # Analyze user distribution
            user_pipeline = [
                {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 10}
            ]
            
            user_distribution = list(db[collection].aggregate(user_pipeline))
            
            if user_distribution:
                logger.info(f"\nTop users by {collection} count:")
                for idx, user in enumerate(user_distribution):
                    logger.info(f"  User {idx+1}: {user['_id']} - {user['count']} documents")
            
            # For expenses, analyze category distribution
            if collection == 'expenses':
                category_pipeline = [
                    {"$group": {"_id": "$category_id", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 10}
                ]
                
                category_distribution = list(db[collection].aggregate(category_pipeline))
                
                if category_distribution:
                    logger.info(f"\nTop categories by expense count:")
                    for idx, category in enumerate(category_distribution):
                        logger.info(f"  Category {idx+1}: {category['_id']} - {category['count']} documents")

def generate_recommendations():
    """Generate database optimization recommendations."""
    logger.info("\nDatabase Optimization Recommendations:")
    logger.info("====================================")
    
    # Collection stats
    stats = analyze_collection_stats()
    
    # Check for large collections
    large_collections = [
        (coll, stat) for coll, stat in stats.items() 
        if stat['count'] > 10000 or stat['size'] > 100
    ]
    
    if large_collections:
        logger.info("\n1. Large Collections:")
        for coll, stat in large_collections:
            logger.info(f"  - {coll}: {stat['count']:,} documents, {stat['size']:.2f} MB")
            
            # Recommendations based on collection size
            if stat['count'] > 100000:
                logger.info("    Recommendation: Consider implementing data archiving for older records")
            
            if stat['avg_obj_size'] > 20:  # If average object size > 20KB
                logger.info("    Recommendation: Check for large embedded documents or arrays")
    
    # Check index size vs data size
    for coll, stat in stats.items():
        if stat['index_size'] > stat['size'] * 0.5 and stat['size'] > 10:
            logger.info(f"\n2. Large Index Overhead:")
            logger.info(f"  - {coll}: Index size ({stat['index_size']:.2f} MB) is more than 50% of data size ({stat['size']:.2f} MB)")
            logger.info("    Recommendation: Review indexes and remove unused ones")
    
    # General recommendations
    logger.info("\n3. General Recommendations:")
    logger.info("  - Run db_optimization.py to create optimal indexes")
    logger.info("  - Implement query caching for expensive operations")
    logger.info("  - Use aggregation pipelines for complex reports")
    logger.info("  - Consider implementing data archiving for historical data")
    logger.info("  - Monitor slow queries regularly")

def main():
    """Main function to run database monitoring."""
    parser = argparse.ArgumentParser(description="MongoDB Database Monitor for Money Tracker")
    parser.add_argument("--stats", action="store_true", help="Analyze collection statistics")
    parser.add_argument("--indexes", action="store_true", help="Analyze index usage")
    parser.add_argument("--queries", action="store_true", help="Analyze slow queries")
    parser.add_argument("--distribution", action="store_true", help="Analyze data distribution")
    parser.add_argument("--recommendations", action="store_true", help="Generate optimization recommendations")
    parser.add_argument("--all", action="store_true", help="Run all analyses")
    parser.add_argument("--slow-ms", type=int, default=100, help="Threshold for slow queries in milliseconds")
    
    args = parser.parse_args()
    
    # If no specific analysis is requested, show help
    if not any([args.stats, args.indexes, args.queries, args.distribution, 
                args.recommendations, args.all]):
        parser.print_help()
        return
    
    logger.info("Money Tracker Database Monitor")
    logger.info("=============================")
    logger.info(f"MongoDB URI: {MONGODB_URI.split('@')[1] if '@' in MONGODB_URI else 'Connected'}")
    logger.info(f"Database: {db.name}")
    logger.info(f"Time: {datetime.now()}")
    logger.info("-----------------------------")
    
    if args.all or args.stats:
        analyze_collection_stats()
    
    if args.all or args.indexes:
        analyze_indexes()
    
    if args.all or args.distribution:
        analyze_data_distribution()
    
    if args.all or args.queries:
        analyze_query_performance(args.slow_ms)
    
    if args.all or args.recommendations:
        generate_recommendations()
    
    logger.info("\nDatabase analysis complete.")

if __name__ == "__main__":
    main()