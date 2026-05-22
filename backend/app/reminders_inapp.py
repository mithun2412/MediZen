"""
MediVoice — Medicine Reminder (In-App Only)
Pure CRUD + dose logging.
Frontend handles notifications.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import uuid
import json

from app.database import get_db
from app.services.auth_service import get_current_user

from app.models.models import (
    MedicineReminder,
    DoseLog
)

router = APIRouter(
    prefix="/reminders",
    tags=["reminders"]
)

# ─────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────

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


class DoseLogRequest(BaseModel):

    reminder_id: str
    status: str
    snoozed_until: Optional[str] = None


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def reminder_to_dict(
    reminder: MedicineReminder,
    today_status=None
):

    return {

        "id": reminder.id,

        "medicine_name":
            reminder.medicine_name,

        "dosage":
            reminder.dosage,

        "frequency":
            reminder.frequency,

        "reminder_times":
            json.loads(reminder.reminder_times),

        "notes":
            reminder.notes,

        "is_active":
            reminder.is_active,

        "end_date":
            reminder.end_date,

        "created_at":
            reminder.created_at.isoformat()
            if reminder.created_at else None,

        "today_status":
            today_status
    }


def log_to_dict(log: DoseLog):

    return {

        "id": log.id,

        "reminder_id":
            log.reminder_id,

        "status":
            log.status,

        "snoozed_until":
            log.snoozed_until,

        "logged_at":
            log.logged_at.isoformat()
            if log.logged_at else None
    }


# ─────────────────────────────────────────────
# CREATE REMINDER
# ─────────────────────────────────────────────

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

        reminder_times=json.dumps(
            body.reminder_times
        ),

        notes=body.notes,

        end_date=body.end_date
    )

    db.add(reminder)

    db.commit()

    db.refresh(reminder)

    return {

        "id": reminder.id,

        "message":
            "Reminder created ✅"
    }


# ─────────────────────────────────────────────
# GET REMINDERS
# ─────────────────────────────────────────────

@router.get("/")
def get_reminders(

    user=Depends(get_current_user),

    db: Session = Depends(get_db),
):

    reminders = (

        db.query(MedicineReminder)

        .filter(
            MedicineReminder.user_id == user.id
        )

        .order_by(
            MedicineReminder.created_at.desc()
        )

        .all()
    )

    today_start = datetime.utcnow().replace(

        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    result = []

    for reminder in reminders:

        latest_log = (

            db.query(DoseLog)

            .filter(

                DoseLog.reminder_id == reminder.id,

                DoseLog.user_id == user.id,

                DoseLog.logged_at >= today_start
            )

            .order_by(
                DoseLog.logged_at.desc()
            )

            .first()
        )

        result.append(

            reminder_to_dict(

                reminder,

                today_status=(
                    latest_log.status
                    if latest_log else None
                )
            )
        )

    return result


# ─────────────────────────────────────────────
# UPDATE REMINDER
# ─────────────────────────────────────────────

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

        raise HTTPException(

            status_code=404,

            detail="Reminder not found"
        )

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

        reminder.reminder_times = json.dumps(
            body.reminder_times
        )

    db.commit()

    return {

        "message":
            "Updated ✅"
    }


# ─────────────────────────────────────────────
# DELETE REMINDER
# ─────────────────────────────────────────────

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

        raise HTTPException(

            status_code=404,

            detail="Reminder not found"
        )

    db.delete(reminder)

    db.commit()

    return {

        "message":
            "Deleted ✅"
    }


# ─────────────────────────────────────────────
# LOG DOSE
# ─────────────────────────────────────────────

@router.post("/log")
def log_dose(

    body: DoseLogRequest,

    user=Depends(get_current_user),

    db: Session = Depends(get_db),
):

    log = DoseLog(

        reminder_id=body.reminder_id,

        user_id=user.id,

        status=body.status,

        snoozed_until=body.snoozed_until
    )

    db.add(log)

    db.commit()

    db.refresh(log)

    return {

        "id": log.id,

        "message":
            f"Logged as {body.status}"
    }


# ─────────────────────────────────────────────
# DOSE HISTORY
# ─────────────────────────────────────────────

@router.get("/history/{rid}")
def dose_history(

    rid: str,

    user=Depends(get_current_user),

    db: Session = Depends(get_db),
):

    logs = (

        db.query(DoseLog)

        .filter(

            DoseLog.reminder_id == rid,

            DoseLog.user_id == user.id
        )

        .order_by(
            DoseLog.logged_at.desc()
        )

        .limit(30)

        .all()
    )

    return [

        log_to_dict(log)

        for log in logs
    ]