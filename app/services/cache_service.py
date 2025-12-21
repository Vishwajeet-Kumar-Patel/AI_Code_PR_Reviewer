"""
Redis cache service
"""
import json
import redis.asyncio as aioredis
from typing import Optional, Any
from functools import wraps
import hashlib

from app.core.config import settings
from app.core.logging import logger
from app.core.metrics import metrics


class CacheService:
    """Redis cache service for caching API responses and data"""
    
    def __init__(self):
        self.redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/1"
        self.client: Optional[aioredis.Redis] = None
        self.default_ttl = settings.CACHE_TTL
    
    async def connect(self):
        """Connect to Redis"""
        if not self.client:
            self.client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis cache service connected")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Redis cache service disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            await self.connect()
        
        try:
            value = await self.client.get(key)
            if value:
                metrics.record_cache_hit("redis")
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            else:
                metrics.record_cache_miss("redis")
                logger.debug(f"Cache miss: {key}")
                return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache"""
        if not self.client:
            await self.connect()
        
        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value)
            await self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.client:
            await self.connect()
        
        try:
            await self.client.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.client:
            await self.connect()
        
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.client:
            await self.connect()
        
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    @staticmethod
    def generate_cache_key(*args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = f"{args}:{kwargs}"
        return hashlib.md5(key_data.encode()).hexdigest()


# Global cache service instance
cache_service = CacheService()


def cached(
    ttl: Optional[int] = None,
    key_prefix: str = "cache",
    key_builder: Optional[callable] = None
):
    """
    Caching decorator for async functions
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
        key_builder: Custom function to build cache key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key = f"{key_prefix}:{key_builder(*args, **kwargs)}"
            else:
                cache_key = f"{key_prefix}:{func.__name__}:{cache_service.generate_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = await cache_service.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Returning cached result for {func.__name__}")
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            await cache_service.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def cache_key_builder_pr(repository: str, pr_number: int) -> str:
    """Build cache key for PR data"""
    return f"pr:{repository}:{pr_number}"


def cache_key_builder_review(review_id: str) -> str:
    """Build cache key for review data"""
    return f"review:{review_id}"
