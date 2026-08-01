from fastapi import APIRouter
from app.api.v1.endpoints import health

router = APIRouter(prefix="/api/v1")

# Include all endpoint routers
router.include_router(health.router, tags=["health"])