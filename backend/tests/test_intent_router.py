import pytest

from app.services.ai_decision_service import LLMDecisionUnavailable
from app.services.intent_router import route_intent


@pytest.fixture(autouse=True)
def mock_llm_router(monkeypatch):
    def decide(message, **_context):
        text = message.lower()
        intent = (
            "ANALYTICS" if "health score" in text or "trend" in text else
            "KNOWLEDGE" if "app" in text or text.startswith("how does") else
            "REPORT" if "report" in text else
            "MEDICATION" if "dose" in text else
            "GENERAL" if "thanks" in text else
            "SYMPTOM"
        )
        return {"intent": intent, "confidence": 0.9, "reason": "Mock LLM", "decision_source": "llm"}
    monkeypatch.setattr("app.services.intent_router.decide_intent", decide)


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


def test_does_not_use_keyword_routing_when_llm_is_unavailable(monkeypatch):
    monkeypatch.setattr("app.services.intent_router.decide_intent", lambda *_args, **_kwargs: None)
    with pytest.raises(LLMDecisionUnavailable):
        route_intent("I have a headache")
