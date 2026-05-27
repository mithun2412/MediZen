from sqlalchemy.orm import Session

from app.models.models import (
    SymptomHistory
)


# ─────────────────────────────────────────────
# SAVE HEALTHCARE HISTORY
# ─────────────────────────────────────────────

def save_health_record(

    db: Session,

    user_id: int,

    symptom: str,

    analysis: str,

    severity: str
):

    try:

        history = SymptomHistory(

            user_id=user_id,

            symptom=symptom,

            analysis=analysis,

            severity=severity
        )

        db.add(history)

        db.commit()

        db.refresh(history)

        return {

            "success": True,

            "message":

                "Healthcare history "
                "saved successfully."
        }

    except Exception as e:

        print(
            "Save History Error:",
            e
        )

        return {

            "success": False,

            "message":

                "Unable to save "
                "healthcare history."
        }


# ─────────────────────────────────────────────
# GET USER HEALTH HISTORY
# ─────────────────────────────────────────────

def get_user_health_history(

    db: Session,

    user_id: int
):

    try:

        records = (

            db.query(SymptomHistory)

            .filter(

                SymptomHistory.user_id
                == user_id
            )

            .order_by(

                SymptomHistory.created_at
                .desc()
            )

            .all()
        )

        history = []

        for record in records:

            history.append({

                "id":
                    record.id,

                "symptom":
                    record.symptom,

                "analysis":
                    record.analysis,

                "severity":
                    record.severity,

                "created_at":

                    str(
                        record.created_at
                    )
            })

        return {

            "success": True,

            "history":
                history
        }

    except Exception as e:

        print(
            "History Fetch Error:",
            e
        )

        return {

            "success": False,

            "history": []
        }


# ─────────────────────────────────────────────
# DELETE HEALTH RECORD
# ─────────────────────────────────────────────

def delete_health_record(

    db: Session,

    record_id: int
):

    try:

        record = (

            db.query(SymptomHistory)

            .filter(

                SymptomHistory.id
                == record_id
            )

            .first()
        )

        if not record:

            return {

                "success": False,

                "message":
                    "Record not found."
            }

        db.delete(record)

        db.commit()

        return {

            "success": True,

            "message":

                "Health record "
                "deleted successfully."
        }

    except Exception as e:

        print(
            "Delete Record Error:",
            e
        )

        return {

            "success": False,

            "message":

                "Unable to delete "
                "health record."
        }