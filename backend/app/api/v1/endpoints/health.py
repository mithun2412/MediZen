from fastapi import APIRouter
from typing import Dict, Any
import time
import psutil
from app.core.config import get_settings
from app.core.database import  check_db_connection

router = APIRouter()

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check for load balancer and monitoring.
    Returns status of all critical services.
    """
    settings = get_settings()
    db_healthy = check_db_connection()
    
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    status = {
        "status": "healthy" if db_healthy else "unhealthy",
        "timestamp": time.time(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "message": "Database connection successful" if db_healthy else "Database connection failed"
            },
            "system": {
                "cpu_percent": round(cpu_percent, 2),
                "memory_used_percent": round(memory.percent, 2),
                "memory_available_mb": round(memory.available / (1024 * 1024), 2)
            },
            "ai_services": {
                "groq": "available"  # We'll check this properly later
            }
        }
    }
    
    return status

@router.get("/readiness")
async def readiness_check() -> Dict[str, str]:
    """
    Readiness probe for Kubernetes/load balancer.
    Indicates if service is ready to receive traffic.
    """
    db_healthy = check_db_connection()
    
    if not db_healthy:
        return {
            "status": "not_ready",
            "reason": "Database connection failed"
        }
    
    return {
        "status": "ready",
        "message": "Service is ready to receive traffic"
    }

@router.get("/liveness")
async def liveness_check() -> Dict[str, str]:
    """
    Liveness probe for Kubernetes.
    Indicates if service is still running.
    """
    return {"status": "alive"}

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Basic metrics endpoint (will be replaced by Prometheus later)
    """
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "service": "medizen-ai",
        "timestamp": time.time(),
        "system": {
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_total_mb": round(memory.total / (1024 * 1024), 2),
            "memory_used_mb": round(memory.used / (1024 * 1024), 2),
            "memory_percent": round(memory.percent, 2),
            "disk_total_gb": round(disk.total / (1024**3), 2),
            "disk_used_gb": round(disk.used / (1024**3), 2),
            "disk_percent": round(disk.percent, 2),
        }
    }