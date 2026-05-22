import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# Database URL
# ─────────────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./medivoice.db"
)

# SQLite special config
connect_args = (
    {"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

# ─────────────────────────────────────────────
# Engine
# ─────────────────────────────────────────────
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
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
# Initialize + Fix DB Schema
# ─────────────────────────────────────────────
def init_db():

    # Import models
    from app.models.models import (
        User,
        SymptomHistory,
        MedicineReminder,
        DoseLog,
        Conversation,
        Message
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # ─────────────────────────────────────────
    # PostgreSQL schema fixes
    # ─────────────────────────────────────────
    if not DATABASE_URL.startswith("sqlite"):

        fix_sql = """
        DO $$

        BEGIN

            -- =====================================
            -- Fix user_id type
            -- =====================================
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'medicine_reminders'
                AND column_name = 'user_id'
                AND data_type = 'character varying'
            ) THEN

                ALTER TABLE medicine_reminders
                ALTER COLUMN user_id TYPE INTEGER
                USING user_id::INTEGER;

            END IF;


            -- =====================================
            -- Fix end_date type
            -- =====================================
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'medicine_reminders'
                AND column_name = 'end_date'
                AND data_type = 'character varying'
            ) THEN

                ALTER TABLE medicine_reminders
                ALTER COLUMN end_date TYPE TIMESTAMP
                USING end_date::TIMESTAMP;

            END IF;


            -- =====================================
            -- Fix id type
            -- =====================================
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'medicine_reminders'
                AND column_name = 'id'
                AND data_type = 'character varying'
            ) THEN

                ALTER TABLE medicine_reminders
                ALTER COLUMN id TYPE UUID
                USING id::UUID;

            END IF;

        END $$;
        """

        try:

            with engine.connect() as conn:

                conn.execute(text(fix_sql))
                conn.commit()

            print("✅ PostgreSQL schema fixes applied")

        except Exception as e:

            print("❌ DB migration fix failed:", e)