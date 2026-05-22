from app.llm.prompts import (
    CLINICAL_QUESTIONS
)

from app.medical.symptom_router import (
    detect_symptom_category
)

from app.medical.intake_engine import (
    normalize_answer
)


# ─────────────────────────────────────────────
# BUILD STRUCTURED CONTEXT
# ─────────────────────────────────────────────
def build_symptom_context(
    symptom: str,
    conversation: list
):

    category = detect_symptom_category(
        symptom
    )

    questions = CLINICAL_QUESTIONS.get(

        category,

        CLINICAL_QUESTIONS["default"]
    )

    context = {}

    user_answers = [

        msg for msg in conversation

        if msg.get("role") == "user"
    ]

    for i, answer_msg in enumerate(user_answers):

        if i >= len(questions):

            break

        question = questions[i]

        key = question["key"]

        answer = answer_msg.get(
            "content",
            ""
        )

        context[key] = normalize_answer(
            question,
            answer
        )

    return context