"""
Query Cache Module for Money Tracker

This module provides caching functionality for expensive database queries
to improve application performance.
"""

import time
import logging
import functools
import hashlib
import json
from datetime import datetime, timedelta
from bson import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Custom JSON encoder to handle MongoDB ObjectId and datetime
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# In-memory cache implementation
class QueryCache:
    def __init__(self, max_size=100, default_ttl=300):  # default TTL: 5 minutes
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, func_name, args, kwargs):
        """Generate a unique cache key based on function name and arguments."""
        key_dict = {
            'func': func_name,
            'args': args,
            'kwargs': kwargs
        }
        key_json = json.dumps(key_dict, sort_keys=True, cls=MongoJSONEncoder)
        return hashlib.md5(key_json.encode()).hexdigest()
    
    def get(self, key):
        """Get a value from cache if it exists and is not expired."""
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, expiry = self.cache[key]
        if expiry < time.time():
            # Cache entry has expired
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return value
    
    def set(self, key, value, ttl=None):
        """Set a value in the cache with expiration time."""
        if ttl is None:
            ttl = self.default_ttl
        
        # If cache is full, remove the oldest entry
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
        
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
    
    def invalidate(self, prefix=None):
        """Invalidate cache entries that start with the given prefix."""
        if prefix is None:
            self.cache.clear()
            logger.info("Cache completely cleared")
        else:
            keys_to_delete = [k for k in self.cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del self.cache[key]
            logger.info(f"Invalidated {len(keys_to_delete)} cache entries with prefix '{prefix}'")
    
    def get_stats(self):
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': f"{hit_rate:.2f}%",
            'entries': len(self.cache)
        }

# Create a global cache instance
query_cache = QueryCache()

# Cache decorator for expensive queries
def cache_query(ttl=None, prefix=None):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds for cache entries
        prefix: Cache key prefix for grouped invalidation
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Skip caching for write operations or if explicitly disabled
            skip_cache = kwargs.pop('skip_cache', False)
            if skip_cache:
                return func(*args, **kwargs)
            
            # Generate cache key
            cache_key = query_cache._generate_key(func.__name__, args, kwargs)
            if prefix:
                cache_key = f"{prefix}:{cache_key}"
            
            # Try to get from cache
            cached_result = query_cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            query_cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, stored result")
            return result
        return wrapper
    return decorator

# Function to invalidate cache for specific data types
def invalidate_user_cache(user_id):
    """Invalidate all cache entries for a specific user."""
    query_cache.invalidate(f"user:{user_id}")

def invalidate_expense_cache(user_id=None):
    """Invalidate expense-related cache entries."""
    if user_id:
        query_cache.invalidate(f"expense:user:{user_id}")
    else:
        query_cache.invalidate("expense:")

def invalidate_salary_cache(user_id=None):
    """Invalidate salary-related cache entries."""
    if user_id:
        query_cache.invalidate(f"salary:user:{user_id}")
    else:
        query_cache.invalidate("salary:")

def invalidate_budget_cache(user_id=None):
    """Invalidate budget-related cache entries."""
    if user_id:
        query_cache.invalidate(f"budget:user:{user_id}")
    else:
        query_cache.invalidate("budget:")

def invalidate_category_cache(user_id=None):
    """Invalidate category-related cache entries."""
    if user_id:
        query_cache.invalidate(f"category:user:{user_id}")
    else:
        query_cache.invalidate("category:")

def get_cache_stats():
    """Get current cache statistics."""
    return query_cache.get_stats()