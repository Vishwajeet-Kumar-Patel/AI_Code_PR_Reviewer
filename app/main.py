from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.core.middleware import MetricsMiddleware, RequestLoggingMiddleware
from app.api.v1.router import api_router
from app.api.v1.endpoints import metrics as metrics_endpoint


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Code & PR Review System",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(MetricsMiddleware)
app.add_middleware(RequestLoggingMiddleware)


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"AI Provider: {settings.AI_PROVIDER}")
    
    # Initialize services (optional - comment out if causing issues)
    # try:
    #     from app.services import RAGService
    #     rag_service = RAGService()
    #     stats = rag_service.get_collection_stats()
    #     logger.info(f"Vector DB initialized with {stats.get('document_count', 0)} documents")
    # except Exception as e:
    #     logger.warning(f"Failed to initialize vector DB: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info(f"Shutting down {settings.APP_NAME}")


# Include API router
app.include_router(api_router)
app.include_router(metrics_endpoint.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI-Powered Code & PR Review System",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
