"""Configuration settings for the Test Generator application."""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration."""
    
    # Application settings
    app_name: str = "Generic Test Generator"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Paths
    tests_dir: str = "/app/tests"
    database_path: str = "/app/data/tests_stats.db"
    template_path: str = "/app/test-template.json"
    schema_path: str = "/app/test-schema.json"
    static_dir: str = "/app/static"
    templates_dir: str = "/app/templates"
    
    # Test configuration
    default_passing_grade: int = 70
    session_timeout: int = 3600  # 1 hour in seconds
    max_concurrent_sessions: int = 50
    
    # UI configuration
    default_theme: str = "generic"
    show_explanations_default: bool = True
    allow_review_default: bool = True
    shuffle_questions: bool = False
    shuffle_options: bool = False
    
    # Random test settings
    random_test_default_questions: int = 10
    random_test_max_questions: int = 20
    
    # Mobile-first settings
    mobile_breakpoint: int = 768
    touch_button_min_size: int = 44
    
    # Database settings
    database_pool_size: int = 10
    database_timeout: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Security
    cors_enabled: bool = False
    cors_origins: list = ["*"]
    
    # Development settings
    enable_api_docs: bool = True
    reload: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings


def ensure_directories():
    """Ensure required directories exist."""
    directories = [
        os.path.dirname(settings.database_path),
        settings.tests_dir,
        settings.static_dir,
        settings.templates_dir,
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"Created directory: {directory}")


def validate_test_files():
    """Validate that test files exist and are accessible."""
    if not os.path.exists(settings.tests_dir):
        raise FileNotFoundError(f"Tests directory not found: {settings.tests_dir}")
    
    # Check for at least one test file
    test_files = [f for f in os.listdir(settings.tests_dir) if f.endswith('.json')]
    if not test_files:
        print(f"Warning: No test files found in {settings.tests_dir}")
    else:
        print(f"Found {len(test_files)} test files")
    
    return test_files


if __name__ == "__main__":
    # For testing configuration
    print("Application Configuration:")
    print(f"App Name: {settings.app_name}")
    print(f"Version: {settings.app_version}")
    print(f"Host: {settings.host}:{settings.port}")
    print(f"Tests Directory: {settings.tests_dir}")
    print(f"Database Path: {settings.database_path}")
    print(f"Debug Mode: {settings.debug}")