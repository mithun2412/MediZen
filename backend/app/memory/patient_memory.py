from app.memory.vector_memory import (

    store_memory,
    search_memory
)


# ─────────────────────────────────────────────
# SAVE PATIENT SYMPTOM MEMORY
# ─────────────────────────────────────────────

def save_patient_memory(

    user_id: int,

    symptom: str,

    analysis: str = ""
):

    memory_text = f"""

    Symptom: {symptom}

    Analysis: {analysis}

    """

    return store_memory(

        user_id=user_id,

        text=memory_text,

        metadata={

            "type": "medical_history"
        }
    )


# ─────────────────────────────────────────────
# GET RELEVANT PATIENT HISTORY
# ─────────────────────────────────────────────

def get_patient_history(

    symptom: str
):

    results = search_memory(

        query=symptom,

        top_k=3
    )

    return results["documents"]