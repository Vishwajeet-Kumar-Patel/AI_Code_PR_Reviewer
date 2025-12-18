from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
from app.models.review import ReviewRequest, ReviewResponse, ReviewStatus
from app.services.code_analyzer import CodeAnalyzer
from app.core.logging import logger
import asyncio


router = APIRouter(prefix="/review", tags=["Review"])

# In-memory store for reviews (in production, use a database)
reviews_store: Dict[str, ReviewResponse] = {}


def get_code_analyzer() -> CodeAnalyzer:
    """Dependency to get code analyzer instance"""
    return CodeAnalyzer()


@router.post("/analyze", response_model=ReviewResponse)
async def analyze_pr(
    request: ReviewRequest,
    background_tasks: BackgroundTasks,
    analyzer: CodeAnalyzer = Depends(get_code_analyzer),
):
    """
    Analyze a GitHub pull request
    
    This endpoint initiates the analysis of a pull request and returns immediately.
    Use the review_id to check the status and get results.
    """
    try:
        logger.info(f"Received analysis request for {request.repository} PR #{request.pr_number}")
        
        # Start analysis in background
        review = await analyzer.analyze_pull_request(
            repository=request.repository,
            pr_number=request.pr_number,
            include_security=request.include_security_scan,
            include_complexity=request.include_complexity_analysis,
        )
        
        # Store review
        reviews_store[review.review_id] = review
        
        return review
        
    except Exception as e:
        logger.error(f"Failed to analyze PR: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: str):
    """
    Get review results by ID
    
    Returns the complete review analysis including all findings and summary.
    """
    if review_id not in reviews_store:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return reviews_store[review_id]


@router.get("/{review_id}/status")
async def get_review_status(review_id: str) -> Dict[str, Any]:
    """
    Get review status
    
    Check the current status of a review without fetching all details.
    """
    if review_id not in reviews_store:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review = reviews_store[review_id]
    return {
        "review_id": review_id,
        "status": review.status,
        "repository": review.repository,
        "pr_number": review.pr_number,
        "created_at": review.created_at,
        "completed_at": review.completed_at,
    }


@router.get("/{review_id}/summary")
async def get_review_summary(review_id: str):
    """
    Get review summary
    
    Returns only the summary portion of the review.
    """
    if review_id not in reviews_store:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review = reviews_store[review_id]
    
    if review.status != ReviewStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Review is not completed yet. Current status: {review.status}"
        )
    
    return {
        "review_id": review_id,
        "summary": review.summary,
        "ai_insights": review.ai_insights,
    }


@router.delete("/{review_id}")
async def delete_review(review_id: str):
    """
    Delete a review
    
    Remove a review from the store.
    """
    if review_id not in reviews_store:
        raise HTTPException(status_code=404, detail="Review not found")
    
    del reviews_store[review_id]
    return {"message": "Review deleted successfully"}


@router.get("/")
async def list_reviews() -> Dict[str, Any]:
    """
    List all reviews
    
    Returns a list of all reviews in the system.
    """
    reviews_list = [
        {
            "review_id": review_id,
            "status": review.status,
            "repository": review.repository,
            "pr_number": review.pr_number,
            "created_at": review.created_at,
        }
        for review_id, review in reviews_store.items()
    ]
    
    return {
        "total": len(reviews_list),
        "reviews": reviews_list,
    }
