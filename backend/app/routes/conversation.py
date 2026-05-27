from fastapi import (

    APIRouter,

    Depends,

    HTTPException
)

from sqlalchemy.orm import Session

from pydantic import BaseModel

from typing import Optional

from app.database import get_db

from app.services.ai_conversation_service import (
    generate_ai_response
)

from app.services.ai_followup_service import (
    generate_ai_followup
)

from app.services.ai_severity_service import (
    analyze_severity
)

from app.services.ai_report_service import (
    generate_ai_report
)

from app.services.ai_memory_service import (

    create_conversation,

    save_message,

    get_conversation_messages
)

from app.services.pdf_service import (
    generate_pdf_report
)

from app.services.hospital_service import (
    get_nearby_hospitals
)

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
        # CREATE CONVERSATION
        # ─────────────────────────

        if not request.conversation_id:

            conversation = create_conversation(

                db=db,

                user_id=request.user_id,

                title="Healthcare Conversation"
            )

            conversation_id = conversation.id

        else:

            conversation_id = (
                request.conversation_id
            )

        # ─────────────────────────
        # SAVE USER MESSAGE
        # ─────────────────────────

        save_message(

            db=db,

            conversation_id=
                conversation_id,

            role="user",

            content=request.message
        )

        # ─────────────────────────
        # GET HISTORY
        # ─────────────────────────

        conversation_history = (

            get_conversation_messages(

                db=db,

                conversation_id=
                    conversation_id
            )
        )

        # ─────────────────────────
        # AI FOLLOW-UP
        # ─────────────────────────

        followup_result = (

            generate_ai_followup(

                user_input=
                    request.message,

                conversation_history=
                    conversation_history
            )
        )

        ai_response = (
            followup_result["response"]
        )

        options = (
            followup_result["options"]
        )

        report_ready = (
            followup_result["report_ready"]
        )

        # ─────────────────────────
        # SAVE AI MESSAGE
        # ─────────────────────────

        save_message(

            db=db,

            conversation_id=
                conversation_id,

            role="assistant",

            content=ai_response
        )

        # ─────────────────────────
        # AI SEVERITY
        # ─────────────────────────

        severity_result = (

            analyze_severity(
                conversation_history
            )
        )

        severity = (
            severity_result["severity"]
        )

        severity_reason = (
            severity_result["reason"]
        )

        # ─────────────────────────
        # HOSPITALS
        # ─────────────────────────

        hospitals = []

        if (

            request.latitude
            and request.longitude
        ):

            hospitals = (

                get_nearby_hospitals(

                    latitude=
                        request.latitude,

                    longitude=
                        request.longitude,

                    symptoms=
                        request.message
                )
            )

        # ─────────────────────────
        # FINAL REPORT
        # ─────────────────────────

        pdf_url = None

        report_text = None

        if report_ready:

            report_text = (

                generate_ai_report(

                    conversation_history=
                        conversation_history,

                    severity=
                        severity
                )
            )

            pdf_result = (

                generate_pdf_report(
                    report_text
                )
            )

            if pdf_result["success"]:

                pdf_url = (

                    f"/reports/"
                    f"{pdf_result['filename']}"
                )

        # ─────────────────────────
        # FINAL RESPONSE
        # ─────────────────────────

        return {

            "success": True,

            "conversation_id":
                conversation_id,

            "response":
                ai_response,

            "options":
                options,

            "severity":
                severity,

            "severity_reason":
                severity_reason,

            "report_ready":
                report_ready,

            "report":
                report_text,

            "pdf_url":
                pdf_url,

            "hospitals":
                hospitals
        }

    except Exception as e:

        print(
            "Conversation Route Error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )