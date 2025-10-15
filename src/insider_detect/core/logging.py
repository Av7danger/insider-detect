"""
Enhanced logging configuration for Insider Threat Detection.

This module provides structured logging with support for:
- JSON formatting for production
- File rotation and management
- Contextual logging with request IDs
- Performance monitoring
- Security event logging
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime
import json
import traceback

from ..core.config import get_settings, LogLevel


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "lineno", "funcName", "created",
                "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "getMessage", "exc_info",
                "exc_text", "stack_info"
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class ContextualFilter(logging.Filter):
    """Filter to add contextual information to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add contextual information to the log record."""
        # Add request ID if available
        if hasattr(record, "request_id"):
            record.request_id = record.request_id
        
        # Add user ID if available
        if hasattr(record, "user_id"):
            record.user_id = record.user_id
        
        # Add session ID if available
        if hasattr(record, "session_id"):
            record.session_id = record.session_id
        
        return True


class SecurityLogger:
    """Specialized logger for security events."""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.logger.setLevel(logging.INFO)
    
    def log_threat_detected(
        self,
        user_id: str,
        session_id: str,
        threat_score: float,
        details: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Log a detected threat."""
        self.logger.warning(
            "Threat detected",
            extra={
                "event_type": "threat_detected",
                "user_id": user_id,
                "session_id": session_id,
                "threat_score": threat_score,
                "details": details,
                "request_id": request_id,
                "severity": "high" if threat_score > 0.8 else "medium" if threat_score > 0.5 else "low",
            }
        )
    
    def log_authentication_failure(
        self,
        user_id: Optional[str],
        ip_address: str,
        reason: str,
        request_id: Optional[str] = None
    ):
        """Log authentication failure."""
        self.logger.warning(
            "Authentication failure",
            extra={
                "event_type": "auth_failure",
                "user_id": user_id,
                "ip_address": ip_address,
                "reason": reason,
                "request_id": request_id,
            }
        )
    
    def log_rate_limit_exceeded(
        self,
        ip_address: str,
        endpoint: str,
        limit: int,
        request_id: Optional[str] = None
    ):
        """Log rate limit exceeded."""
        self.logger.warning(
            "Rate limit exceeded",
            extra={
                "event_type": "rate_limit_exceeded",
                "ip_address": ip_address,
                "endpoint": endpoint,
                "limit": limit,
                "request_id": request_id,
            }
        )


class PerformanceLogger:
    """Specialized logger for performance monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
        self.logger.setLevel(logging.INFO)
    
    def log_inference_time(
        self,
        model_name: str,
        inference_time: float,
        input_size: int,
        request_id: Optional[str] = None
    ):
        """Log model inference performance."""
        self.logger.info(
            "Model inference completed",
            extra={
                "event_type": "model_inference",
                "model_name": model_name,
                "inference_time_ms": inference_time * 1000,
                "input_size": input_size,
                "request_id": request_id,
            }
        )
    
    def log_api_response_time(
        self,
        endpoint: str,
        method: str,
        response_time: float,
        status_code: int,
        request_id: Optional[str] = None
    ):
        """Log API response time."""
        self.logger.info(
            "API request completed",
            extra={
                "event_type": "api_request",
                "endpoint": endpoint,
                "method": method,
                "response_time_ms": response_time * 1000,
                "status_code": status_code,
                "request_id": request_id,
            }
        )


def setup_logging(settings=None) -> None:
    """Setup logging configuration."""
    if settings is None:
        settings = get_settings()
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.monitoring.log_level.value))
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.monitoring.log_level.value))
    
    if settings.monitoring.log_format == "json":
        console_formatter = JSONFormatter()
    else:
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(ContextualFilter())
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if settings.monitoring.log_file:
        log_file = Path(settings.monitoring.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, settings.monitoring.log_level.value))
        file_handler.setFormatter(JSONFormatter())
        file_handler.addFilter(ContextualFilter())
        root_logger.addHandler(file_handler)
    
    # Security events log
    security_log_file = log_dir / "security.log"
    security_handler = logging.handlers.RotatingFileHandler(
        security_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8"
    )
    security_handler.setLevel(logging.WARNING)
    security_handler.setFormatter(JSONFormatter())
    security_handler.addFilter(ContextualFilter())
    
    security_logger = logging.getLogger("security")
    security_logger.addHandler(security_handler)
    security_logger.propagate = False
    
    # Performance log
    performance_log_file = log_dir / "performance.log"
    performance_handler = logging.handlers.RotatingFileHandler(
        performance_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    performance_handler.setLevel(logging.INFO)
    performance_handler.setFormatter(JSONFormatter())
    performance_handler.addFilter(ContextualFilter())
    
    performance_logger = logging.getLogger("performance")
    performance_logger.addHandler(performance_handler)
    performance_logger.propagate = False
    
    # API log
    api_log_file = log_dir / "api.log"
    api_handler = logging.handlers.RotatingFileHandler(
        api_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(JSONFormatter())
    api_handler.addFilter(ContextualFilter())
    
    api_logger = logging.getLogger("api")
    api_logger.addHandler(api_handler)
    api_logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def get_security_logger() -> SecurityLogger:
    """Get the security logger instance."""
    return SecurityLogger()


def get_performance_logger() -> PerformanceLogger:
    """Get the performance logger instance."""
    return PerformanceLogger()


# Global logger instances
security_logger = get_security_logger()
performance_logger = get_performance_logger()
