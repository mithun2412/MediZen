from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from app.services.auth_service import get_current_user
from app.services.ai_service import generate_followup_question, check_emergency

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class FollowUpRequest(BaseModel):
    symptoms: str
    conversation: List[Message] = []

class FollowUpResponse(BaseModel):
    is_done: bool
    question: Optional[str] = None
    final_analysis: Optional[dict] = None
    is_emergency: bool = False

@router.post("/symptom/followup", response_model=FollowUpResponse)
async def symptom_followup(req: FollowUpRequest, user=Depends(get_current_user)):
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty")

    is_emergency = check_emergency(req.symptoms)
    conversation_dicts = [{"role": m.role, "content": m.content} for m in req.conversation]
    result = generate_followup_question(req.symptoms, conversation_dicts)

    return FollowUpResponse(
        is_done=result["is_done"],
        question=result.get("question"),
        final_analysis=result.get("final_analysis"),
        is_emergency=is_emergency or (result.get("final_analysis") or {}).get("is_emergency", False)
    )