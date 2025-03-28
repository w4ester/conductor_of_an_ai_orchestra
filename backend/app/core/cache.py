import json
import os
import pickle
from typing import Any, Optional, Dict, List, Union
import redis
from functools import wraps
import time
import hashlib

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # Default TTL: 1 hour
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# Redis client initialization
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=False) if CACHE_ENABLED else None
    # Test connection
    if CACHE_ENABLED:
        redis_client.ping()
except Exception as e:
    print(f"Warning: Redis connection failed: {e}")
    redis_client = None

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from the function arguments
    """
    # Create a string representation of args and kwargs
    key_parts = [prefix]
    
    if args:
        key_parts.append("_".join(str(arg) for arg in args))
    
    if kwargs:
        # Sort kwargs by key for consistent hash generation
        sorted_kwargs = sorted(kwargs.items())
        key_parts.append("_".join(f"{k}={v}" for k, v in sorted_kwargs))
    
    # Join and hash the key parts
    key = "_".join(key_parts)
    if len(key) > 100:  # If key is too long, use a hash
        key = f"{prefix}_{hashlib.md5(key.encode()).hexdigest()}"
    
    return key

async def cache_get(key: str) -> Optional[Any]:
    """
    Get a value from the cache
    """
    if not redis_client:
        return None
    
    try:
        data = redis_client.get(key)
        if data:
            return pickle.loads(data)
        return None
    except Exception as e:
        print(f"Cache get error: {e}")
        return None

async def cache_set(key: str, value: Any, ttl: int = CACHE_TTL) -> bool:
    """
    Set a value in the cache
    """
    if not redis_client:
        return False
    
    try:
        redis_client.setex(key, ttl, pickle.dumps(value))
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False

async def cache_delete(key: str) -> bool:
    """
    Delete a value from the cache
    """
    if not redis_client:
        return False
    
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False

async def cache_delete_pattern(pattern: str) -> bool:
    """
    Delete all keys matching a pattern
    """
    if not redis_client:
        return False
    
    try:
        cursor = 0
        while True:
            cursor, keys = redis_client.scan(cursor, match=pattern, count=100)
            if keys:
                redis_client.delete(*keys)
            if cursor == 0:
                break
        return True
    except Exception as e:
        print(f"Cache delete pattern error: {e}")
        return False

def cached(prefix: str, ttl: int = CACHE_TTL):
    """
    Decorator to cache function results
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not CACHE_ENABLED or not redis_client:
                return await func(*args, **kwargs)
            
            # Generate cache key
            key = get_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = await cache_get(key)
            if cached_value is not None:
                return cached_value
            
            # Call the function and cache the result
            result = await func(*args, **kwargs)
            await cache_set(key, result, ttl)
            return result
        
        return wrapper
    return decorator
