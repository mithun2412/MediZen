import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import (
    conversation,
    uploads,
    analytics,
    auth,
    reminders,
    knowledge,
)
from app.routes.health import analytics_router, medications_router, reports_router
from app.core.database import  Base, engine, init_db
from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.middleware.request_tracker import RequestTrackerMiddleware
from app.api.v1.router import router as api_v1_router
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.database import SessionLocal
from app.services.health_insights_service import mark_overdue_medication_logs
from app.routes.reminders import check_and_create_dose_logs
from app.rag.rag_service import rag_service

# ─────────────────────────────────────────────
# SETUP LOGGING (NEW)
# ─────────────────────────────────────────────
setup_logging()
logger = get_logger(__name__)

# ─────────────────────────────────────────────
# LOAD CONFIGURATION (NEW)
# ─────────────────────────────────────────────
settings = get_settings()

logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
logger.info(f"Environment: {settings.ENVIRONMENT}")

# ─────────────────────────────────────────────
# CREATE DATABASE TABLES
# ─────────────────────────────────────────────
init_db()

# ─────────────────────────────────────────────
# CREATE REQUIRED FOLDERS
# ─────────────────────────────────────────────
os.makedirs("uploads", exist_ok=True)
os.makedirs("reports", exist_ok=True)
os.makedirs("logs", exist_ok=True)  # ← NEW

# ─────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,  # ← CHANGED: use from config
    description="Conversational Multimodal Healthcare AI Platform",
    version=settings.APP_VERSION,  # ← CHANGED: use from config
    docs_url="/docs" if settings.DEBUG else None,  # ← NEW: hide in production
    redoc_url="/redoc" if settings.DEBUG else None,  # ← NEW
)

# ─────────────────────────────────────────────
# REQUEST TRACKING MIDDLEWARE (NEW)
# ─────────────────────────────────────────────
app.add_middleware(RequestTrackerMiddleware)

# ─────────────────────────────────────────────
# CORS (IMPROVED)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # ← CHANGED: use config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# STATIC FILES
# ─────────────────────────────────────────────
# IMAGE UPLOADS
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)

# PDF REPORTS
app.mount(
    "/reports",
    StaticFiles(directory="reports"),
    name="reports"
)

# ─────────────────────────────────────────────
# API ROUTES (CLEANED UP - no duplicates)
# ─────────────────────────────────────────────

# Authentication
app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)

app.include_router(analytics_router, prefix="/api")
app.include_router(medications_router, prefix="/api")
app.include_router(reports_router, prefix="/api")

# Analytics
app.include_router(
    analytics.router,
    prefix="/api/analytics",
    tags=["Analytics"]
)

# Conversation
app.include_router(
    conversation.router,
    prefix="/api/conversation",
    tags=["Conversation AI"]
)

# Uploads
app.include_router(
    uploads.router,
    prefix="/api/uploads",
    tags=["Uploads"]
)

# Reminders
app.include_router(
    reminders.router,
    prefix="/api/reminders",  # ← FIXED: was "/api" before
    tags=["Reminders"]
)

app.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["Knowledge Base"],
)

# ─────────────────────────────────────────────
# V1 API ROUTES (NEW - for versioning)
# ─────────────────────────────────────────────
app.include_router(api_v1_router)

# ─────────────────────────────────────────────
# ROOT ENDPOINT (IMPROVED)
# ─────────────────────────────────────────────
@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {
        "message": f"{settings.APP_NAME} Backend Running",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else None,
        "status": "success"
    }

# ─────────────────────────────────────────────
# HEALTH CHECK (IMPROVED - now at /health and /api/v1/health)
# ─────────────────────────────────────────────
@app.get("/health")
def health_check():
    """Basic health check endpoint"""
    return {
        "server": "running",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

# ─────────────────────────────────────────────
# STARTUP EVENT (NEW)
# ─────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    # Load an existing vector store or rebuild it only when the source PDF changed.
    rag_service.initialize()
    scheduler = BackgroundScheduler()
    def update_overdue_doses():
        db = SessionLocal()
        try:
            mark_overdue_medication_logs(db)
        finally:
            db.close()
    def create_scheduled_medication_logs():
        db = SessionLocal()
        try:
            check_and_create_dose_logs(db)
        finally:
            db.close()
    scheduler.add_job(update_overdue_doses, "interval", minutes=5, id="medication-status-update", replace_existing=True)
    scheduler.add_job(create_scheduled_medication_logs, "interval", minutes=1, id="medication-log-create", replace_existing=True)
    scheduler.start()
    app.state.health_scheduler = scheduler
    logger.info(f"🚀 {settings.APP_NAME} started successfully")
    logger.info(f"📊 Database pool size: {settings.DB_POOL_SIZE}")
    logger.info(f"🌐 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔗 Allowed origins: {settings.BACKEND_CORS_ORIGINS}")

# ─────────────────────────────────────────────
# SHUTDOWN EVENT (NEW)
# ─────────────────────────────────────────────
@app.on_event("shutdown")
async def shutdown_event():
    scheduler = getattr(app.state, "health_scheduler", None)
    if scheduler:
        scheduler.shutdown(wait=False)
    logger.info(f"🛑 {settings.APP_NAME} shutting down")

# ─────────────────────────────────────────────
# RUN (for development)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        reload_excludes=[  # ← ADD THIS SECTION
            "*.log",
            "logs/*",
            "uploads/*",
            "reports/*",
            "*.db",
            "__pycache__/*",
            "*.pyc",
        ],
        workers=1,
        log_level="info",
    )
