# app/models/models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import  Base
from datetime import datetime
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    reminders = relationship("MedicineReminder", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    symptom_history = relationship("SymptomHistory", back_populates="user", cascade="all, delete-orphan")
    medication_logs = relationship("MedicationLog", back_populates="user", cascade="all, delete-orphan")
    health_analytics = relationship("HealthAnalytics", back_populates="user", uselist=False, cascade="all, delete-orphan")
    symptom_trends = relationship("SymptomTrend", back_populates="user", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    report_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added
    
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added
    
    conversation = relationship("Conversation", back_populates="messages")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added
    
    user = relationship("User", back_populates="reports")

class SymptomHistory(Base):
    __tablename__ = "symptom_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symptom = Column(String, nullable=False)
    severity = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Episodes are retained after recovery so historical and recurrence metrics
    # never lose clinical context.
    status = Column(String(16), nullable=False, default="Active", index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="symptom_history")

class MedicineReminder(Base):
    __tablename__ = "medicine_reminders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medicine_name = Column(String, nullable=False)
    dosage = Column(String, nullable=True)
    frequency = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added
    is_active = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="reminders")
    dose_logs = relationship("DoseLog", back_populates="reminder", cascade="all, delete-orphan")

class DoseLog(Base):
    __tablename__ = "dose_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(UUID(as_uuid=True), ForeignKey("medicine_reminders.id"), nullable=False)
    taken_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="taken")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    reminder = relationship("MedicineReminder", back_populates="dose_logs")


class MedicationLog(Base):
    """Immutable per-dose tracking record used by analytics and the medication tracker."""
    __tablename__ = "medication_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reminder_id = Column(String, nullable=True, index=True)
    medicine_name = Column(String, nullable=False)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    status = Column(String(16), nullable=False, default="Pending")
    taken_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="medication_logs")


class HealthAnalytics(Base):
    __tablename__ = "health_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    health_score = Column(Integer, nullable=False, default=100)
    adherence_percentage = Column(Float, nullable=False, default=0)
    risk_level = Column(String(16), nullable=False, default="Low")
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="health_analytics")


class SymptomTrend(Base):
    __tablename__ = "symptom_trends"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symptom_name = Column(String, nullable=False)
    severity = Column(String(16), nullable=False)
    recorded_date = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("User", back_populates="symptom_trends")

class ReportParameter(Base):
    __tablename__ = "report_parameters"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    parameter_name = Column(String, nullable=False)
    parameter_value = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    reference_range = Column(String, nullable=True)
    is_abnormal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added

class ReportChat(Base):
    __tablename__ = "report_chats"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String, ForeignKey("reports.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Added
