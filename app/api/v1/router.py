from fastapi import APIRouter
from app.api.v1.endpoints import (
    review, repository, health, auth, websocket, 
    webhooks, analytics, plugins, organizations, security
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
api_router.include_router(plugins.router)
api_router.include_router(organizations.router)
api_router.include_router(security.router)
