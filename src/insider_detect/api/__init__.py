"""
Insider Threat Detection API Package.

This package contains the FastAPI application and all API-related components.
"""

from .app import create_app, get_app
from .routes import health, inference, models, monitoring
from .middleware import setup_middleware
from .exceptions import setup_exception_handlers

__all__ = [
    "create_app",
    "get_app", 
    "health",
    "inference",
    "models",
    "monitoring",
    "setup_middleware",
    "setup_exception_handlers"
]
