# Workers Directory

This directory contains Celery workers for asynchronous task processing.

## Starting Celery Worker

```bash
# Start worker with all queues
celery -A app.workers.celery_app worker --loglevel=info

# Start worker for specific queue
celery -A app.workers.celery_app worker -Q code_analysis --loglevel=info

# Start with concurrency
celery -A app.workers.celery_app worker --concurrency=4

# Start with auto-scaling
celery -A app.workers.celery_app worker --autoscale=10,3
```

## Starting Celery Beat (Scheduler)

```bash
celery -A app.workers.celery_app beat --loglevel=info
```

## Monitoring with Flower

```bash
pip install flower
celery -A app.workers.celery_app flower --port=5555
```

## Task Queues

- `code_analysis`: Code analysis tasks
- `ai_processing`: AI review generation
- `security`: Security scanning tasks

## Available Tasks

- `analyze_code`: Analyze code file
- `generate_review`: Generate AI review
- `scan_security`: Run security scan
- `batch_analyze_repository`: Analyze entire repository
- `cleanup_old_results`: Periodic cleanup task
