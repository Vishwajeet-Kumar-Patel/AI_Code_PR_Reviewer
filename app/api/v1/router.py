from fastapi import APIRouter
from app.api.v1.endpoints import (
    review, repository, health, auth, websocket, 
    webhooks, analytics, plugins, organizations, security,
    ml_training, code_fixes, advanced_analytics
)


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(review.router)
api_router.include_router(repository.router)
api_router.include_router(repository.pull_requests_router)
api_router.include_router(websocket.router)
api_router.include_router(webhooks.router)
api_router.include_router(analytics.router)
api_router.include_router(advanced_analytics.router)  # New advanced analytics
api_router.include_router(plugins.router)
api_router.include_router(organizations.router)
api_router.include_router(security.router)

# New advanced features
api_router.include_router(ml_training.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(code_fixes.router, prefix="/code-fixes", tags=["Code Fixes"])
