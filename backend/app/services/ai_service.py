# FILE: backend/app/services/ai_service.py

from app.llm.groq_client import client

from app.medical.symptom_router import (
    detect_symptom_category
)


from app.medical.emergency_detector import check_emergency
from app.medical.symptom_classifier import detect_query_type
from app.llm.parser import (
    clean_json_response,
    validate_analysis
)
from app.medical.symptom_context import (
    build_symptom_context
)
from app.llm.prompts import (

    QUESTION_REFINE_SYSTEM,

    FINAL_ANALYSIS_SYSTEM,

    CLINICAL_QUESTIONS
)
from app.memory.patient_memory import (
    save_patient_memory,
    get_patient_history
)




# HELPERS
# ─────────────────────────────────────────────────────────────

def _conversation_text(conversation: list):

    return " ".join(
        m.get("content", "")
        for m in conversation
    ).lower()


def _covered_keys(conversation: list):

    conv_text = _conversation_text(conversation)

    covered = set()

    coverage_hints = {

        "onset": [
            "started",
            "since",
            "yesterday",
            "days ago",
            "morning"
        ],

        "severity": [
            "1/10",
            "5/10",
            "10/10",
            "pain level"
        ],

        "location": [
            "left",
            "right",
            "head",
            "stomach",
            "chest"
        ],

        "character": [
            "sharp",
            "dull",
            "burning",
            "pressure",
            "throbbing"
        ],

        "associated": [
            "fever",
            "nausea",
            "vomiting",
            "fatigue",
            "dizziness"
        ],

        "history": [
            "diabetes",
            "bp",
            "asthma",
            "tablet",
            "medicine"
        ]
    }

    for key, hints in coverage_hints.items():

        if any(h in conv_text for h in hints):
            covered.add(key)

    return covered




def _pick_next_question(
    symptom: str,
    conversation: list
):

    # Detect category
    category = detect_symptom_category(
        symptom
    )

    # Get question set
    selected_questions = (
        CLINICAL_QUESTIONS.get(
            category,
            CLINICAL_QUESTIONS["default"]
        )
    )

    # Count answered user messages
    answered_count = len([

        msg for msg in conversation

        if msg.get("role") == "user"
    ])

    # Finished all questions
    if answered_count >= len(
        selected_questions
    ):

        return None

    # Return next question object
    return selected_questions[
        answered_count
    ]



def _naturalise_question(
    raw_question: str,
    symptom: str,
    conversation: list
):

    last_user_message = ""

    for m in reversed(conversation):

        if m.get("role") == "user":
            last_user_message = m.get("content", "")
            break

    context = f"""
Patient symptoms:
{symptom}

Last user message:
{last_user_message}

Question:
{raw_question}
"""

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": QUESTION_REFINE_SYSTEM
            },

            {
                "role": "user",
                "content": context
            }
        ],

        max_tokens=100,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()





def _build_final_analysis(
    symptom: str,
    conversation: list
):
    structured_context = build_symptom_context(
        symptom,
        conversation
    )

    # 🧠 VECTOR MEMORY

    previous_history = get_patient_history(
        symptom
    )

    history_text = "\n".join(
        previous_history
    )

    messages = [

        {
            "role": "system",
            "content": FINAL_ANALYSIS_SYSTEM
        },

        {
            "role": "user",

            "content": (

            f"Initial symptoms: {symptom}\n\n"

            f"Structured clinical context:\n"
            f"{structured_context}\n\n"

            f"Previous patient medical history:\n"
            f"{history_text}"
            )
        },

        *conversation,

        {
            "role": "user",
            "content": (
                "Give the final medical analysis."
            )
        }
    ]

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=messages,

        max_tokens=700,

        temperature=0.3,
    )

    raw = response.choices[0].message.content.strip()
    print("\nRAW LLM RESPONSE:\n")
    print(raw)
    print("\n")

    analysis = clean_json_response(raw)

    analysis = validate_analysis(
        analysis
    )
    save_patient_memory(

    user_id=1,

    symptom=symptom,

    analysis=str(analysis)
    )
    return analysis


# ─────────────────────────────────────────────────────────────
# SIMPLE ANALYSIS
# ─────────────────────────────────────────────────────────────

