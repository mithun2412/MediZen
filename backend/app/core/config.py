from functools import lru_cache
from typing import List, Optional
from pydantic import Field, root_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
import secrets

load_dotenv()

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MediZen AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = Field(default="sqlite:///./dev.db")
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False
    
    # Redis (for later)
    REDIS_URL: Optional[str] = None
    
    # AI Services
    GROQ_API_KEY: Optional[str] = None
    
    # CORS - IMPORTANT: Add your frontend URLs here
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8000",
    ]
    
    # Rate Limiting (for later)
    RATE_LIMIT_PER_MINUTE: int = 60

    @root_validator(pre=True)
    def require_production_settings(cls, values):
        env = values.get("ENVIRONMENT") or os.getenv("ENVIRONMENT", "development")
        if env.lower() == "production":
            missing = []
            if not values.get("SECRET_KEY"):
                missing.append("SECRET_KEY")
            if not values.get("DATABASE_URL"):
                missing.append("DATABASE_URL")
            if missing:
                raise ValueError(
                    "Missing required environment variables in production: "
                    + ", ".join(missing)
                    + ". Set them in the deployment environment or provide a .env file."
                )
        return values
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Using lru_cache means we only load .env once.
    """
    return Settings()