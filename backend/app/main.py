from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health_insights import (
    router as health_insights_router
)

from app.memory.patient_memory import (

    save_patient_memory,
    get_patient_history
)

from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from app.routes.disease_prediction import (
    router as disease_prediction_router
)

from contextlib import asynccontextmanager
from datetime import datetime

from app.database import (
    SessionLocal,
    init_db
)

from app.models.models import (
    MedicineReminder
)

from app.routes import auth, analyze

from app.routes.followup import (
    router as followup_router
)

from app.reminders_inapp import (
    router as reminder_router
)

from app.routes.voice import (
    router as voice_router
)

from app.routes.image_analysis import (
    router as image_analysis_router
)

# ─────────────────────────────────────────────
# Scheduler Job
# ─────────────────────────────────────────────
def deactivate_expired_reminders():

    db = SessionLocal()

    try:

        now = datetime.utcnow()

        expired = db.query(
            MedicineReminder
        ).filter(
            MedicineReminder.is_active == True,
            MedicineReminder.end_date != None,
            MedicineReminder.end_date <= now,
        ).all()

        if expired:

            for reminder in expired:
                reminder.is_active = False

            db.commit()

            print(
                f"[Scheduler] ✅ "
                f"Deactivated {len(expired)} "
                f"expired reminder(s)"
            )

        else:

            print(
                "[Scheduler] ℹ️ "
                "No expired reminders found"
            )

    except Exception as e:

        db.rollback()

        print(
            "[Scheduler] ❌ Error:",
            e
        )

    finally:

        db.close()


# ─────────────────────────────────────────────
# Scheduler
# ─────────────────────────────────────────────
scheduler = BackgroundScheduler(
    timezone="UTC"
)


# ─────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize DB + run migrations
    init_db()

    # Run reminder cleanup once
    deactivate_expired_reminders()

    # Schedule recurring cleanup
    scheduler.add_job(
        deactivate_expired_reminders,
        trigger="interval",
        minutes=30,
        id="expire_reminders",
        replace_existing=True,
    )

    scheduler.start()

    print(
        "[Startup] ✅ Reminder scheduler started"
    )

    yield

    # Shutdown
    if scheduler.running:

        scheduler.shutdown(wait=False)

        print(
            "[Shutdown] 🛑 Scheduler stopped"
        )


# ─────────────────────────────────────────────
# FastAPI App
# ─────────────────────────────────────────────
app = FastAPI(
    title="MediVoice AI Backend",
    description="AI-powered healthcare assistant API",
    version="2.0.0",
    lifespan=lifespan,
)


# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(analyze.router)
app.include_router(followup_router)
app.include_router(reminder_router)
app.include_router(voice_router)
app.include_router(health_insights_router)
app.include_router(disease_prediction_router)
app.include_router(
    image_analysis_router
)


# ─────────────────────────────────────────────
# Health Routes
# ─────────────────────────────────────────────
@app.get("/")
def root():

    return {
        "message": (
            "MediVoice AI Backend "
            "v2.0 running ✅"
        )
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.get("/health/scheduler")
def scheduler_health():

    jobs = [

        {
            "id": job.id,
            "next_run": str(job.next_run_time),
        }

        for job in scheduler.get_jobs()
    ]

    return {

        "scheduler_running": scheduler.running,

        "jobs": jobs,
    }

