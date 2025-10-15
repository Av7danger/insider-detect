"""
Main FastAPI application factory and configuration.

This module provides the application factory pattern for creating
the FastAPI app with all necessary configurations, middleware, and routes.
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from ..core.config import get_settings, Environment
from ..core.logging import setup_logging, get_logger
from ..services.model_service import ModelService
from ..services.cache_service import CacheService
from ..services.monitoring_service import MonitoringService

from .middleware import setup_middleware
from .exceptions import setup_exception_handlers
from .routes import health, inference, models, monitoring


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown events."""
    settings = get_settings()
    
    # Startup
    logger.info("Starting Insider Threat Detection API", extra={
        "version": settings.version,
        "environment": settings.environment.value,
        "debug": settings.debug
    })
    
    # Initialize services
    try:
        # Initialize model service
        model_service = ModelService()
        await model_service.initialize()
        app.state.model_service = model_service
        
        # Initialize cache service
        cache_service = CacheService()
        await cache_service.initialize()
        app.state.cache_service = cache_service
        
        # Initialize monitoring service
        monitoring_service = MonitoringService()
        await monitoring_service.initialize()
        app.state.monitoring_service = monitoring_service
        
        logger.info("All services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Insider Threat Detection API")
    
    # Cleanup services
    try:
        if hasattr(app.state, 'model_service'):
            await app.state.model_service.cleanup()
        
        if hasattr(app.state, 'cache_service'):
            await app.state.cache_service.cleanup()
        
        if hasattr(app.state, 'monitoring_service'):
            await app.state.monitoring_service.cleanup()
        
        logger.info("All services cleaned up successfully")
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}", exc_info=True)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    
    # Setup logging
    setup_logging(settings)
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        description=settings.description,
        version=settings.version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.environment != Environment.PRODUCTION else None,
        redoc_url="/redoc" if settings.environment != Environment.PRODUCTION else None,
        openapi_url="/openapi.json" if settings.environment != Environment.PRODUCTION else None,
    )
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(inference.router, prefix="/api/v1", tags=["inference"])
    app.include_router(models.router, prefix="/api/v1", tags=["models"])
    app.include_router(monitoring.router, prefix="/api/v1", tags=["monitoring"])
    
    # Root endpoint
    @app.get("/", include_in_schema=False)
    async def root():
        """Root endpoint with basic API information."""
        return {
            "name": settings.app_name,
            "version": settings.version,
            "description": settings.description,
            "environment": settings.environment.value,
            "docs_url": "/docs" if settings.environment != Environment.PRODUCTION else None,
            "health_url": "/api/v1/health"
        }
    
    return app


def get_app() -> FastAPI:
    """Get the FastAPI application instance."""
    return create_app()


def run_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    workers: int = 1,
    reload: bool = False,
    log_level: str = "info"
):
    """Run the FastAPI server."""
    settings = get_settings()
    
    uvicorn.run(
        "src.insider_detect.api.app:get_app",
        host=host or settings.api.host,
        port=port or settings.api.port,
        workers=workers or settings.api.workers,
        reload=reload or settings.api.reload,
        log_level=log_level or settings.api.log_level.value.lower(),
        factory=True,
        access_log=True,
    )


# For direct execution
if __name__ == "__main__":
    run_server()
