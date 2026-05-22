
from fastapi import APIRouter
from pydantic import BaseModel

from app.ml.disease_predictor import (
    predict_disease
)

router = APIRouter(
    prefix="/predict-disease",
    tags=["Disease Prediction"]
)


# ─────────────────────────────────────────────
# REQUEST MODEL
# ─────────────────────────────────────────────

class DiseasePredictionRequest(BaseModel):

    fever: int = 0
    cough: int = 0
    fatigue: int = 0
    headache: int = 0
    chest_pain: int = 0
    breathing_issue: int = 0
    stress: int = 0
    sleep_issue: int = 0
    age: int = 25


# ─────────────────────────────────────────────
# PREDICTION ROUTE
# ─────────────────────────────────────────────

@router.post("/")
def disease_prediction(

    body: DiseasePredictionRequest
):

    result = predict_disease(

        body.dict()
    )

    return {

        "success": True,

        "prediction": result
    }