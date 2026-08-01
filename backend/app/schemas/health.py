from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field

MedicationStatus = Literal["Taken", "Missed", "Pending"]

class MedicationStatusUpdate(BaseModel):
    status: MedicationStatus
    taken_at: Optional[datetime] = None

class MedicationLogResponse(BaseModel):
    id: int
    medicine_name: str
    scheduled_time: datetime
    status: MedicationStatus
    taken_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

class HealthDashboardResponse(BaseModel):
    health_score: int = Field(ge=0, le=100)
    adherence: float = Field(ge=0, le=100)
    risk_level: Literal["Low", "Medium", "High"]
    symptom_trends: dict
    medication_stats: dict
    weekly_summary: str
    ai_insights: list[str]
    recommendations: list[str]
