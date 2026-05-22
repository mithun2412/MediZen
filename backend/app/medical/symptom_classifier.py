def detect_query_type(text: str):

    text = text.lower().strip()

    app_queries = [
        "who are you",
        "what is your name",
        "your name",
        "what can you do",
        "what will you do",
        "what does this app do",
        "what will this app do",
        "what is this app about",
        "about you",
        "about app",
        "features",
        "introduce yourself"
    ]

    for q in app_queries:
        if q == text:
            return "app_info"

    greetings = [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good evening"
    ]

    for g in greetings:
        if g == text:
            return "greeting"

    health_keywords = [
        "pain",
        "fever",
        "headache",
        "nausea",
        "vomit",
        "vomiting",
        "dizziness",
        "cough",
        "cold",
        "flu",
        "infection",
        "chest",
        "breathing",
        "asthma",
        "diabetes",
        "heart",
        "medicine",
        "tablet",
        "doctor",
        "symptom",
        "sick",
        "ill",
        "fatigue",
        "stomach",
        "migraine",
        "allergy",
        "rash",
        "injury",
        "stress",
        "anxiety",
        "depression",
        "severe",
        "hurt",
        "ache"
    ]

    for word in health_keywords:
        if word in text:
            return "health"

    return "other"