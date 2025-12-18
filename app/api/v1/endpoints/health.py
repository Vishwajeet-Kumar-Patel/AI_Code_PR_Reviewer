from fastapi import APIRouter
from typing import Dict, Any
from app.core.config import settings
from app.services.rag_service import RAGService
from app.core.logging import logger


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    
    Returns the health status of the application and its dependencies.
    """
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
        "services": {},
    }
    
    # Check GitHub service
    try:
        if settings.GITHUB_TOKEN:
            health_status["services"]["github"] = "configured"
        else:
            health_status["services"]["github"] = "not_configured"
    except Exception as e:
        health_status["services"]["github"] = f"error: {str(e)}"
    
    # Check AI provider
    try:
        if settings.AI_PROVIDER == "openai" and settings.is_openai_configured:
            health_status["services"]["ai_provider"] = "openai_configured"
        elif settings.AI_PROVIDER == "gemini" and settings.is_gemini_configured:
            health_status["services"]["ai_provider"] = "gemini_configured"
        else:
            health_status["services"]["ai_provider"] = "not_configured"
    except Exception as e:
        health_status["services"]["ai_provider"] = f"error: {str(e)}"
    
    # Check vector database
    try:
        rag_service = RAGService()
        stats = rag_service.get_collection_stats()
        health_status["services"]["vector_db"] = {
            "status": "operational",
            "documents": stats.get("document_count", 0),
        }
    except Exception as e:
        health_status["services"]["vector_db"] = f"error: {str(e)}"
    
    return health_status


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint
    
    Returns whether the application is ready to accept requests.
    """
    is_ready = True
    checks = {}
    
    # Check required configuration
    checks["github_token"] = bool(settings.GITHUB_TOKEN)
    checks["ai_provider"] = settings.is_openai_configured or settings.is_gemini_configured
    
    is_ready = checks["github_token"] and checks["ai_provider"]
    
    return {
        "ready": is_ready,
        "checks": checks,
    }


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check endpoint
    
    Returns whether the application is alive.
    """
    return {"status": "alive"}
