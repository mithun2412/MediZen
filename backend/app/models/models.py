import uuid

from datetime import datetime

from sqlalchemy import (

    Column,
    Date,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Time
)
from sqlalchemy import Boolean

from sqlalchemy.orm import relationship

from app.database import Base


# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # RELATIONSHIPS

    symptoms = relationship(

        "SymptomHistory",

        back_populates="user",

        cascade="all, delete-orphan"
    )

    medicine_reminders = relationship(

        "MedicineReminder",

        back_populates="user",

        cascade="all, delete-orphan"
    )

    dose_logs = relationship(

        "DoseLog",

        back_populates="user",

        cascade="all, delete-orphan"
    )

    conversations = relationship(

        "Conversation",

        back_populates="user",

        cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────
# SYMPTOM HISTORY
# ─────────────────────────────────────────────

class SymptomHistory(Base):

    __tablename__ = "symptom_history"

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

    symptom = Column(
        Text,
        nullable=False
    )

    analysis = Column(
        Text,
        nullable=False
    )

    severity = Column(
        String(20),
        nullable=False
    )

    created_at = Column(

        DateTime,

        default=datetime.utcnow
    )

    user = relationship(

        "User",

        back_populates="symptoms"
    )


# ─────────────────────────────────────────────
# MEDICINE REMINDERS
# ─────────────────────────────────────────────

class MedicineReminder(Base):

    __tablename__ = "medicine_reminders"

    id = Column(String, primary_key=True)

    user_id = Column(Integer)

    medicine_name = Column(String)

    dosage = Column(String)

    reminder_time = Column(Time)

    end_date = Column(Date)

    status = Column(String)
    created_at = Column(

        DateTime,

        default=datetime.utcnow
    )

    # RELATIONSHIPS

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
# DOSE LOGS
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

        ForeignKey(
            "medicine_reminders.id"
        ),

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

    # RELATIONSHIPS

    user = relationship(

        "User",

        back_populates="dose_logs"
    )

    reminder = relationship(

        "MedicineReminder",

        back_populates="dose_logs"
    )


# ─────────────────────────────────────────────
# CONVERSATIONS
# ─────────────────────────────────────────────
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

    report_generated = Column(
        Boolean,
        default=False,
        nullable=False
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

    # RELATIONSHIPS

    user = relationship(
        "User",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


# ─────────────────────────────────────────────
# MESSAGES
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