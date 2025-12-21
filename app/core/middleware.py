"""
Middleware for tracking metrics and logging
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
from app.core.metrics import http_requests_total, http_request_duration_seconds
from app.core.logging import logger


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect metrics for all requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        http_requests_total.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else None
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} ({duration:.3f}s)",
                extra={
                    "status_code": response.status_code,
                    "duration": duration
                }
            )
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)} ({duration:.3f}s)",
                extra={
                    "error": str(e),
                    "duration": duration
                },
                exc_info=True
            )
            raise
