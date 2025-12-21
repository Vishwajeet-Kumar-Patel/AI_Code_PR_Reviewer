"""
Celery configuration for async task processing
"""
from celery import Celery
from app.core.config import settings
import os


# Configure Celery
celery_app = Celery(
    "code_reviewer",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.workers.tasks.analyze_code": {"queue": "code_analysis"},
        "app.workers.tasks.generate_review": {"queue": "ai_processing"},
        "app.workers.tasks.scan_security": {"queue": "security"},
    },
    
    # Performance settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Rate limits
    task_annotations={
        "app.workers.tasks.generate_review": {"rate_limit": "10/m"},
        "app.workers.tasks.scan_security": {"rate_limit": "20/m"},
    },
    
    # Result expiration
    result_expires=3600,  # 1 hour
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Event monitoring
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True
