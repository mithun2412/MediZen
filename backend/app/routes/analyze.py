from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import SymptomHistory, User
from app.schemas.schemas import AnalysisResponse, SymptomRequest
from app.services.ai_service import analyze_symptoms
from app.services.auth_service import get_current_user

router = APIRouter(tags=["analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze(
    request: SymptomRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not request.symptom.strip():
        raise HTTPException(status_code=400, detail="Symptom cannot be empty.")

    try:
        result = analyze_symptoms(request.symptom)

        entry = SymptomHistory(
            user_id=current_user.id,
            symptom=request.symptom,       # ✅ fixed: was "symptoms"
            analysis=result["analysis"],
            severity=result["severity"]
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)

        return AnalysisResponse(
            analysis=result["analysis"],
            severity=result["severity"]
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    records = (
        db.query(SymptomHistory)
        .filter(SymptomHistory.user_id == current_user.id)
        .order_by(SymptomHistory.created_at.desc())
        .all()
    )
    return records


@router.delete("/history/{entry_id}")
def delete_history(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = db.query(SymptomHistory).filter(
        SymptomHistory.id == entry_id,
        SymptomHistory.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Deleted"}