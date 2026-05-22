import uuid
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Boolean, ForeignKey
)

from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(100), nullable=False)
    email           = Column(String(150), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)

    symptoms           = relationship("SymptomHistory",   back_populates="user", cascade="all, delete-orphan")
    medicine_reminders = relationship("MedicineReminder", back_populates="user", cascade="all, delete-orphan")
    dose_logs          = relationship("DoseLog",          back_populates="user", cascade="all, delete-orphan")


class SymptomHistory(Base):
    __tablename__ = "symptom_history"

    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    symptom    = Column(Text, nullable=False)
    analysis   = Column(Text, nullable=False)
    severity   = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="symptoms")


# ─────────────────────────────────────────────
# Medicine Reminder
# ─────────────────────────────────────────────

class MedicineReminder(Base):

    __tablename__ = "medicine_reminders"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    medicine_name = Column(
        String(200),
        nullable=False
    )

    dosage = Column(
        String(100),
        nullable=True
    )

    frequency = Column(
        String(100),
        nullable=True
    )

    reminder_times = Column(
        Text,
        nullable=True
    )

    notes = Column(
        Text,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    end_date = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="medicine_reminders"
    )

    dose_logs = relationship(
        "DoseLog",
        back_populates="reminder",
        cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────
# Dose Logs
# ─────────────────────────────────────────────

class DoseLog(Base):

    __tablename__ = "dose_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    reminder_id = Column(
        String,
        ForeignKey("medicine_reminders.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    status = Column(
        String(50),
        nullable=False
    )

    snoozed_until = Column(
        DateTime,
        nullable=True
    )

    logged_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="dose_logs"
    )

    reminder = relationship(
        "MedicineReminder",
        back_populates="dose_logs"
    )


class Conversation(Base):

    __tablename__ = "conversations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────
# Messages
# ─────────────────────────────────────────────

class Message(Base):

    __tablename__ = "messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )

    role = Column(
        String(50),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )