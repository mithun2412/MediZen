EMERGENCY_KEYWORDS = [
    "chest pain",
    "heart attack",
    "can't breathe",
    "difficulty breathing",
    "shortness of breath",
    "stroke",
    "face drooping",
    "arm weakness",
    "speech difficulty",
    "unconscious",
    "seizure",
    "vomiting blood",
    "severe bleeding",
    "suicidal",
    "anaphylaxis"
]


def check_emergency(symptom_text: str):

    text_lower = symptom_text.lower()

    return any(
        keyword in text_lower
        for keyword in EMERGENCY_KEYWORDS
    )