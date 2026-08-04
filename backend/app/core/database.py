import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from app.core.config import get_settings

load_dotenv()

# Get settings
settings = get_settings()

# ─────────────────────────────────────────────
# Database URL
# ─────────────────────────────────────────────
DATABASE_URL = settings.DATABASE_URL

# SQLite special config
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

# ─────────────────────────────────────────────
# Engine WITH CONNECTION POOLING
# ─────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_size=settings.DB_POOL_SIZE,  # ← NEW
    max_overflow=settings.DB_MAX_OVERFLOW,  # ← NEW
    pool_timeout=settings.DB_POOL_TIMEOUT,  # ← NEW
    pool_pre_ping=True,  # Verify connections before using
    echo=settings.DB_ECHO,  # ← NEW
)

# ─────────────────────────────────────────────
# Session
# ─────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ─────────────────────────────────────────────
# Base
# ─────────────────────────────────────────────
Base = declarative_base()

# ─────────────────────────────────────────────
# Dependency
# ─────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────────
# Health Check Helper (NEW)
# ─────────────────────────────────────────────
def check_db_connection() -> bool:
    """Check if database is accessible"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
        return False

# ─────────────────────────────────────────────
# Initialize DB
# ─────────────────────────────────────────────
def init_db():
    # Import models
    from app.models.models import (
        User,
        SymptomHistory,
        MedicineReminder,
        DoseLog,
        Conversation,
        Message,
        Report,
        MedicationLog,
        HealthAnalytics,
        SymptomTrend,
    )

    # Create tables
    Base.metadata.create_all(bind=engine)
    # Existing databases need an additive migration because create_all does not
    # alter a table that has already been created.
    try:
        with engine.begin() as conn:
            if DATABASE_URL.startswith("sqlite"):
                columns = {row[1] for row in conn.execute(text("PRAGMA table_info(symptom_history)"))}
                if "status" not in columns: conn.execute(text("ALTER TABLE symptom_history ADD COLUMN status VARCHAR(16) NOT NULL DEFAULT 'Active'"))
                if "started_at" not in columns: conn.execute(text("ALTER TABLE symptom_history ADD COLUMN started_at DATETIME"))
                if "resolved_at" not in columns: conn.execute(text("ALTER TABLE symptom_history ADD COLUMN resolved_at DATETIME"))
            else:
                conn.execute(text("ALTER TABLE symptom_history ADD COLUMN IF NOT EXISTS status VARCHAR(16) NOT NULL DEFAULT 'Active'"))
                conn.execute(text("ALTER TABLE symptom_history ADD COLUMN IF NOT EXISTS started_at TIMESTAMP"))
                conn.execute(text("ALTER TABLE symptom_history ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP"))
            conn.execute(text("UPDATE symptom_history SET started_at = COALESCE(started_at, created_at), status = COALESCE(status, 'Active')"))
    except Exception as e:
        print(f"Symptom lifecycle schema check: {e}")
    print("✅ Database tables created/verified")

    # ─────────────────────────────────────────
    # PostgreSQL schema fixes (if needed)
    # ─────────────────────────────────────────
    if not DATABASE_URL.startswith("sqlite"):
        try:
            with engine.connect() as conn:
                # Check and fix any column type issues
                conn.execute(text("""
                    DO $$
                    BEGIN
                        -- Check if medicine_reminders table exists
                        IF EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_name = 'medicine_reminders'
                        ) THEN
                            -- Fix id type to UUID if it's not already
                            IF EXISTS (
                                SELECT 1 FROM information_schema.columns
                                WHERE table_name = 'medicine_reminders'
                                AND column_name = 'id'
                                AND data_type = 'character varying'
                            ) THEN
                                ALTER TABLE medicine_reminders 
                                ALTER COLUMN id TYPE UUID USING id::UUID;
                            END IF;
                        END IF;
                    END $$;
                """))
                conn.commit()
            print("✅ PostgreSQL schema verified")
        except Exception as e:
            print(f"⚠️ PostgreSQL schema check: {e}")
