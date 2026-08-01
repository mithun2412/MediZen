"""Single, deterministic intent router for messages sent to the health chat."""
from dataclasses import asdict, dataclass
import re


@dataclass(frozen=True)
class IntentResult:
    intent: str
    confidence: float
    reason: str
    next_action: str

    def to_dict(self):
        return asdict(self)


INTENT_ACTIONS = {
    "SYMPTOM": "symptom_workflow",
    "KNOWLEDGE": "knowledge_base_lookup",
    "REPORT": "report_analysis_workflow",
    "MEDICATION": "medication_service",
    "ANALYTICS": "live_analytics_lookup",
    "GENERAL": "general_response",
}

# Priority matters. For example, "report history" is analytics, while
# "summarise my uploaded report" is report analysis.
PATTERNS = {
    "ANALYTICS": ("health score", "health analytics", "analytics", "symptom trend", "symptom trends", "recovery trend", "ai insight", "report history", "health history"),
    "MEDICATION": ("medication", "medicine", "tablet", "pill", "dose", "doses", "reminder", "adherence", "mark taken", "missed dose"),
    "REPORT": ("medical report", "lab report", "blood report", "scan report", "uploaded report", "document", "pdf", "test result", "report summary", "summarize report", "summarise report"),
    "KNOWLEDGE": ("medizen", "this app", "the app", "application", "feature", "features", "service", "services", "privacy", "data safe", "how does", "how do i use", "what can you do"),
    "SYMPTOM": ("pain", "ache", "fever", "cough", "cold", "headache", "migraine", "nausea", "vomit", "dizzy", "dizziness", "rash", "swelling", "breath", "breathing", "chest", "diarrhea", "diarrhoea", "fatigue", "tired", "symptom", "recover", "recovery", "condition", "feel sick", "unwell"),
}
GENERAL = ("hi", "hello", "hey", "thanks", "thank you", "good morning", "good evening")
KNOWLEDGE_EXPLANATION_PATTERNS = (
    "how does ai health chat work", "how does medical report analysis work",
    "how does medication reminder work", "how does medication tracker work",
    "how is my health score calculated", "why did my health score decrease",
    "what are ai insights", "what happens when i recover", "symptom recurrence",
    "can medizen", "what information is stored", "how does report history work",
)


def route_intent(message: str, *, symptom_workflow_active: bool = False, report_context_active: bool = False) -> dict:
    """Classify one message exactly once before any workflow is invoked."""
    text = re.sub(r"\s+", " ", (message or "").lower()).strip()
    if not text:
        return IntentResult("GENERAL", 0.99, "The message is empty.", INTENT_ACTIONS["GENERAL"]).to_dict()

    if text in GENERAL or re.fullmatch(r"(hi|hello|hey)[!. ]*", text):
        return IntentResult("GENERAL", 0.99, "The message is a greeting or acknowledgement.", INTENT_ACTIONS["GENERAL"]).to_dict()

    if any(pattern in text for pattern in KNOWLEDGE_EXPLANATION_PATTERNS):
        return IntentResult("KNOWLEDGE", 0.96, "Matched an application knowledge-base question.", INTENT_ACTIONS["KNOWLEDGE"]).to_dict()

    for intent in ("ANALYTICS", "MEDICATION", "REPORT", "KNOWLEDGE", "SYMPTOM"):
        matches = [keyword for keyword in PATTERNS[intent] if keyword in text]
        if matches:
            return IntentResult(intent, min(0.99, 0.88 + 0.04 * len(matches)), f"Matched {intent.lower()} terms: {', '.join(matches[:2])}.", INTENT_ACTIONS[intent]).to_dict()

    if report_context_active:
        return IntentResult("REPORT", 0.82, "The active conversation contains a completed report.", INTENT_ACTIONS["REPORT"]).to_dict()
    if symptom_workflow_active:
        return IntentResult("SYMPTOM", 0.82, "The message continues an active symptom assessment.", INTENT_ACTIONS["SYMPTOM"]).to_dict()
    return IntentResult("GENERAL", 0.75, "No supported health workflow was identified.", INTENT_ACTIONS["GENERAL"]).to_dict()
