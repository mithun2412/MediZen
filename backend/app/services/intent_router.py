"""LLM-selected workflow routing for messages sent to the health chat."""
from app.services.ai_decision_service import LLMDecisionUnavailable, decide_intent


INTENT_ACTIONS = {
    "SYMPTOM": "symptom_workflow",
    "KNOWLEDGE": "knowledge_base_lookup",
    "REPORT": "report_analysis_workflow",
    "MEDICATION": "medication_service",
    "ANALYTICS": "live_analytics_lookup",
    "GENERAL": "general_response",
}

def route_intent(message: str, *, symptom_workflow_active: bool = False, report_context_active: bool = False) -> dict:
    """Use the LLM to select the workflow; no keyword routing is applied."""
    decision = decide_intent(
        message,
        symptom_workflow_active=symptom_workflow_active,
        report_context_active=report_context_active,
    )
    if decision:
        decision["next_action"] = INTENT_ACTIONS[decision["intent"]]
        return decision
    raise LLMDecisionUnavailable("The AI routing service is unavailable. Please try again shortly.")
