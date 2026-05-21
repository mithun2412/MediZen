from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# ---- Auth Schemas ----

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

# ---- Symptom Schemas ----

class SymptomRequest(BaseModel):
    symptom: str

class AnalysisResponse(BaseModel):
    analysis: str
    severity: str
    remedies: List[str] = []
    when_to_see_doctor: str = ""
    is_emergency: bool = False
    history_id: Optional[int] = None

# ---- History Schemas ----

class HistoryItem(BaseModel):
    id: int
    symptom: str
    analysis: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True