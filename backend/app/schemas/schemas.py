from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


# ──────────────────────────────────────────────
#  AUTH
# ──────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_name: str
    user_email: str


# ──────────────────────────────────────────────
#  SYMPTOM
# ──────────────────────────────────────────────

class SymptomRequest(BaseModel):
    symptom: str

class AnalysisResponse(BaseModel):
    analysis: str
    severity: str
    remedies: List[str] = []
    when_to_see_doctor: str = ""
    is_emergency: bool = False
    history_id: Optional[int] = None


# ──────────────────────────────────────────────
#  SYMPTOM HISTORY
# ──────────────────────────────────────────────

class HistoryItem(BaseModel):
    id: int
    symptom: str
    analysis: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True


# ──────────────────────────────────────────────
#  MEDICINE REMINDERS
# ──────────────────────────────────────────────

class MedicineReminderCreate(BaseModel):
    medicine_name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reminder_times: Optional[List[str]] = []   # ["08:00", "20:00"]
    notes: Optional[str] = None
    end_date: Optional[datetime] = None

class MedicineReminderUpdate(BaseModel):
    medicine_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    reminder_times: Optional[List[str]] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    end_date: Optional[datetime] = None

class MedicineReminderResponse(BaseModel):
    id: int
    user_id: int
    medicine_name: str
    dosage: Optional[str]
    frequency: Optional[str]
    reminder_times: Optional[List[str]]
    notes: Optional[str]
    is_active: bool
    end_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True