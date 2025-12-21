"""
Analytics endpoints for dashboard
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from app.core.deps import get_db, get_current_user
from app.db.models import Review, User, Repository, ReviewFeedback, AuditLog
from datetime import datetime, timedelta
from typing import Optional
import json


router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
async def get_dashboard_stats(
    time_range: Optional[str] = Query("7d", regex="^(24h|7d|30d|90d)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard statistics
    
    Args:
        time_range: Time range for stats (24h, 7d, 30d, 90d)
    """
    # Calculate time range
    time_map = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90)
    }
    start_date = datetime.utcnow() - time_map[time_range]
    
    # Total reviews
    total_reviews = db.query(func.count(Review.id)).filter(
        Review.created_at >= start_date
    ).scalar()
    
    # Average quality score
    avg_score = db.query(func.avg(Review.quality_score)).filter(
        Review.created_at >= start_date
    ).scalar() or 0
    
    # Reviews by status
    reviews_by_status = db.query(
        Review.status,
        func.count(Review.id).label("count")
    ).filter(
        Review.created_at >= start_date
    ).group_by(Review.status).all()
    
    # Top issues
    top_issues = db.query(
        Review.summary,
        func.count(Review.id).label("count")
    ).filter(
        Review.created_at >= start_date,
        Review.summary.isnot(None)
    ).group_by(Review.summary).order_by(desc("count")).limit(10).all()
    
    # Reviews over time
    reviews_over_time = db.query(
        func.date(Review.created_at).label("date"),
        func.count(Review.id).label("count")
    ).filter(
        Review.created_at >= start_date
    ).group_by(func.date(Review.created_at)).all()
    
    return {
        "total_reviews": total_reviews,
        "average_quality_score": round(float(avg_score), 2),
        "reviews_by_status": [
            {"status": status, "count": count}
            for status, count in reviews_by_status
        ],
        "top_issues": [
            {"issue": summary, "count": count}
            for summary, count in top_issues
        ],
        "reviews_over_time": [
            {"date": str(date), "count": count}
            for date, count in reviews_over_time
        ],
        "time_range": time_range
    }


@router.get("/repository/{repository_id}")
async def get_repository_analytics(
    repository_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics for specific repository"""
    
    # Repository stats
    repo = db.query(Repository).filter(Repository.id == repository_id).first()
    if not repo:
        return {"error": "Repository not found"}
    
    total_reviews = db.query(func.count(Review.id)).filter(
        Review.repository_id == repository_id
    ).scalar()
    
    avg_score = db.query(func.avg(Review.quality_score)).filter(
        Review.repository_id == repository_id
    ).scalar() or 0
    
    # Language distribution
    language_dist = db.query(
        Review.findings,
        func.count(Review.id).label("count")
    ).filter(
        Review.repository_id == repository_id
    ).group_by(Review.findings).limit(5).all()
    
    return {
        "repository": {
            "id": repo.id,
            "name": repo.name,
            "full_name": repo.full_name
        },
        "total_reviews": total_reviews,
        "average_score": round(float(avg_score), 2),
        "language_distribution": [
            {"language": lang, "count": count}
            for lang, count in language_dist if lang
        ]
    }


@router.get("/team")
async def get_team_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team performance analytics"""
    
    # User review counts
    user_reviews = db.query(
        User.username,
        func.count(Review.id).label("review_count"),
        func.avg(Review.quality_score).label("avg_score")
    ).join(
        Review, Review.repository_id == User.id  # Simplified - adjust based on your schema
    ).group_by(User.username).limit(10).all()
    
    # Feedback statistics
    feedback_stats = db.query(
        func.avg(ReviewFeedback.rating).label("avg_rating"),
        func.count(ReviewFeedback.id).label("total_feedback")
    ).scalar()
    
    return {
        "team_members": [
            {
                "username": username,
                "review_count": count,
                "average_score": round(float(avg), 2) if avg else 0
            }
            for username, count, avg in user_reviews
        ],
        "overall_feedback": {
            "average_rating": round(float(feedback_stats[0] or 0), 2),
            "total_feedback": feedback_stats[1] or 0
        }
    }


@router.get("/trends")
async def get_trends(
    metric: str = Query("quality_score", regex="^(quality_score|review_count|issue_count)$"),
    time_range: str = Query("30d", regex="^(7d|30d|90d)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trend analysis"""
    
    time_map = {
        "7d": timedelta(days=7),
        "30d": timedelta(days=30),
        "90d": timedelta(days=90)
    }
    start_date = datetime.utcnow() - time_map[time_range]
    
    if metric == "quality_score":
        trends = db.query(
            func.date(Review.created_at).label("date"),
            func.avg(Review.quality_score).label("value")
        ).filter(
            Review.created_at >= start_date
        ).group_by(func.date(Review.created_at)).all()
    
    elif metric == "review_count":
        trends = db.query(
            func.date(Review.created_at).label("date"),
            func.count(Review.id).label("value")
        ).filter(
            Review.created_at >= start_date
        ).group_by(func.date(Review.created_at)).all()
    
    else:  # issue_count
        trends = db.query(
            func.date(Review.created_at).label("date"),
            func.count(Review.id).label("value")
        ).filter(
            Review.created_at >= start_date,
            Review.findings.isnot(None)
        ).group_by(func.date(Review.created_at)).all()
    
    return {
        "metric": metric,
        "time_range": time_range,
        "data": [
            {"date": str(date), "value": float(value or 0)}
            for date, value in trends
        ]
    }


@router.post("/feedback")
async def submit_feedback(
    review_id: str,
    rating: int = Query(..., ge=1, le=5),
    feedback_type: str = Query(..., regex="^(helpful|not_helpful|false_positive)$"),
    comment: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit feedback on a review"""
    
    feedback = ReviewFeedback(
        review_id=review_id,
        user_id=current_user.id,
        rating=rating,
        feedback_type=feedback_type,
        comment=comment,
        created_at=datetime.utcnow()
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": feedback.id
    }


@router.get("/reports/summary")
async def get_summary_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate summary report for date range"""
    
    # Total reviews
    total = db.query(func.count(Review.id)).filter(
        and_(Review.created_at >= start_date, Review.created_at <= end_date)
    ).scalar()
    
    # Quality metrics
    quality = db.query(
        func.avg(Review.quality_score).label("avg"),
        func.min(Review.quality_score).label("min"),
        func.max(Review.quality_score).label("max")
    ).filter(
        and_(Review.created_at >= start_date, Review.created_at <= end_date)
    ).first()
    
    # Critical issues
    critical_issues = db.query(func.count(Review.id)).filter(
        and_(
            Review.created_at >= start_date,
            Review.created_at <= end_date,
            Review.quality_score < 50
        )
    ).scalar()
    
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "total_reviews": total,
        "quality_metrics": {
            "average": round(float(quality.avg or 0), 2),
            "min": round(float(quality.min or 0), 2),
            "max": round(float(quality.max or 0), 2)
        },
        "critical_issues": critical_issues,
        "health_score": round((100 - (critical_issues / max(total, 1)) * 100), 2)
    }
