"""
Command-line interface for Insider Threat Detection System.

This module provides a comprehensive CLI for managing the application,
including development, deployment, and maintenance tasks.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .core.config import get_settings, Environment, validate_configuration
from .core.logging import setup_logging, get_logger
from .api.app import run_server
from .services.model_service import ModelService


app = typer.Typer(
    name="insider-detect",
    help="Insider Threat Detection System CLI",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Show version information."""
    settings = get_settings()
    console.print(f"Insider Threat Detection System v{settings.version}")


@app.command()
def config(
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    validate: bool = typer.Option(False, "--validate", "-v", help="Validate configuration"),
    environment: Optional[Environment] = typer.Option(None, "--env", "-e", help="Environment to use"),
):
    """Manage configuration."""
    if show:
        _show_config(environment)
    elif validate:
        _validate_config(environment)
    else:
        console.print("Use --show or --validate options")


def _show_config(environment: Optional[Environment]):
    """Show current configuration."""
    settings = get_settings()
    
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Environment", settings.environment.value)
    table.add_row("Debug", str(settings.debug))
    table.add_row("API Host", settings.api.host)
    table.add_row("API Port", str(settings.api.port))
    table.add_row("Database URL", settings.database.url)
    table.add_row("Model Directory", settings.model.model_dir)
    table.add_row("XGBoost Weight", str(settings.model.xgb_weight))
    table.add_row("LSTM Weight", str(settings.model.lstm_weight))
    table.add_row("Threshold", str(settings.model.threshold))
    table.add_row("Cache Enabled", str(settings.cache.enabled))
    table.add_row("Log Level", settings.monitoring.log_level.value)
    
    console.print(table)


def _validate_config(environment: Optional[Environment]):
    """Validate configuration."""
    issues = validate_configuration()
    
    if not issues:
        console.print(Panel("✅ Configuration is valid", style="green"))
    else:
        console.print(Panel("❌ Configuration issues found:", style="red"))
        for issue in issues:
            console.print(f"  • {issue}")


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    workers: int = typer.Option(1, "--workers", "-w", help="Number of workers"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
    log_level: str = typer.Option("info", "--log-level", "-l", help="Log level"),
):
    """Start the API server."""
    console.print(f"🚀 Starting Insider Threat Detection API on {host}:{port}")
    
    try:
        run_server(
            host=host,
            port=port,
            workers=workers,
            reload=reload,
            log_level=log_level
        )
    except KeyboardInterrupt:
        console.print("\n👋 Server stopped")
    except Exception as e:
        console.print(f"❌ Server failed to start: {e}")
        sys.exit(1)


@app.command()
def models(
    list_models: bool = typer.Option(False, "--list", "-l", help="List available models"),
    health: bool = typer.Option(False, "--health", "-h", help="Check model health"),
    load: bool = typer.Option(False, "--load", help="Load models"),
):
    """Manage ML models."""
    if list_models:
        _list_models()
    elif health:
        _check_model_health()
    elif load:
        _load_models()
    else:
        console.print("Use --list, --health, or --load options")


