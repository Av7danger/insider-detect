"""
Exception handlers for the FastAPI application.

This module provides centralized exception handling for the API,
including custom exceptions and error response formatting.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from ..core.logging import get_logger


logger = get_logger(__name__)


class InsiderDetectException(Exception):
    """Base exception for Insider Detect application."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ModelLoadError(InsiderDetectException):
    """Raised when model loading fails."""
    pass


class ModelInferenceError(InsiderDetectException):
    """Raised when model inference fails."""
    pass


class ConfigurationError(InsiderDetectException):
    """Raised when configuration is invalid."""
    pass


class CacheError(InsiderDetectException):
    """Raised when cache operations fail."""
    pass


class ValidationError(InsiderDetectException):
    """Raised when input validation fails."""
    pass


def create_error_response(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create a standardized error response."""
    error_data = {
        "error": {
            "message": message,
            "code": error_code or "UNKNOWN_ERROR",
            "status_code": status_code,
        }
    }
    
    if details:
        error_data["error"]["details"] = details
    
    if request_id:
        error_data["error"]["request_id"] = request_id
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, "request_id", None)
    
    logger.warning(
        "HTTP exception occurred",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail,
            "url": str(request.url),
        }
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        error_code="HTTP_ERROR",
        request_id=request_id
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """Handle request validation errors."""
    request_id = getattr(request.state, "request_id", None)
    
    # Format validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(
        "Validation error occurred",
        extra={
            "request_id": request_id,
            "errors": errors,
            "url": str(request.url),
        }
    )
    
    return create_error_response(
        status_code=422,
        message="Validation error",
        error_code="VALIDATION_ERROR",
        details={"validation_errors": errors},
        request_id=request_id
    )


async def insider_detect_exception_handler(
    request: Request,
    exc: InsiderDetectException
) -> JSONResponse:
    """Handle custom Insider Detect exceptions."""
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(
        "Insider Detect exception occurred",
        extra={
            "request_id": request_id,
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "url": str(request.url),
        },
        exc_info=True
    )
    
    return create_error_response(
        status_code=500,
        message=exc.message,
        error_code=exc.error_code,
        details=exc.details,
        request_id=request_id
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    request_id = getattr(request.state, "request_id", None)
    
    logger.error(
        "Unhandled exception occurred",
        extra={
            "request_id": request_id,
            "exception_type": type(exc).__name__,
            "message": str(exc),
            "url": str(request.url),
        },
        exc_info=True
    )
    
    return create_error_response(
        status_code=500,
        message="Internal server error",
        error_code="INTERNAL_ERROR",
        request_id=request_id
    )


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup all exception handlers for the FastAPI application."""
    
    # Custom exception handlers
    app.add_exception_handler(InsiderDetectException, insider_detect_exception_handler)
    app.add_exception_handler(ModelLoadError, insider_detect_exception_handler)
    app.add_exception_handler(ModelInferenceError, insider_detect_exception_handler)
    app.add_exception_handler(ConfigurationError, insider_detect_exception_handler)
    app.add_exception_handler(CacheError, insider_detect_exception_handler)
    app.add_exception_handler(ValidationError, insider_detect_exception_handler)
    
    # FastAPI exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # General exception handler (must be last)
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers setup completed")