def analyze_symptoms(symptom: str):

    try:

        analysis = _build_final_analysis(
            symptom,
            []
        )

        return {

            "analysis": analysis,

            "severity": analysis.get(
                "severity",
                "Low"
            ),

            "remedies": analysis.get(
                "remedies",
                []
            ),

            "when_to_see_doctor": analysis.get(
                "when_to_see_doctor",
                ""
            ),

            "is_emergency": analysis.get(
                "is_emergency",
                False
            )
        }

    except Exception as e:

        print(
            "Analyze Symptoms Error:",
            e
        )

        return {
            "analysis": {},
            "severity": "Low",
            "remedies": [],
            "when_to_see_doctor": "",
            "is_emergency": False
        }


# ─────────────────────────────────────────────────────────────
# MAIN FOLLOW-UP FUNCTION
# ─────────────────────────────────────────────────────────────

def generate_followup_question(
    symptom: str,
    conversation: list
):

    query_type = detect_query_type(symptom)

    symptom_lower = symptom.lower().strip()

    # ─────────────────────────────────────────
    # GREETING
    # ─────────────────────────────────────────

    if query_type == "greeting":

        return {

            "is_done": False,

            "question": (
                "Hello, I'm MediZen AI.\n\n"
                "Your intelligent healthcare assistant.\n\n"
                "Describe your symptoms and "
                "I'll help analyze them step by step."
            ),

            "final_analysis": None
        }

    # ─────────────────────────────────────────
    # APP INFO
    # ─────────────────────────────────────────

    if query_type == "app_info":

        if (
            symptom_lower == "who are you"
            or symptom_lower == "what is your name"
            or symptom_lower == "your name"
            or symptom_lower == "introduce yourself"
        ):

            return {

                "is_done": False,

                "question": (
                    "I'm MediZen AI — your intelligent healthcare assistant.\n\n"

                    "I help users with:\n"
                    "• AI symptom analysis\n"
                    "• Medicine guidance\n"
                    "• Health recommendations\n"
                    "• Emergency detection\n"
                    "• Smart medical conversations\n\n"

                    "You can type or use voice to describe your symptoms."
                ),

                "final_analysis": None
            }

        return {

            "is_done": False,

            "question": (
                "MediZen AI is an AI-powered healthcare platform "
                "designed to help users understand and manage their health.\n\n"

                "Features include:\n"
                "• AI symptom analysis\n"
                "• Smart medical follow-up questions\n"
                "• Medicine recommendations & reminders\n"
                "• Emergency severity detection\n"
                "• Voice healthcare interaction\n"
                "• Health dashboards & analytics\n"
                "• AI medical PDF reports\n"
                "• Nearby hospital finder\n"
                "• Health history tracking\n\n"

                "Simply describe your symptoms and "
                "I'll guide you step by step."
            ),

            "final_analysis": None
        }

    # ─────────────────────────────────────────
    # NON HEALTH
    # ─────────────────────────────────────────

    if query_type == "other":

        return {

            "is_done": False,

            "question": (
                "Sorry, I mainly assist with healthcare "
                "and medical-related concerns.\n\n"

                "Please describe your symptoms "
                "or health issue."
            ),

            "final_analysis": None
        }

    # ─────────────────────────────────────────
    # NORMAL HEALTHCARE FLOW
    # ─────────────────────────────────────────

    ai_turns = [

        m for m in conversation

        if m.get("role") == "assistant"
    ]

    force_final = len(ai_turns) >= 6

    if not force_final:

        next_q_template = _pick_next_question(
            symptom,
            conversation
        )

    else:

        next_q_template = None

    # ─────────────────────────────────────────
    # ASK NEXT QUESTION
    # ─────────────────────────────────────────

    if next_q_template and not force_final:

        natural_q = next_q_template["question"]

        return {

            "is_done": False,

            "question": natural_q,

            "final_analysis": None,
        }

    # ─────────────────────────────────────────
    # FINAL ANALYSIS
    # ─────────────────────────────────────────

    try:

        analysis = _build_final_analysis(
            symptom,
            conversation
        )

        return {

            "is_done": True,

            "question": None,

            "final_analysis": analysis,
        }

    except Exception as e:

        print("FINAL ANALYSIS ERROR:", e)

        return {

            "is_done": True,

            "question": None,

            "final_analysis": {

                "possible_conditions": [
                    "Unable to generate detailed analysis"
                ],

                "severity": "Moderate",

                "is_emergency": False,

                "medications": [],

                "remedies": [

                    "Take proper rest",

                    "Stay hydrated",

                    "Consult a doctor if symptoms worsen"
                ],

                "when_to_see_doctor":
                    "If symptoms continue or worsen",

                "doctor_advice":
                    "Professional consultation recommended.",

                "tests": []
            }
        }