from app.services.intent_router import route_intent


def test_routes_supported_intents():
    cases = {
        "I have had a headache for two days": "SYMPTOM",
        "How does this app protect my privacy?": "KNOWLEDGE",
        "Summarise my uploaded blood report": "REPORT",
        "How many doses did I miss?": "MEDICATION",
        "What is my health score and symptom trend?": "ANALYTICS",
        "Thanks!": "GENERAL",
    }
    for message, expected in cases.items():
        result = route_intent(message)
        assert result["intent"] == expected
        assert 0 <= result["confidence"] <= 1
        assert result["next_action"]


def test_routes_short_follow_up_to_active_symptom_workflow():
    assert route_intent("three days", symptom_workflow_active=True)["intent"] == "SYMPTOM"


def test_routes_product_explanations_to_knowledge_base():
    assert route_intent("How is my Health Score calculated?")["intent"] == "KNOWLEDGE"
    assert route_intent("How does Medical Report Analysis work?")["intent"] == "KNOWLEDGE"
