# app/routes/conversation.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db  # ✅ NEW
from app.services.ai_post_report_service import generate_post_report_answer
from app.services.ai_followup_service import generate_ai_followup
from app.services.ai_severity_service import analyze_severity
from app.services.ai_report_service import generate_ai_report, extract_symptoms_data
from app.services.ai_memory_service import (
    create_conversation,
    save_message,
    get_conversation_messages
)
from fastapi.responses import FileResponse
import os
from app.services.pdf_service import generate_pdf_report
from app.services.hospital_service import (
    get_nearby_hospitals,
    create_specialty_maps_search_link,
    get_recommended_specialty,
)
from app.models.models import Conversation, MedicationLog, Report, SymptomHistory
import uuid
from app.services.symptom_lifecycle_service import apply_resolution_message, record_active_episode
from app.services.intent_router import route_intent
from app.services.health_insights_service import calculate_dashboard, mark_overdue_medication_logs
from app.rag.rag_service import rag_service
from app.services.ai_decision_service import LLMDecisionUnavailable

router = APIRouter()

# ─────────────────────────────────────────────
# REQUEST MODEL
# ─────────────────────────────────────────────

class ConversationRequest(BaseModel):
    user_id: int
    message: str
    conversation_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class IntentRouteRequest(BaseModel):
    message: str
    symptom_workflow_active: bool = False
    report_context_active: bool = False


@router.post("/intent/route")
def intent_route(request: IntentRouteRequest):
    """Classify a message without invoking any downstream workflow."""
    return route_intent(
        request.message,
        symptom_workflow_active=request.symptom_workflow_active,
        report_context_active=request.report_context_active,
    )


def _workflow_response(db: Session, request: ConversationRequest, conversation_id: int, intent_result: dict) -> dict:
    """Invoke exactly one non-symptom workflow and return the shared chat shape."""
    intent = intent_result["intent"]
    if intent == "KNOWLEDGE":
        response = rag_service.answer(request.message)["answer"]
    elif intent == "MEDICATION":
        mark_overdue_medication_logs(db)
        logs = db.query(MedicationLog).filter(MedicationLog.user_id == request.user_id).all()
        taken = sum(log.status == "Taken" for log in logs)
        missed = sum(log.status == "Missed" for log in logs)
        pending = sum(log.status == "Pending" for log in logs)
        response = f"Your medication record has {taken} taken, {missed} missed, and {pending} pending dose(s). Manage reminders in Medication Tracker."
    elif intent == "ANALYTICS":
        analytics = calculate_dashboard(db, request.user_id)
        response = f"Your live health score is {analytics['health_score']}/100. Medication adherence is {analytics['adherence']}%, symptom trend is {analytics['severity_trend'].lower()}, and risk level is {analytics['risk_level']}."
    elif intent == "REPORT":
        report = db.query(Report).filter(Report.user_id == request.user_id).order_by(Report.created_at.desc()).first()
        response = (f"Your latest report, {report.title or 'Medical report'}, says: {(report.content or 'No extracted text is available.')[:800]}" if report else "Please upload a medical report (PDF or image) so I can analyse it or answer questions about it.")
    else:
        response = "Hello! I can help with symptoms, reports, medication reminders, and health analytics."

    save_message(db=db, conversation_id=conversation_id, role="assistant", content=response)
    return {
        "success": True, "conversation_id": conversation_id, "response": response,
        "severity": None, "severity_reason": None, "report_ready": False,
        "report": None, "pdf_url": None, "hospitals": [], "followup_options": [],
        "intent_router": intent_result,
    }

# ─────────────────────────────────────────────
# AI CONVERSATION ROUTE
# ─────────────────────────────────────────────

@router.post("/chat")
def ai_chat(
    request: ConversationRequest,
    db: Session = Depends(get_db)
):
    try:
        # ─────────────────────────
        # STEP 1: CREATE CONVERSATION (if new)
        # ─────────────────────────
        
        if not request.conversation_id:
            conversation = create_conversation(
                db=db,
                user_id=request.user_id,
                title="Healthcare Conversation"
            )
            conversation_id = conversation.id
        else:
            conversation_id = request.conversation_id

        # ─────────────────────────
        # STEP 2: SAVE USER MESSAGE
        # ─────────────────────────
        
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )

        # Route before any health workflow runs. Only SYMPTOM may continue into
        # the follow-up/report-generation path below.
        current_conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        symptom_active = db.query(SymptomHistory).filter(
            SymptomHistory.user_id == request.user_id,
            SymptomHistory.status == "Active",
        ).first() is not None
        intent_result = route_intent(
            request.message,
            symptom_workflow_active=symptom_active,
            report_context_active=bool(current_conversation and current_conversation.report_generated),
        )
        # A report-context route must reach the post-report Q&A handler below.
        # Otherwise general questions asked after an assessment only return the
        # raw report text instead of an answer to the user's question.
        is_post_report_question = bool(
            current_conversation
            and current_conversation.report_generated
            and intent_result["intent"] == "REPORT"
        )
        if intent_result["intent"] != "SYMPTOM" and not is_post_report_question:
            return _workflow_response(db, request, conversation_id, intent_result)

        lifecycle = apply_resolution_message(db, request.user_id, request.message)
        if lifecycle["action"] == "confirm":
            names = ", ".join(lifecycle["symptoms"])
            return {"success": True, "conversation_id": conversation_id, "response": f"Are your active symptom(s) ({names}) completely gone, or only improving?", "severity": None, "severity_reason": None, "report_ready": False, "report": None, "pdf_url": None, "hospitals": [], "followup_options": ["Completely gone", "Still present"], "intent_router": intent_result}

        # ─────────────────────────
        # STEP 3: LOAD CONVERSATION HISTORY
        # ─────────────────────────
        
        conversation_history = get_conversation_messages(
            db=db,
            conversation_id=conversation_id
        )

        # Get conversation object for checking report status
        conversation = db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

        # ─────────────────────────
        # STEP 4: CHECK IF REPORT ALREADY GENERATED
        # ─────────────────────────
        
        if conversation and conversation.report_generated:
            # POST REPORT Q&A - Return report without follow-ups
            followup_result = generate_post_report_answer(
                user_input=request.message,
                conversation_history=conversation_history
            )
            
            ai_response = followup_result.get("response", "No response received.")
            
            save_message(
                db=db,
                conversation_id=conversation_id,
                role="assistant",
                content=ai_response
            )
            
            return {
                "success": True,
                "conversation_id": conversation_id,
                "response": ai_response,
                "severity": None,
                "severity_reason": None,
                "report_ready": True,
                "report": None,
                "pdf_url": None,
                "hospitals": [],
                "followup_options": [],  # Empty - no follow-ups after report
                "intent_router": intent_result,
            }

        # ─────────────────────────
        # STEP 5: AI FOLLOW-UP ENGINE
        # ─────────────────────────
        
        followup_result = generate_ai_followup(
            user_input=request.message,
            conversation_history=conversation_history
        )
        
        ai_response = followup_result.get("response", "No response received.")
        report_ready = followup_result.get("report_ready", False)
        followup_options = followup_result.get("followup_options", [])

        # Save AI message
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response
        )

        # ─────────────────────────
        # STEP 6: CHECK IF ENOUGH INFORMATION
        # ─────────────────────────
        
        if not report_ready:
            # Return follow-up response with options
            return {
                "success": True,
                "conversation_id": conversation_id,
                "response": ai_response,
                "severity": None,
                "severity_reason": None,
                "report_ready": False,
                "report": None,
                "pdf_url": None,
                "hospitals": [],
                "followup_options": followup_options,  # Show options only before report
                "intent_router": intent_result,
            }

        # ─────────────────────────
        # STEP 7: ENOUGH INFORMATION - GENERATE REPORT
        # ─────────────────────────
        
        print("ENOUGH INFORMATION - Generating Report")
        
        # Mark report as generated
        if conversation:
            conversation.report_generated = True
            db.commit()

        # ─────────────────────────
        # STEP 7A: SEVERITY ANALYSIS
        # ─────────────────────────
        
        print("Analyzing Severity...")
        severity_result = analyze_severity(conversation_history)
        severity = severity_result.get("severity", "MODERATE")
        severity_reason = severity_result.get("reason", "Unable to analyze severity")
        recommended_specialty = severity_result.get("specialty", "General Medicine")

        # Store the structured result from the completed AI health chat. Analytics
        # read this persisted history; they never infer symptoms from chat text.
        extracted = extract_symptoms_data(conversation_history)
        symptom = extracted.get("primary_symptom")
        if symptom and symptom != "Not specified":
            record_active_episode(db, request.user_id, symptom, severity.title(), extracted.get("duration"), severity_reason)

        # ─────────────────────────
        # STEP 7B: NEARBY HOSPITALS
        # ─────────────────────────
        
        print("Finding Nearby Hospitals...")
        hospitals = []
        symptom_summary = extract_symptoms_data(conversation_history).get("primary_symptom", "")
        google_maps_link = (
            "https://www.google.com/maps/search/"
            f"{recommended_specialty.replace(' ', '+')}+hospital"
        )
        
        if request.latitude and request.longitude:
            hospitals = get_nearby_hospitals(
                latitude=request.latitude,
                longitude=request.longitude,
                symptoms=symptom_summary,
                specialty=recommended_specialty,
            )
            google_maps_link = create_specialty_maps_search_link(
                request.latitude,
                request.longitude,
                recommended_specialty,
            )

        # ─────────────────────────
        # STEP 7C: GENERATE REPORT
        # ─────────────────────────
        
        print("Generating Medical Report...")
        report_text = generate_ai_report(
            conversation_history=conversation_history,
            severity=severity,
            hospitals=hospitals,
            google_maps_link=google_maps_link
        )

        # Keep AI-generated assessment reports in the same report history as
        # uploaded reports, including their original timestamp and severity.
        db.add(Report(
            id=str(uuid.uuid4()), user_id=request.user_id,
            title="AI Health Assessment", content=f"Severity: {severity}\n\n{report_text}",
        ))
        db.commit()

        # Persist the report itself, not only the short status reply. This lets users
        # see the assessment again when they reopen the conversation.
        save_message(
            db=db,
            conversation_id=conversation_id,
            role="assistant",
            content=report_text
        )

        # ─────────────────────────
        # STEP 7D: GENERATE PDF/TEXT REPORT
        # ─────────────────────────
        
        print("Generating Report File...")
        pdf_result = generate_pdf_report(report_text)
        
        pdf_url = None
        if pdf_result.get("success"):
            # Update to use .txt extension since we're not using PDF
            filename = pdf_result['filename']
            pdf_url = f"/reports/{filename}"

        # ─────────────────────────
        # STEP 8: RETURN RESPONSE WITH REPORT (NO FOLLOW-UPS)
        # ─────────────────────────
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "response": "Here is your complete health assessment report.",
            "severity": severity,
            "severity_reason": severity_reason,
            "report_ready": True,
            "report": report_text,
            "pdf_url": pdf_url,
            "hospitals": hospitals,
            "google_maps_link": google_maps_link,
            "followup_options": [],  # Empty - no follow-ups after report
            "intent_router": intent_result,
        }

    except LLMDecisionUnavailable as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        print("Conversation Route Error:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ─────────────────────────────────────────────
# REPORT DOWNLOAD ROUTE
# ─────────────────────────────────────────────

@router.get("/reports/{filename}")
def download_report(filename: str):
    try:
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        filepath = os.path.join("reports", filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Determine media type based on file extension
        media_type = "text/plain" if filename.endswith('.txt') else "application/pdf"
        
        return FileResponse(
            filepath,
            media_type=media_type,
            filename=filename
        )
    except Exception as e:
        print(f"Report Download Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
