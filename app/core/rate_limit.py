"""
Rate limiting using Redis and SlowAPI
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from typing import Optional
import redis.asyncio as aioredis
from functools import wraps
import time

from app.core.config import settings
from app.core.logging import logger


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)


# Redis client for advanced rate limiting
class RedisRateLimiter:
    """Custom rate limiter using Redis"""
    
    def __init__(self):
        self.redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
        self.client: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        if not self.client:
            self.client = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Redis rate limiter connected")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            logger.info("Redis rate limiter disconnected")
    
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int
    ) -> tuple[bool, dict]:
        """
        Check if rate limit is exceeded
        
        Args:
            key: Unique identifier for the rate limit
            limit: Maximum number of requests allowed
            window: Time window in seconds
        
        Returns:
            Tuple of (is_allowed, info_dict)
        """
        if not self.client:
            await self.connect()
        
        current_time = int(time.time())
        window_start = current_time - window
        
        # Use Redis sorted set for sliding window
        pipe = self.client.pipeline()
        
        # Remove old entries
        await pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        await pipe.zcard(key)
        
        # Add current request
        await pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiry
        await pipe.expire(key, window)
        
        results = await pipe.execute()
        current_count = results[1]
        
        # Check if limit exceeded
        is_allowed = current_count < limit
        remaining = max(0, limit - current_count - 1)
        
        info = {
            "limit": limit,
            "remaining": remaining,
            "reset": current_time + window
        }
        
        return is_allowed, info


# Global rate limiter instance
redis_limiter = RedisRateLimiter()


def rate_limit(
    limit: int = 60,
    window: int = 60,
    key_prefix: str = "rate_limit"
):
    """
    Rate limiting decorator
    
    Args:
        limit: Maximum requests allowed
        window: Time window in seconds
        key_prefix: Prefix for the rate limit key
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs
            request: Optional[Request] = kwargs.get('request')
            
            if not request:
                # Try to find request in args
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            
            if not request:
                # No request found, skip rate limiting
                return await func(*args, **kwargs)
            
            # Generate rate limit key
            client_ip = request.client.host if request.client else "unknown"
            user_id = getattr(kwargs.get('current_user'), 'id', 'anonymous')
            rate_limit_key = f"{key_prefix}:{user_id}:{client_ip}"
            
            # Check rate limit
            is_allowed, info = await redis_limiter.check_rate_limit(
                rate_limit_key,
                limit,
                window
            )
            
            if not is_allowed:
                logger.warning(
                    f"Rate limit exceeded for {rate_limit_key}",
                    extra={"key": rate_limit_key, "limit": limit}
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": str(info["reset"]),
                        "Retry-After": str(window)
                    }
                )
            
            # Add rate limit headers to response
            response = await func(*args, **kwargs)
            
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(info["reset"])
            
            return response
        
        return wrapper
    return decorator


# Tier-based rate limits
class RateLimitTiers:
    """Rate limit configurations for different user tiers"""
    
    FREE = {
        "requests_per_minute": 10,
        "requests_per_hour": 100,
        "requests_per_day": 1000
    }
    
    PRO = {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "requests_per_day": 10000
    }
    
    ENTERPRISE = {
        "requests_per_minute": 300,
        "requests_per_hour": 10000,
        "requests_per_day": 100000
    }
    
    @staticmethod
    def get_limits_for_tier(tier: str) -> dict:
        """Get rate limits for a user tier"""
        return {
            "free": RateLimitTiers.FREE,
            "pro": RateLimitTiers.PRO,
            "enterprise": RateLimitTiers.ENTERPRISE
        }.get(tier.lower(), RateLimitTiers.FREE)


async def check_tier_rate_limit(user_tier: str, request: Request) -> bool:
    """Check rate limit based on user tier"""
    limits = RateLimitTiers.get_limits_for_tier(user_tier)
    
    client_ip = request.client.host if request.client else "unknown"
    
    # Check per-minute limit
    minute_key = f"tier:{user_tier}:{client_ip}:minute"
    is_allowed, _ = await redis_limiter.check_rate_limit(
        minute_key,
        limits["requests_per_minute"],
        60
    )
    
    if not is_allowed:
        return False
    
    # Check per-hour limit
    hour_key = f"tier:{user_tier}:{client_ip}:hour"
    is_allowed, _ = await redis_limiter.check_rate_limit(
        hour_key,
        limits["requests_per_hour"],
        3600
    )
    
    if not is_allowed:
        return False
    
    # Check per-day limit
    day_key = f"tier:{user_tier}:{client_ip}:day"
    is_allowed, _ = await redis_limiter.check_rate_limit(
        day_key,
        limits["requests_per_day"],
        86400
    )
    
    return is_allowed
