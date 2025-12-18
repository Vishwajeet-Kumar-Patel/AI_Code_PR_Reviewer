from fastapi import APIRouter
from app.api.v1.endpoints import review, repository, health


api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router)
api_router.include_router(review.router)
api_router.include_router(repository.router)
api_router.include_router(repository.pull_requests_router)
