from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models.models import Base

from app.routes import auth, analyze
from app.routes.followup import router as followup_router
from app.reminders_inapp import router as reminder_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MediVoice AI Backend",
    description="AI-powered healthcare assistant API",
    version="2.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(followup_router)
app.include_router(reminder_router)

# Root Route
@app.get("/")
def root():
    return {
        "message": "MediVoice AI Backend v2.0 running ✅"
    }

# Health Check
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }