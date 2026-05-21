"""
MediVoice — Medicine Reminder (In-App Only)
Pure CRUD + dose logging. No Twilio. No APScheduler.
Notifications are handled entirely by the frontend.
Uses SQLAlchemy to match the existing project DB setup.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional, List
from datetime import datetime
import uuid
import json

from app.database import engine, get_db
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/reminders", tags=["reminders"])

# ─────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────
ReminderBase = declarative_base()


class MedicineReminder(ReminderBase):
    __tablename__ = "medicine_reminders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    medicine_name = Column(String, nullable=False)
    dosage = Column(String, nullable=False)
    frequency = Column(String, nullable=False)
    reminder_times = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    end_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DoseLogModel(ReminderBase):
    __tablename__ = "dose_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    reminder_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    snoozed_until = Column(String, nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)


# Create tables automatically
ReminderBase.metadata.create_all(bind=engine)

# ─────────────────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────────────────
class ReminderCreate(BaseModel):
    medicine_name: str
    dosage: str
    frequency: str
    reminder_times: List[str]
    notes: Optional[str] = None
    end_date: Optional[str] = None


class ReminderUpdate(BaseModel):
    medicine_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reminder_times: Optional[List[str]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    end_date: Optional[str] = None


class DoseLog(BaseModel):
    reminder_id: str
    status: str
    snoozed_until: Optional[str] = None


# ─────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────
def reminder_to_dict(r: MedicineReminder, today_status=None):
    return {
        "id": r.id,
        "medicine_name": r.medicine_name,
        "dosage": r.dosage,
        "frequency": r.frequency,
        "reminder_times": json.loads(r.reminder_times),
        "notes": r.notes,
        "is_active": r.is_active,
        "end_date": r.end_date,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "today_status": today_status,
    }


def log_to_dict(log: DoseLogModel):
    return {
        "id": log.id,
        "reminder_id": log.reminder_id,
        "status": log.status,
        "snoozed_until": log.snoozed_until,
        "logged_at": log.logged_at.isoformat() if log.logged_at else None,
    }


# ─────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────

# CREATE REMINDER
@router.post("/", status_code=201)
def create_reminder(
    body: ReminderCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reminder = MedicineReminder(
        id=str(uuid.uuid4()),
        user_id=user.id,
        medicine_name=body.medicine_name,
        dosage=body.dosage,
        frequency=body.frequency,
        reminder_times=json.dumps(body.reminder_times),
        notes=body.notes,
        end_date=body.end_date,
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return {
        "id": reminder.id,
        "message": "Reminder created ✅"
    }


# GET ALL REMINDERS
@router.get("/")
def get_reminders(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reminders = (
        db.query(MedicineReminder)
        .filter(MedicineReminder.user_id == user.id)
        .order_by(MedicineReminder.created_at.desc())
        .all()
    )

    today_start = datetime.utcnow().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    result = []

    for r in reminders:
        log = (
            db.query(DoseLogModel)
            .filter(
                DoseLogModel.reminder_id == r.id,
                DoseLogModel.user_id == user.id,
                DoseLogModel.logged_at >= today_start,
            )
            .order_by(DoseLogModel.logged_at.desc())
            .first()
        )

        result.append(
            reminder_to_dict(
                r,
                today_status=log.status if log else None
            )
        )

    return result


# UPDATE REMINDER
@router.patch("/{rid}")
def update_reminder(
    rid: str,
    body: ReminderUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reminder = (
        db.query(MedicineReminder)
        .filter(
            MedicineReminder.id == rid,
            MedicineReminder.user_id == user.id
        )
        .first()
    )

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    if body.medicine_name is not None:
        reminder.medicine_name = body.medicine_name

    if body.dosage is not None:
        reminder.dosage = body.dosage

    if body.frequency is not None:
        reminder.frequency = body.frequency

    if body.notes is not None:
        reminder.notes = body.notes

    if body.is_active is not None:
        reminder.is_active = body.is_active

    if body.end_date is not None:
        reminder.end_date = body.end_date

    if body.reminder_times is not None:
        reminder.reminder_times = json.dumps(body.reminder_times)

    db.commit()

    return {"message": "Updated ✅"}


# DELETE REMINDER
@router.delete("/{rid}")
def delete_reminder(
    rid: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    reminder = (
        db.query(MedicineReminder)
        .filter(
            MedicineReminder.id == rid,
            MedicineReminder.user_id == user.id
        )
        .first()
    )

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    db.delete(reminder)
    db.commit()

    return {"message": "Deleted ✅"}


# LOG DOSE
@router.post("/log")
def log_dose(
    body: DoseLog,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    log = DoseLogModel(
        id=str(uuid.uuid4()),
        reminder_id=body.reminder_id,
        user_id=user.id,
        status=body.status,
        snoozed_until=body.snoozed_until,
    )

    db.add(log)
    db.commit()

    return {
        "id": log.id,
        "message": f"Logged as {body.status}"
    }


# DOSE HISTORY
@router.get("/history/{rid}")
def dose_history(
    rid: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = (
        db.query(DoseLogModel)
        .filter(
            DoseLogModel.reminder_id == rid,
            DoseLogModel.user_id == user.id
        )
        .order_by(DoseLogModel.logged_at.desc())
        .limit(30)
        .all()
    )

    return [log_to_dict(l) for l in logs]