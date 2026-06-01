from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.database import get_db

from app.models.models import MedicineReminder


import uuid

from datetime import datetime, time

router = APIRouter(

    prefix="/reminders",

    tags=["Medicine Reminders"]
)


# ─────────────────────────────────────────────
# CREATE REMINDER
# ─────────────────────────────────────────────

@router.post("/create")
def create_reminder(

    data: dict,

    db: Session = Depends(get_db)
):

    reminder = MedicineReminder(

        id=str(uuid.uuid4()),

        user_id=data["user_id"],

        medicine_name=data["medicine_name"],

        dosage=data["dosage"],

        reminder_time=datetime.strptime(
            data["reminder_time"],
            "%H:%M"
        ).time(),

        end_date=datetime.strptime(
            data["end_date"],
            "%Y-%m-%d"
        ).date(),

        status="Pending"
    )

    db.add(reminder)

    db.commit()

    db.refresh(reminder)

    return {

        "message":
        "Reminder created successfully",

        "data": {

            "id": reminder.id
        }
    }
# ─────────────────────────────────────────────
# GET REMINDERS
# ─────────────────────────────────────────────

@router.get("/{user_id}")
def get_reminders(

    user_id: int,

    db: Session = Depends(get_db)
):

    reminders = db.query(
        MedicineReminder
    ).filter(

        MedicineReminder.user_id == user_id

    ).all()

    return reminders


# ─────────────────────────────────────────────
# UPDATE STATUS
# ─────────────────────────────────────────────

@router.put("/status/{reminder_id}")
def update_status(

    reminder_id: str,

    data: dict,

    db: Session = Depends(get_db)
):

    reminder = db.query(
        MedicineReminder
    ).filter(

        MedicineReminder.id == reminder_id

    ).first()

    if not reminder:

        raise HTTPException(

            status_code=404,

            detail="Reminder not found"
        )

    reminder.status = data["status"]

    db.commit()

    db.refresh(reminder)

    return {

        "message":
        "Status updated",

        "status":
        reminder.status
    }


# ─────────────────────────────────────────────
# DELETE REMINDER
# ─────────────────────────────────────────────

@router.delete("/{reminder_id}")
def delete_reminder(

    reminder_id: str,

    db: Session = Depends(get_db)
):

    reminder = db.query(
        MedicineReminder
    ).filter(

        MedicineReminder.id == reminder_id

    ).first()

    if not reminder:

        raise HTTPException(

            status_code=404,

            detail="Reminder not found"
        )

    db.delete(reminder)

    db.commit()

    return {

        "message":
        "Reminder deleted"
    }