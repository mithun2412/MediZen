from app.llm.prompts import (
    CLINICAL_QUESTIONS
)

from app.medical.symptom_router import (
    detect_symptom_category
)


# ─────────────────────────────────────────────
# GET CURRENT QUESTION
# ─────────────────────────────────────────────
def get_current_question(
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

    answered_count = len([

        msg for msg in conversation

        if msg.get("role") == "user"
    ])

    if answered_count >= len(questions):

        return None

    return questions[answered_count]


# ─────────────────────────────────────────────
# VALIDATE ANSWER
# ─────────────────────────────────────────────
def validate_answer(
    question: dict,
    answer: str
):

    answer = answer.lower().strip()

    # clarification detection
    clarification_words = [

        "what",
        "what do you mean",
        "explain",
        "don't understand",
        "?"
    ]

    if any(
        word in answer
        for word in clarification_words
    ):

        return {

            "valid": False,

            "needs_clarification": True
        }

    # empty
    if len(answer) < 1:

        return {

            "valid": False,

            "needs_clarification": False
        }

    qtype = question.get("type")

    # =========================================
    # FREQUENCY
    # =========================================
    if qtype == "frequency":

        valid_words = [

            "constant",
            "occasional",
            "sometimes",
            "comes and goes"
        ]

        if not any(
            word in answer
            for word in valid_words
        ):

            return {

                "valid": False,

                "needs_clarification": True
            }

    # =========================================
    # YES / NO
    # =========================================
    if qtype == "yes_no":

        valid_words = [

            "yes",
            "no",
            "yeah",
            "nope",
            "yep"
        ]

        if not any(
            word in answer
            for word in valid_words
        ):

            return {

                "valid": False,

                "needs_clarification": True
            }

    return {

        "valid": True,

        "needs_clarification": False
    }


# ─────────────────────────────────────────────
# HELP TEXT
# ─────────────────────────────────────────────
def get_help_text(
    question: dict
):

    qtype = question.get("type")

    help_map = {

        "severity":
            "Answer like mild, moderate, severe or rate from 1-10.",

        "duration":
            "Example: yesterday, 2 days, 1 week.",

        "frequency":
            "Example: constant, occasional, comes and goes.",

        "yes_no":
            "Please answer yes or no.",

        "temperature":
            "Example: 101 F or 38 C."
    }

    return help_map.get(

        qtype,

        "Please describe your symptoms clearly."
    )


# ─────────────────────────────────────────────
# NORMALIZE ANSWERS
# ─────────────────────────────────────────────
def normalize_answer(
    question: dict,
    answer: str
):

    qtype = question.get("type")

    answer = answer.lower().strip()

    # =========================================
    # SEVERITY
    # =========================================
    if qtype == "severity":

        if any(word in answer for word in [
            "1", "2", "3",
            "mild"
        ]):

            return "Mild"

        if any(word in answer for word in [
            "4", "5", "6",
            "moderate",
            "bad"
        ]):

            return "Moderate"

        if any(word in answer for word in [
            "7", "8", "9", "10",
            "severe",
            "terrible"
        ]):

            return "Severe"

    # =========================================
    # YES / NO
    # =========================================
    if qtype == "yes_no":

        if answer in [
            "yes",
            "yeah",
            "yep"
        ]:

            return "Yes"

        if answer in [
            "no",
            "nope"
        ]:

            return "No"

    # =========================================
    # FREQUENCY
    # =========================================
    if qtype == "frequency":

        if "constant" in answer:

            return "Constant"

        if any(word in answer for word in [

            "occasional",
            "sometimes",
            "comes and goes"
        ]):

            return "Occasional"

    return answer