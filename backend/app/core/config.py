from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MediZen AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Using lru_cache means we only load .env once.
    """
    return Settings()