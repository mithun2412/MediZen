from typing import List, Dict, Any
from app.services.ai_decision_service import LLMDecisionUnavailable, assess_symptoms

def analyze_severity(conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the severity of symptoms based on conversation history.
    """
    llm_result = assess_symptoms(conversation_history)
    if llm_result:
        return llm_result
    raise LLMDecisionUnavailable("The AI triage service is unavailable. Please try again shortly.")
