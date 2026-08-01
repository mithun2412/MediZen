"""Persistence rules for active and resolved symptom episodes."""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import SymptomHistory

RESOLVED_WORDS = ("is gone", "has gone", "pain has stopped", "pain stopped", "i recovered", "have recovered", "fully recovered", "no longer have")
UNCERTAIN_WORDS = ("feeling better", "feel better", "has reduced", "is reduced", "improving", "improved")

def _normal(value): return " ".join((value or "").lower().split())

def record_active_episode(db: Session, user_id: int, symptom: str, severity: str | None, duration: str | None = None, notes: str | None = None):
    """Create only a new episode; an existing active episode is never duplicated."""
    symptom = symptom.strip()
    active = db.query(SymptomHistory).filter(SymptomHistory.user_id == user_id, SymptomHistory.status == "Active").all()
    existing = next((item for item in active if _normal(item.symptom) == _normal(symptom)), None)
    if existing:
        existing.severity, existing.duration, existing.notes = severity or existing.severity, duration or existing.duration, notes or existing.notes
        db.commit(); return existing, False
    item = SymptomHistory(user_id=user_id, symptom=symptom, severity=severity, duration=duration, notes=notes, status="Active", started_at=datetime.utcnow())
    db.add(item); db.commit(); db.refresh(item)
    return item, True

def apply_resolution_message(db: Session, user_id: int, message: str):
    """Resolve only clear statements. Ambiguous improvement requests confirmation."""
    text = _normal(message)
    active = db.query(SymptomHistory).filter(SymptomHistory.user_id == user_id, SymptomHistory.status == "Active").order_by(SymptomHistory.started_at.desc()).all()
    if not active: return {"action": "none"}
    if any(word in text for word in RESOLVED_WORDS):
        matched = next((item for item in active if _normal(item.symptom) in text), active[0] if len(active) == 1 else None)
        if matched:
            matched.status, matched.resolved_at = "Resolved", datetime.utcnow()
            db.commit()
            return {"action": "resolved", "symptom": matched.symptom}
    if any(word in text for word in UNCERTAIN_WORDS):
        return {"action": "confirm", "symptoms": [item.symptom for item in active]}
    return {"action": "none"}
