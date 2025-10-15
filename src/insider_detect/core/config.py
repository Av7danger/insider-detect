"""
Enhanced configuration management system for Insider Threat Detection.

This module provides a comprehensive configuration system with support for:
- Environment-based configurations
- Model-specific settings
- Validation and type checking
- Hot-reloading capabilities
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseSettings, Field, validator
from enum import Enum


class Environment(str, Enum):
    """Supported environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Supported log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class DatabaseConfig(BaseSettings):
    """Database configuration."""
    url: str = Field(default="sqlite:///./insider_detect.db", description="Database URL")
    pool_size: int = Field(default=10, ge=1, le=100, description="Connection pool size")
    max_overflow: int = Field(default=20, ge=0, le=200, description="Max overflow connections")
    echo: bool = Field(default=False, description="Enable SQL echo")
    pool_pre_ping: bool = Field(default=True, description="Enable pool pre-ping")


class APIConfig(BaseSettings):
    """API configuration."""
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, ge=1, le=65535, description="API port")
    workers: int = Field(default=1, ge=1, le=32, description="Number of workers")
    reload: bool = Field(default=False, description="Enable auto-reload")
    log_level: LogLevel = Field(default=LogLevel.INFO, description="Log level")
    cors_origins: List[str] = Field(default=["*"], description="CORS origins")
    rate_limit: int = Field(default=100, ge=1, description="Rate limit per minute")
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v


class ModelConfig(BaseSettings):
    """Model configuration."""
    xgb_weight: float = Field(default=0.6, ge=0.0, le=1.0, description="XGBoost model weight")
    lstm_weight: float = Field(default=0.4, ge=0.0, le=1.0, description="LSTM model weight")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Prediction threshold")
    model_dir: str = Field(default="models/artifacts", description="Model directory")
    cache_enabled: bool = Field(default=True, description="Enable model caching")
    cache_ttl: int = Field(default=300, ge=1, description="Cache TTL in seconds")
    
    @validator('lstm_weight')
    def validate_weights(cls, v, values):
        if 'xgb_weight' in values:
            total = v + values['xgb_weight']
            if abs(total - 1.0) > 0.01:
                raise ValueError(f"Model weights must sum to 1.0, got {total}")
        return v


class MonitoringConfig(BaseSettings):
    """Monitoring and observability configuration."""
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    metrics_port: int = Field(default=9090, ge=1, le=65535, description="Metrics port")
    enable_tracing: bool = Field(default=False, description="Enable distributed tracing")
    jaeger_endpoint: Optional[str] = Field(default=None, description="Jaeger endpoint")
    log_format: str = Field(default="json", description="Log format (json/text)")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_rotation: bool = Field(default=True, description="Enable log rotation")


class SecurityConfig(BaseSettings):
    """Security configuration."""
    secret_key: str = Field(default="your-secret-key-here", description="Secret key")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, ge=1, description="Token expiry")
    enable_auth: bool = Field(default=False, description="Enable authentication")
    allowed_hosts: List[str] = Field(default=["*"], description="Allowed hosts")


class CacheConfig(BaseSettings):
    """Cache configuration."""
    enabled: bool = Field(default=True, description="Enable caching")
    backend: str = Field(default="memory", description="Cache backend")
    redis_url: Optional[str] = Field(default=None, description="Redis URL")
    ttl: int = Field(default=300, ge=1, description="Default TTL in seconds")
    max_size: int = Field(default=1000, ge=1, description="Max cache size")


class Settings(BaseSettings):
    """Main application settings."""
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    
    # Component configurations
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    
    # Application metadata
    app_name: str = Field(default="Insider Threat Detection", description="Application name")
    version: str = Field(default="2.0.0", description="Application version")
    description: str = Field(default="ML-powered insider threat detection system", description="App description")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_nested_delimiter = "__"


class ConfigManager:
    """Configuration manager with hot-reloading and validation."""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/environments")
        self._settings: Optional[Settings] = None
        self._last_modified: Optional[float] = None
    
    def load_config(self, environment: Optional[Environment] = None) -> Settings:
        """Load configuration for the specified environment."""
        if environment is None:
            environment = Environment(os.getenv("ENVIRONMENT", "development"))
        
        config_file = self.config_path / f"{environment.value}.yaml"
        
        # Load YAML configuration if it exists
        config_data = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
        
        # Override with environment variables
        env_vars = self._get_env_vars()
        config_data.update(env_vars)
        
        # Create settings instance
        self._settings = Settings(**config_data)
        self._last_modified = config_file.stat().st_mtime if config_file.exists() else 0
        
        return self._settings
    
    def get_settings(self) -> Settings:
        """Get current settings, reloading if necessary."""
        if self._settings is None:
            return self.load_config()
        
        # Check if config file has been modified
        if self.config_path.exists():
            config_file = self.config_path / f"{self._settings.environment.value}.yaml"
            if config_file.exists():
                current_modified = config_file.stat().st_mtime
                if current_modified > self._last_modified:
                    return self.load_config(self._settings.environment)
        
        return self._settings
    
    def _get_env_vars(self) -> Dict[str, Any]:
        """Extract configuration from environment variables."""
        config = {}
        
        for key, value in os.environ.items():
            if key.startswith("INSIDER_DETECT_"):
                # Remove prefix and convert to nested structure
                config_key = key[16:].lower().replace("__", ".")
                self._set_nested_value(config, config_key, value)
        
        return config
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: Any):
        """Set a nested value in the configuration dictionary."""
        keys = key.split(".")
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Convert value to appropriate type
        current[keys[-1]] = self._convert_value(value)
    
    def _convert_value(self, value: str) -> Union[str, int, float, bool, List[str]]:
        """Convert string value to appropriate type."""
        # Boolean conversion
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        
        # Numeric conversion
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # List conversion (comma-separated)
        if "," in value:
            return [item.strip() for item in value.split(",")]
        
        return value
    
    def validate_config(self) -> List[str]:
        """Validate current configuration and return any issues."""
        issues = []
        
        try:
            settings = self.get_settings()
            
            # Validate model weights
            if abs(settings.model.xgb_weight + settings.model.lstm_weight - 1.0) > 0.01:
                issues.append("Model weights must sum to 1.0")
            
            # Validate database URL
            if not settings.database.url:
                issues.append("Database URL is required")
            
            # Validate model directory
            model_dir = Path(settings.model.model_dir)
            if not model_dir.exists():
                issues.append(f"Model directory does not exist: {model_dir}")
            
        except Exception as e:
            issues.append(f"Configuration validation error: {str(e)}")
        
        return issues


# Global configuration manager instance
config_manager = ConfigManager()

# Convenience function to get settings
def get_settings() -> Settings:
    """Get current application settings."""
    return config_manager.get_settings()


# Environment-specific configuration loading
def load_environment_config(environment: Environment) -> Settings:
    """Load configuration for a specific environment."""
    return config_manager.load_config(environment)


# Configuration validation
def validate_configuration() -> List[str]:
    """Validate the current configuration."""
    return config_manager.validate_config()
