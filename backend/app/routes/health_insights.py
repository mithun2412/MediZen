from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.services.auth_service import (
    get_current_user
)

from app.ml.health_score import (
    calculate_health_score
)

from app.medical.symptom_analytics import (

    get_recurring_symptoms,

    get_symptom_frequency,

    get_stress_trend,

    get_medicine_adherence,

    generate_health_insights
)

router = APIRouter(
    prefix="/health-insights",
    tags=["Health Insights"]
)


# ─────────────────────────────────────────────
# HEALTH OVERVIEW
# ─────────────────────────────────────────────
@router.get("/")
def health_overview(

    db: Session = Depends(get_db),

    user=Depends(get_current_user)
):

    health_score_data = calculate_health_score(
        db,
        user.id
    )

    recurring = get_recurring_symptoms(
        db,
        user.id
    )

    symptom_frequency = get_symptom_frequency(
        db,
        user.id
    )

    stress = get_stress_trend(
        db,
        user.id
    )

    adherence = get_medicine_adherence(
        db,
        user.id
    )

    insights = generate_health_insights(
        db,
        user.id
    )

    return {

        "health_score": health_score_data,

        "recurring_symptoms": recurring,

        "symptom_frequency": symptom_frequency,

        "stress_trend": stress,

        "medicine_adherence": adherence,

        "insights": insights
    }