async def _list_models():
    """List available models."""
    model_service = ModelService()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading models...", total=None)
        
        try:
            await model_service.initialize()
            model_info = await model_service.get_model_info()
            
            progress.update(task, description="✅ Models loaded")
            
            table = Table(title="Available Models")
            table.add_column("Name", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Type", style="yellow")
            table.add_column("Created", style="blue")
            
            for name, metadata in model_info.items():
                table.add_row(
                    metadata.name,
                    metadata.version,
                    metadata.model_type.value,
                    metadata.created_at
                )
            
            console.print(table)
            
        except Exception as e:
            progress.update(task, description=f"❌ Failed to load models: {e}")
            console.print(f"Error: {e}")


async def _check_model_health():
    """Check model health."""
    model_service = ModelService()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Checking model health...", total=None)
        
        try:
            await model_service.initialize()
            health = await model_service.get_model_health()
            
            progress.update(task, description="✅ Health check completed")
            
            table = Table(title="Model Health")
            table.add_column("Status", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in health.items():
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                table.add_row(key, str(value))
            
            console.print(table)
            
        except Exception as e:
            progress.update(task, description=f"❌ Health check failed: {e}")
            console.print(f"Error: {e}")


async def _load_models():
    """Load models."""
    model_service = ModelService()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Loading models...", total=None)
        
        try:
            await model_service.initialize()
            progress.update(task, description="✅ Models loaded successfully")
            console.print("Models loaded successfully!")
            
        except Exception as e:
            progress.update(task, description=f"❌ Failed to load models: {e}")
            console.print(f"Error: {e}")


@app.command()
def test(
    path: Optional[str] = typer.Option(None, "--path", "-p", help="Test path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    coverage: bool = typer.Option(False, "--coverage", "-c", help="Run with coverage"),
):
    """Run tests."""
    import subprocess
    
    cmd = ["python", "-m", "pytest"]
    
    if path:
        cmd.append(path)
    else:
        cmd.append("tests/")
    
    if verbose:
        cmd.append("-v")
    
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
    
    console.print(f"🧪 Running tests: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        console.print("✅ Tests passed!")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Tests failed with exit code {e.returncode}")
        sys.exit(e.returncode)


@app.command()
def format_code(
    check: bool = typer.Option(False, "--check", "-c", help="Check formatting without changing files"),
):
    """Format code using black and isort."""
    import subprocess
    
    if check:
        console.print("🔍 Checking code formatting...")
        black_cmd = ["python", "-m", "black", "--check", "src/", "tests/"]
        isort_cmd = ["python", "-m", "isort", "--check-only", "src/", "tests/"]
    else:
        console.print("🎨 Formatting code...")
        black_cmd = ["python", "-m", "black", "src/", "tests/"]
        isort_cmd = ["python", "-m", "isort", "src/", "tests/"]
    
    try:
        subprocess.run(black_cmd, check=True)
        subprocess.run(isort_cmd, check=True)
        console.print("✅ Code formatting completed!")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Code formatting failed: {e}")
        sys.exit(e.returncode)


@app.command()
def lint():
    """Run linting checks."""
    import subprocess
    
    console.print("🔍 Running linting checks...")
    
    try:
        # Run flake8
        subprocess.run(["python", "-m", "flake8", "src/", "tests/"], check=True)
        
        # Run mypy
        subprocess.run(["python", "-m", "mypy", "src/"], check=True)
        
        console.print("✅ Linting checks passed!")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Linting checks failed: {e}")
        sys.exit(e.returncode)


@app.command()
def init(
    environment: Environment = typer.Option(Environment.DEVELOPMENT, "--env", "-e", help="Environment"),
    force: bool = typer.Option(False, "--force", "-f", help="Force initialization"),
):
    """Initialize the application."""
    console.print(f"🚀 Initializing Insider Threat Detection System for {environment.value} environment")
    
    # Create necessary directories
    directories = [
        "logs",
        "data/raw",
        "data/processed",
        "models/artifacts",
        "models/checkpoints",
        "config/environments",
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        console.print(f"  📁 Created directory: {directory}")
    
    # Create default configuration files
    config_files = [
        ("config/environments/development.yaml", _get_development_config()),
        ("config/environments/production.yaml", _get_production_config()),
        (".env.example", _get_env_example()),
    ]
    
    for file_path, content in config_files:
        if not Path(file_path).exists() or force:
            Path(file_path).write_text(content)
            console.print(f"  📄 Created file: {file_path}")
    
    console.print("✅ Initialization completed!")


def _get_development_config() -> str:
    """Get development configuration template."""
    return """# Development Environment Configuration
api:
  host: "0.0.0.0"
  port: 8000
  reload: true
  log_level: "DEBUG"

database:
  url: "sqlite:///./insider_detect_dev.db"
  echo: true

model:
  xgb_weight: 0.6
  lstm_weight: 0.4
  threshold: 0.5
  model_dir: "models/artifacts"

monitoring:
  log_level: "DEBUG"
  log_format: "text"
  enable_metrics: true

cache:
  enabled: true
  backend: "memory"
  ttl: 300
"""


def _get_production_config() -> str:
    """Get production configuration template."""
    return """# Production Environment Configuration
api:
  host: "0.0.0.0"
  port: 8000
  reload: false
  log_level: "INFO"

database:
  url: "postgresql://user:password@localhost/insider_detect"
  echo: false

model:
  xgb_weight: 0.6
  lstm_weight: 0.4
  threshold: 0.5
  model_dir: "models/artifacts"

monitoring:
  log_level: "INFO"
  log_format: "json"
  enable_metrics: true

cache:
  enabled: true
  backend: "redis"
  redis_url: "redis://localhost:6379/0"
  ttl: 300
"""


def _get_env_example() -> str:
    """Get environment variables example."""
    return """# Environment Variables Example
# Copy this file to .env and update the values

# Environment
ENVIRONMENT=development
DEBUG=true

# API Configuration
INSIDER_DETECT_API__HOST=0.0.0.0
INSIDER_DETECT_API__PORT=8000
INSIDER_DETECT_API__LOG_LEVEL=INFO

# Database
INSIDER_DETECT_DATABASE__URL=sqlite:///./insider_detect.db

# Model Configuration
INSIDER_DETECT_MODEL__XGB_WEIGHT=0.6
INSIDER_DETECT_MODEL__LSTM_WEIGHT=0.4
INSIDER_DETECT_MODEL__THRESHOLD=0.5

# Security
INSIDER_DETECT_SECURITY__SECRET_KEY=your-secret-key-here

# Monitoring
INSIDER_DETECT_MONITORING__LOG_LEVEL=INFO
INSIDER_DETECT_MONITORING__LOG_FORMAT=json
"""


def main():
    """Main CLI entry point."""
    # Setup logging for CLI
    setup_logging()
    
    # Run async commands
    if len(sys.argv) > 1 and sys.argv[1] in ["models"]:
        if len(sys.argv) > 2 and sys.argv[2] in ["--list", "-l", "--health", "-h", "--load"]:
            asyncio.run(app())
        else:
            app()
    else:
        app()


if __name__ == "__main__":
    main()
