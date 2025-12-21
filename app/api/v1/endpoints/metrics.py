"""
Metrics endpoint
"""
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter(prefix="/metrics", tags=["Monitoring"])


@router.get("", include_in_schema=False)
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/health", include_in_schema=False)
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-code-reviewer"
    }
