from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db  # ✅ NEW
from app.models.models import MedicineReminder, DoseLog, MedicationLog

import uuid
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler

router = APIRouter(
    tags=["Medicine Reminders"]
)

# ═══════════════════════════════════════════════════════════════
#                        COMPLETE FLOW
# ═══════════════════════════════════════════════════════════════
#
#   User creates reminder
#           ↓
#   medicine_reminders table
#
#   09:00 AM arrives
#           ↓
#   Scheduler detects due reminder
#           ↓
#   Create today's dose_log
#           ↓
#   Send notification
#           ↓
#   User clicks Taken
#           ↓
#   dose_logs updated
#
#   Next day
#           ↓
#   New dose_log created
#           ↓
#   Notification sent again
#
#   End date reached
#           ↓
#   Reminder ignored/deleted
#           ↓
#   No more notifications
#
# ═══════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────
# STEP 1: User creates reminder
#         → Stored in medicine_reminders table
# ─────────────────────────────────────────────

@router.post("/create")
def create_reminder(
    data: dict,
    db: Session = Depends(get_db)
):
    reminder_time = datetime.strptime(data["reminder_time"], "%H:%M").time()
    scheduled_at = datetime.combine(date.today(), reminder_time)
    reminder = MedicineReminder(
        user_id=data["user_id"],
        medicine_name=data["medicine_name"],
        dosage=data.get("dosage"),
        start_date=scheduled_at,
        end_date=datetime.strptime(data["continue_medicine_until"], "%Y-%m-%d"),
        is_active=True,
    )
    db.add(reminder)
    db.flush()
    # The first scheduled dose is a real persisted analytics record, not a
    # frontend-derived estimate. Future daily records are created by the job below.
    db.add(MedicationLog(user_id=reminder.user_id, reminder_id=str(reminder.id), medicine_name=reminder.medicine_name, scheduled_time=scheduled_at, status="Pending"))
    db.commit()
    db.refresh(reminder)

    return {
        "message": "Reminder created successfully",
        "data": {"id": reminder.id}
    }


# ─────────────────────────────────────────────
# STEP 2: Scheduler detects due reminder
#         → Creates today's dose_log
#         → Sends notification
# ─────────────────────────────────────────────

def check_and_create_dose_logs(db: Session):
    now = datetime.now()
    today = date.today()

    reminders = db.query(MedicineReminder).filter(MedicineReminder.is_active.is_(True), MedicineReminder.end_date >= datetime.combine(today, datetime.min.time())).all()

    for reminder in reminders:
        # Scheduler detects due reminder at reminder_time
        if reminder.start_date.hour == now.hour and reminder.start_date.minute == now.minute:

            # Check if dose_log already exists for today
            scheduled_at = datetime.combine(today, reminder.start_date.time())
            existing = db.query(MedicationLog).filter(MedicationLog.reminder_id == str(reminder.id), MedicationLog.scheduled_time == scheduled_at).first()

            if not existing:
                # Create today's dose_log
                dose_log = MedicationLog(
                    reminder_id=str(reminder.id),
                    user_id=reminder.user_id,
                    medicine_name=reminder.medicine_name,
                    scheduled_time=scheduled_at,
                    status="Pending"
                )
                db.add(dose_log)
                db.commit()

                # Send notification (push/email/SMS trigger here)
                send_notification(reminder.user_id, reminder.medicine_name, dose_log.id)


def send_notification(user_id: int, medicine_name: str, dose_log_id: str):
    # Integrate with Firebase / Twilio / Email service here
    print(f"[NOTIFICATION] User {user_id}: Time to take {medicine_name} | Log ID: {dose_log_id}")


# ─────────────────────────────────────────────
# STEP 3: User clicks "Taken"
#         → dose_logs updated
# ─────────────────────────────────────────────

@router.put("/dose/{dose_log_id}/taken")
def mark_dose_taken(
    dose_log_id: str,
    db: Session = Depends(get_db)
):
    dose_log = db.query(DoseLog).filter(
        DoseLog.id == dose_log_id
    ).first()

    if not dose_log:
        raise HTTPException(status_code=404, detail="Dose log not found")

    # dose_logs updated
    dose_log.status = "Taken"
    dose_log.taken_at = datetime.now()

    db.commit()
    db.refresh(dose_log)

    return {
        "message": "Dose marked as taken",
        "dose_log_id": dose_log_id,
        "status": dose_log.status
    }


# ─────────────────────────────────────────────
# STEP 4: Next day → New dose_log created
#                  → Notification sent again
#         (Handled automatically by scheduler)
# ─────────────────────────────────────────────

# Scheduler runs check_and_create_dose_logs() every minute
# On each new day, a fresh dose_log is created per active reminder
# Notification is sent again automatically

def start_scheduler(db_session_factory):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=lambda: check_and_create_dose_logs(db_session_factory()),
        trigger="interval",
        minutes=1,
        id="dose_log_scheduler"
    )
    scheduler.start()
    return scheduler


# ─────────────────────────────────────────────
# STEP 5: End date reached
#         → Reminder ignored/deleted
#         → No more notifications
# ─────────────────────────────────────────────

def deactivate_expired_reminders(db: Session):
    today = date.today()
    expired = db.query(MedicineReminder).filter(
        MedicineReminder.continue_medicine_until < today,
        MedicineReminder.status == "Active"
    ).all()

    for reminder in expired:
        # Reminder ignored/deleted → no more notifications
        reminder.status = "Expired"

    db.commit()
    print(f"[SCHEDULER] {len(expired)} reminder(s) marked as Expired.")


# ─────────────────────────────────────────────
# GET REMINDERS
# ─────────────────────────────────────────────

@router.get("/{user_id}")
def get_reminders(
    user_id: int,
    db: Session = Depends(get_db)
):
    reminders = db.query(MedicineReminder).filter(
        MedicineReminder.user_id == user_id
    ).all()
    return reminders


# ─────────────────────────────────────────────
# GET DOSE LOGS FOR USER
# ─────────────────────────────────────────────

@router.get("/{user_id}/dose-logs")
def get_dose_logs(
    user_id: int,
    db: Session = Depends(get_db)
):
    logs = db.query(DoseLog).filter(
        DoseLog.user_id == user_id
    ).order_by(DoseLog.scheduled_date.desc()).all()
    return logs


# ─────────────────────────────────────────────
# DELETE REMINDER
# ─────────────────────────────────────────────

@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: str,
    db: Session = Depends(get_db)
):
    reminder = db.query(MedicineReminder).filter(
        MedicineReminder.id == reminder_id
    ).first()

    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    db.delete(reminder)
    db.commit()

    return {"message": "Reminder deleted"}
