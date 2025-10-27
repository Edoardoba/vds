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
