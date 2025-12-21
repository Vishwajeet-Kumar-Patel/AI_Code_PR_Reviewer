"""
Celery tasks for async code review processing
"""
from app.workers.celery_app import celery_app
from app.services.code_analyzer import CodeAnalyzer
from app.services.ai_service import AIService
from app.services.security_scanner import SecurityScanner
from app.services.secrets_scanner import SecretsScanner
from app.services.websocket_service import send_review_update, send_review_completed
from app.core.logging import logger
from celery import Task
import asyncio


class CallbackTask(Task):
    """Base task with callbacks"""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Success callback"""
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Failure callback"""
        logger.error(f"Task {task_id} failed: {exc}")


@celery_app.task(base=CallbackTask, bind=True, max_retries=3)
def analyze_code(self, code: str, language: str, file_path: str):
    """Analyze code asynchronously"""
    try:
        analyzer = CodeAnalyzer()
        
        # Run async function in event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(
            analyzer.analyze_code(code, language)
        )
        
        return {
            "status": "success",
            "file_path": file_path,
            "result": result
        }
    
    except Exception as e:
        logger.error(f"Code analysis failed: {e}", exc_info=True)
        self.retry(exc=e, countdown=60)


@celery_app.task(base=CallbackTask, bind=True, max_retries=3)
def generate_review(self, review_id: str, code_data: dict):
    """Generate AI review asynchronously"""
    try:
        ai_service = AIService()
        
        # Send progress update
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            send_review_update(
                review_id,
                "generating_review",
                {"progress": 50, "message": "Analyzing code with AI"}
            )
        )
        
        # Generate review
        prompt = f"""Analyze this code and provide a detailed review:
        
Language: {code_data.get('language')}
Files: {len(code_data.get('files', []))}

Code Analysis:
{code_data.get('analysis_summary')}

Provide:
1. Overall quality score
2. Major issues
3. Best practice violations
4. Security concerns
5. Recommendations
"""
        
        loop = asyncio.get_event_loop()
        review_text = loop.run_until_complete(
            ai_service.get_ai_response(prompt)
        )
        
        result = {
            "review_id": review_id,
            "review_text": review_text,
            "quality_score": code_data.get("quality_score", 70),
            "status": "completed"
        }
        
        # Send completion notification
        loop.run_until_complete(
            send_review_completed(review_id, result)
        )
        
        return result
    
    except Exception as e:
        logger.error(f"Review generation failed: {e}", exc_info=True)
        self.retry(exc=e, countdown=60)


@celery_app.task(base=CallbackTask, bind=True)
def scan_security(self, code: str, file_path: str):
    """Run security scan asynchronously"""
    try:
        scanner = SecurityScanner()
        secrets_scanner = SecretsScanner()
        
        # Run security scans
        security_issues = scanner.scan_code(code, file_path)
        secret_findings = secrets_scanner.scan_code(code, file_path)
        
        return {
            "status": "success",
            "file_path": file_path,
            "security_issues": security_issues,
            "secrets_found": len(secret_findings),
            "secret_findings": secret_findings
        }
    
    except Exception as e:
        logger.error(f"Security scan failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@celery_app.task(bind=True)
def batch_analyze_repository(self, repository_data: dict):
    """Analyze entire repository in background"""
    try:
        files = repository_data.get("files", [])
        review_id = repository_data.get("review_id")
        
        # Process files in parallel using Celery chord
        from celery import group, chord
        
        # Create group of analysis tasks
        analysis_tasks = group(
            analyze_code.s(file["content"], file["language"], file["path"])
            for file in files
        )
        
        # Execute with callback
        result = chord(analysis_tasks)(
            aggregate_results.s(review_id)
        )
        
        return {"task_id": result.id, "status": "processing"}
    
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@celery_app.task
def aggregate_results(results: list, review_id: str):
    """Aggregate analysis results"""
    try:
        total_issues = sum(len(r.get("result", {}).get("issues", [])) for r in results)
        
        summary = {
            "review_id": review_id,
            "files_analyzed": len(results),
            "total_issues": total_issues,
            "status": "completed"
        }
        
        # Send final update
        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            send_review_completed(review_id, summary)
        )
        
        return summary
    
    except Exception as e:
        logger.error(f"Result aggregation failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@celery_app.task
def cleanup_old_results():
    """Periodic task to clean up old results"""
    try:
        # Clean up results older than 24 hours
        from app.db.database import SessionLocal
        from app.db.models import Review
        from datetime import datetime, timedelta
        
        db = SessionLocal()
        cutoff_date = datetime.utcnow() - timedelta(days=1)
        
        old_reviews = db.query(Review).filter(
            Review.created_at < cutoff_date,
            Review.status == "completed"
        ).all()
        
        for review in old_reviews:
            # Archive or delete old data
            logger.info(f"Cleaning up old review: {review.id}")
        
        db.close()
        
        return {"cleaned": len(old_reviews)}
    
    except Exception as e:
        logger.error(f"Cleanup failed: {e}", exc_info=True)
        return {"status": "error"}


# Periodic tasks configuration
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "cleanup-old-results": {
        "task": "app.workers.tasks.cleanup_old_results",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}
