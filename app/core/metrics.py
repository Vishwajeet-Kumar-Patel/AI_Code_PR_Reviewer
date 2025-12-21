"""
Prometheus metrics for monitoring
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time
from typing import Callable
from app.core.logging import logger


# Application info
app_info = Info('app', 'Application information')
app_info.info({
    'name': 'AI Code Review System',
    'version': '1.0.0'
})

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Review metrics
reviews_total = Counter(
    'code_reviews_total',
    'Total code reviews performed',
    ['status']
)

review_duration_seconds = Histogram(
    'code_review_duration_seconds',
    'Code review duration in seconds'
)

code_quality_score = Histogram(
    'code_quality_score',
    'Code quality scores',
    buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

security_score = Histogram(
    'security_score',
    'Security scores',
    buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

complexity_score = Histogram(
    'complexity_score',
    'Complexity scores',
    buckets=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
)

# AI metrics
ai_requests_total = Counter(
    'ai_requests_total',
    'Total AI API requests',
    ['provider', 'status']
)

ai_request_duration_seconds = Histogram(
    'ai_request_duration_seconds',
    'AI API request duration in seconds',
    ['provider']
)

ai_tokens_used = Counter(
    'ai_tokens_used_total',
    'Total AI tokens used',
    ['provider', 'model']
)

# Database metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections'
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation']
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# GitHub API metrics
github_api_requests_total = Counter(
    'github_api_requests_total',
    'Total GitHub API requests',
    ['status']
)

github_api_rate_limit_remaining = Gauge(
    'github_api_rate_limit_remaining',
    'GitHub API rate limit remaining'
)

# Authentication metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['method', 'status']
)

active_users = Gauge(
    'active_users',
    'Number of active users'
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['type', 'severity']
)


def track_request_metrics(func: Callable) -> Callable:
    """Decorator to track HTTP request metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        status_code = 500
        
        try:
            response = await func(*args, **kwargs)
            status_code = getattr(response, 'status_code', 200)
            return response
        except Exception as e:
            logger.error(f"Request error: {e}")
            raise
        finally:
            duration = time.time() - start_time
            endpoint = func.__name__
            method = kwargs.get('method', 'GET')
            
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
    
    return wrapper


def track_review_metrics(func: Callable) -> Callable:
    """Decorator to track code review metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            
            # Track metrics from result
            if hasattr(result, 'status'):
                reviews_total.labels(status=result.status).inc()
            
            if hasattr(result, 'quality_score') and result.quality_score:
                code_quality_score.observe(result.quality_score)
            
            if hasattr(result, 'security_score') and result.security_score:
                security_score.observe(result.security_score)
            
            if hasattr(result, 'complexity_score') and result.complexity_score:
                complexity_score.observe(result.complexity_score)
            
            return result
        finally:
            duration = time.time() - start_time
            review_duration_seconds.observe(duration)
    
    return wrapper


def track_ai_metrics(provider: str):
    """Decorator to track AI API metrics"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                ai_requests_total.labels(provider=provider, status=status).inc()
                ai_request_duration_seconds.labels(provider=provider).observe(duration)
        
        return wrapper
    return decorator


class MetricsCollector:
    """Centralized metrics collector"""
    
    @staticmethod
    def record_review(status: str, quality: float = None, security: float = None, complexity: float = None):
        """Record review metrics"""
        reviews_total.labels(status=status).inc()
        if quality is not None:
            code_quality_score.observe(quality)
        if security is not None:
            security_score.observe(security)
        if complexity is not None:
            complexity_score.observe(complexity)
    
    @staticmethod
    def record_ai_request(provider: str, status: str, duration: float, tokens: int = None):
        """Record AI request metrics"""
        ai_requests_total.labels(provider=provider, status=status).inc()
        ai_request_duration_seconds.labels(provider=provider).observe(duration)
        if tokens:
            ai_tokens_used.labels(provider=provider, model='default').inc(tokens)
    
    @staticmethod
    def record_cache_hit(cache_type: str):
        """Record cache hit"""
        cache_hits_total.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_cache_miss(cache_type: str):
        """Record cache miss"""
        cache_misses_total.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_github_request(status: str):
        """Record GitHub API request"""
        github_api_requests_total.labels(status=status).inc()
    
    @staticmethod
    def update_github_rate_limit(remaining: int):
        """Update GitHub rate limit"""
        github_api_rate_limit_remaining.set(remaining)
    
    @staticmethod
    def record_auth_attempt(method: str, status: str):
        """Record authentication attempt"""
        auth_attempts_total.labels(method=method, status=status).inc()
    
    @staticmethod
    def record_error(error_type: str, severity: str):
        """Record error"""
        errors_total.labels(type=error_type, severity=severity).inc()


# Export metrics collector instance
metrics = MetricsCollector()
