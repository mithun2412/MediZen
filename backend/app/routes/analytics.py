from fastapi import (

    APIRouter,

    Depends,

    HTTPException
)

from sqlalchemy.orm import Session

from pydantic import BaseModel

from app.database import get_db

from app.services.adherence_service import (

    save_health_record,

    get_user_health_history,

    delete_health_record
)

from app.services.analytics_service import (
    generate_health_analytics
)

router = APIRouter()


# ─────────────────────────────────────────────
# REQUEST MODELS
# ─────────────────────────────────────────────

class SaveHealthRequest(BaseModel):

    user_id: int

    symptom: str

    analysis: str

    severity: str


class DeleteRecordRequest(BaseModel):

    record_id: int


# ─────────────────────────────────────────────
# SAVE HEALTH HISTORY
# ─────────────────────────────────────────────

@router.post("/save")
def save_health_history(

    request: SaveHealthRequest,

    db: Session = Depends(get_db)
):

    try:

        result = save_health_record(

            db=db,

            user_id=request.user_id,

            symptom=request.symptom,

            analysis=request.analysis,

            severity=request.severity
        )

        return result

    except Exception as e:

        print(
            "Save Analytics Error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ─────────────────────────────────────────────
# GET USER HISTORY
# ─────────────────────────────────────────────

@router.get("/history/{user_id}")
def get_health_history(

    user_id: int,

    db: Session = Depends(get_db)
):

    try:

        result = get_user_health_history(

            db=db,

            user_id=user_id
        )

        return result

    except Exception as e:

        print(
            "History Route Error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ─────────────────────────────────────────────
# HEALTH ANALYTICS
# ─────────────────────────────────────────────

@router.get("/dashboard/{user_id}")
def get_dashboard_analytics(

    user_id: int,

    db: Session = Depends(get_db)
):

    try:

        # GET HISTORY
        history_result = (

            get_user_health_history(

                db=db,

                user_id=user_id
            )
        )

        if not history_result["success"]:

            raise HTTPException(

                status_code=400,

                detail=
                    "Unable to fetch history."
            )

        history = history_result[
            "history"
        ]

        # GENERATE ANALYTICS
        analytics = (

            generate_health_analytics(
                history
            )
        )

        return analytics

    except Exception as e:

        print(
            "Dashboard Analytics Error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ─────────────────────────────────────────────
# DELETE HEALTH RECORD
# ─────────────────────────────────────────────

@router.delete("/delete")
def delete_record(

    request: DeleteRecordRequest,

    db: Session = Depends(get_db)
):

    try:

        result = delete_health_record(

            db=db,

            record_id=request.record_id
        )

        return result

    except Exception as e:

        print(
            "Delete Route Error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )