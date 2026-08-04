from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import MedicationLog, Report, SymptomHistory, User
from app.schemas.health import MedicationStatusUpdate
from app.services.health_insights_service import calculate_dashboard, mark_overdue_medication_logs

analytics_router = APIRouter(prefix="/analytics", tags=["Health Analytics"])
medications_router = APIRouter(prefix="/medications", tags=["Medication Tracker"])
reports_router = APIRouter(prefix="/reports", tags=["Report History"])

@analytics_router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    mark_overdue_medication_logs(db)
    db.commit()
    return calculate_dashboard(db, user.id)

@analytics_router.get("/symptoms")
def symptoms(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = calculate_dashboard(db, user.id)
    return {key: data[key] for key in ("symptom_frequency", "symptom_recurrence", "most_frequent_symptoms", "severity_trend")}


@analytics_router.patch("/symptoms/{symptom_id}/resolve")
def resolve_symptom(symptom_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Let a user explicitly mark one active symptom episode as recovered."""
    symptom = db.query(SymptomHistory).filter(
        SymptomHistory.id == symptom_id,
        SymptomHistory.user_id == user.id,
    ).first()
    if not symptom:
        raise HTTPException(status_code=404, detail="Symptom record not found")
    if symptom.status != "Active":
        raise HTTPException(status_code=409, detail="This symptom is already resolved")
    symptom.status = "Resolved"
    symptom.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(symptom)
    return symptom

@analytics_router.get("/adherence")
def adherence(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return calculate_dashboard(db, user.id)["medication_statistics"]

@analytics_router.get("/health-score")
def health_score(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = calculate_dashboard(db, user.id)
    return {key: data[key] for key in ("health_score", "risk_level", "weekly_summary", "monthly_summary")}

@analytics_router.get("/recovery")
def recovery(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = calculate_dashboard(db, user.id)
    return {"severity_trend": data["severity_trend"], "recovery_trend": data["recovery_trend"], "risk_level": data["risk_level"]}

@analytics_router.get("/weekly")
def weekly(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return calculate_dashboard(db, user.id)["weekly_summary"]

@analytics_router.get("/monthly")
def monthly(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return calculate_dashboard(db, user.id)["monthly_summary"]

@medications_router.get("/today")
def medication_today(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Refresh here too, so users do not have to wait for the next scheduler run.
    mark_overdue_medication_logs(db)
    today = datetime.now().date()
    return db.query(MedicationLog).filter(MedicationLog.user_id == user.id, MedicationLog.scheduled_time >= datetime.combine(today, datetime.min.time()), MedicationLog.scheduled_time < datetime.combine(today, datetime.max.time())).order_by(MedicationLog.scheduled_time).all()

@medications_router.get("/history")
def medication_history(limit: int = Query(100, le=365), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(MedicationLog).filter(MedicationLog.user_id == user.id).order_by(MedicationLog.scheduled_time.desc()).limit(limit).all()

@medications_router.patch("/{log_id}/status")
def update_medication_status(log_id: int, body: MedicationStatusUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    log = db.query(MedicationLog).filter(MedicationLog.id == log_id, MedicationLog.user_id == user.id).first()
    if not log: raise HTTPException(status_code=404, detail="Medication log not found")
    log.status = body.status
    log.taken_at = body.taken_at or (datetime.utcnow() if body.status == "Taken" else None)
    db.commit(); db.refresh(log)
    return log

@medications_router.get("/statistics")
def medication_statistics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return calculate_dashboard(db, user.id)["medication_statistics"]

@reports_router.get("/history")
def report_history(query: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    records = db.query(Report).filter(Report.user_id == user.id).order_by(Report.created_at.desc())
    if query: records = records.filter(Report.title.ilike(f"%{query}%"))
    return records.all()

@reports_router.get("/search")
def search_reports(q: str = Query(min_length=1), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return report_history(q, db, user)

@reports_router.get("/{report_id}")
def report_detail(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.query(Report).filter(Report.id == report_id, Report.user_id == user.id).first()
    if not record: raise HTTPException(status_code=404, detail="Report not found")
    return record

@reports_router.delete("/{report_id}")
def delete_report(report_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    record = db.query(Report).filter(Report.id == report_id, Report.user_id == user.id).first()
    if not record: raise HTTPException(status_code=404, detail="Report not found")
    db.delete(record); db.commit(); return {"deleted": True}
