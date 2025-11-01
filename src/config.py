import os
from typing import Optional

# Handle Pydantic v2 BaseSettings import
try:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict
    PYDANTIC_V2 = True
except ImportError:
    try:
        from pydantic import BaseSettings
        PYDANTIC_V2 = False
    except ImportError:
        # Fallback for newer versions
        class BaseSettings:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
        PYDANTIC_V2 = False


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # S3 Configuration
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "csv-upload-bucket")
    S3_ENDPOINT_URL: Optional[str] = os.getenv("S3_ENDPOINT_URL")  # For LocalStack or MinIO
    
    # File upload settings
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB to accommodate Excel files
    ALLOWED_FILE_EXTENSIONS: list = [".csv", ".xlsx", ".xls"]
    
    # Claude API Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    CLAUDE_MAX_TOKENS: int = int(os.getenv("CLAUDE_MAX_TOKENS", "32000"))
    CLAUDE_TEMPERATURE: float = float(os.getenv("CLAUDE_TEMPERATURE", "0.1"))
    
    # Mock Configuration
    AGENT_MOCK: bool = os.getenv("AGENT_MOCK", "false").lower() in ["true", "1", "yes"]
    # Debug/observability
    SHOW_AGENT_RESPONSE: bool = os.getenv("SHOW_AGENT_RESPONSE", "false").lower() in ["true", "1", "yes"]
    # Cache controls
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "true").lower() in ["true", "1", "yes"]
    AGENT_CACHE_ENABLED: bool = os.getenv("AGENT_CACHE_ENABLED", "true").lower() in ["true", "1", "yes"]
    
    # Rate limiting (requests per time window)
    # SECURITY: Enable rate limiting to prevent API abuse and cost overruns
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() in ["true", "1", "yes"]  # Changed default to TRUE
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "5"))  # Reduced from 10 to 5 for expensive analysis endpoint
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    
    # Circuit breaker
    CIRCUIT_BREAKER_ENABLED: bool = os.getenv("CIRCUIT_BREAKER_ENABLED", "false").lower() in ["true", "1", "yes"]
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5"))
    CIRCUIT_BREAKER_TIMEOUT_SECONDS: int = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT_SECONDS", "60"))
    CIRCUIT_BREAKER_SUCCESS_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_SUCCESS_THRESHOLD", "2"))
    
    if PYDANTIC_V2:
        model_config = ConfigDict(
            env_file=".env",
            case_sensitive=True,
            extra="ignore"  # Allow extra fields in .env file
        )
    else:
        class Config:
            env_file = ".env"
            case_sensitive = True
            extra = "ignore"


# Create global settings instance
settings = Settings()
