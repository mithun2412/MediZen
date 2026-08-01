from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import SymptomHistory

def save_health_record(
    db: Session,
    user_id: int,
    symptom: str,
    analysis: str,
    severity: str
) -> Dict[str, Any]:
    """
    Save a health record to the database
    """
    try:
        # Create new symptom history record
        health_record = SymptomHistory(
            user_id=user_id,
            symptom=symptom,
            # SymptomHistory stores the narrative in notes; `analysis` was a
            # stale field name and caused history reads to fail.
            notes=analysis,
            severity=severity,
            created_at=datetime.utcnow()
        )
        
        db.add(health_record)
        db.commit()
        db.refresh(health_record)
        
        return {
            "success": True,
            "message": "Health record saved successfully",
            "record_id": health_record.id,
            "record": {
                "id": health_record.id,
                "symptom": health_record.symptom,
                "analysis": health_record.notes,
                "severity": health_record.severity,
                "created_at": health_record.created_at.isoformat()
            }
        }
        
    except Exception as e:
        db.rollback()
        print(f"Save health record error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to save health record"
        }

def get_user_health_history(
    db: Session,
    user_id: int,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get health history for a user
    """
    try:
        # Get all symptom history for the user
        records = db.query(SymptomHistory).filter(
            SymptomHistory.user_id == user_id
        ).order_by(
            SymptomHistory.created_at.desc()
        ).limit(limit).all()
        
        history = []
        for record in records:
            history.append({
                "id": record.id,
                "symptom": record.symptom,
                "analysis": record.notes,
                "severity": record.severity,
                "created_at": record.created_at.isoformat() if record.created_at else None
            })
        
        return {
            "success": True,
            "user_id": user_id,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        print(f"Get user health history error: {e}")
        return {
            "success": False,
            "error": str(e),
            "history": []
        }

def delete_health_record(
    db: Session,
    record_id: int
) -> Dict[str, Any]:
    """
    Delete a health record by ID
    """
    try:
        # Find the record
        record = db.query(SymptomHistory).filter(
            SymptomHistory.id == record_id
        ).first()
        
        if not record:
            return {
                "success": False,
                "error": "Record not found",
                "message": "No record found with the given ID"
            }
        
        # Delete the record
        db.delete(record)
        db.commit()
        
        return {
            "success": True,
            "message": "Health record deleted successfully",
            "record_id": record_id
        }
        
    except Exception as e:
        db.rollback()
        print(f"Delete health record error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to delete health record"
        }

def get_health_record_by_id(
    db: Session,
    record_id: int
) -> Dict[str, Any]:
    """
    Get a single health record by ID
    """
    try:
        record = db.query(SymptomHistory).filter(
            SymptomHistory.id == record_id
        ).first()
        
        if not record:
            return {
                "success": False,
                "error": "Record not found"
            }
        
        return {
            "success": True,
            "record": {
                "id": record.id,
                "user_id": record.user_id,
                "symptom": record.symptom,
                "analysis": record.notes,
                "severity": record.severity,
                "created_at": record.created_at.isoformat() if record.created_at else None
            }
        }
        
    except Exception as e:
        print(f"Get health record error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
