"""Structured LLM decisions for MediZen's health-chat workflows.

The model is used for judgement; application code remains responsible for
validation, persistence, and emergency safety guards.
"""
from __future__ import annotations

import json
import os
from typing import Any


INTENTS = {"SYMPTOM", "KNOWLEDGE", "REPORT", "MEDICATION", "ANALYTICS", "GENERAL"}
SPECIALTIES = {
    "General Medicine", "Cardiology", "Neurology", "Gastroenterology",
    "Pulmonology", "Dermatology", "Orthopedics", "Ophthalmology", "ENT",
    "Emergency Medicine",
}
class LLMDecisionUnavailable(RuntimeError):
    """Raised when a workflow needs an LLM decision but none is available."""


def _json_object(value: str) -> dict[str, Any]:
    start, end = value.find("{"), value.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Model response did not contain a JSON object")
    parsed = json.loads(value[start:end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Model response was not an object")
    return parsed


def _complete(system_prompt: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    """Request a decision without making an API key mandatory for startup."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    try:
        from groq import Groq

        completion = Groq(api_key=api_key).chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0,
            max_tokens=300,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload)},
            ],
        )
        return _json_object(completion.choices[0].message.content or "")
    except Exception:
        return None


def decide_intent(message: str, *, symptom_workflow_active: bool, report_context_active: bool) -> dict[str, Any] | None:
    result = _complete(
        """Classify the user's message for a healthcare app. Return JSON only:
{"intent":"SYMPTOM|KNOWLEDGE|REPORT|MEDICATION|ANALYTICS|GENERAL", "confidence":0.0, "reason":"brief"}.
Use KNOWLEDGE for questions about how MediZen works, REPORT for an uploaded or generated report,
MEDICATION for dose/reminder questions, ANALYTICS for account health metrics, and SYMPTOM for a
health concern. Prefer the active workflow only if the message reasonably continues it.""",
        {"message": message, "symptom_workflow_active": symptom_workflow_active, "report_context_active": report_context_active},
    )
    if not result or result.get("intent") not in INTENTS:
        return None
    return {
        "intent": result["intent"],
        "confidence": max(0.0, min(1.0, float(result.get("confidence", 0.8)))),
        "reason": str(result.get("reason", "Classified by the AI decision model.")).strip(),
        "decision_source": "llm",
    }


def assess_symptoms(conversation_history: list[dict[str, Any]]) -> dict[str, str] | None:
    user_messages = [str(item.get("content", "")) for item in conversation_history if item.get("role") == "user"]
    result = _complete(
        """Assess the reported symptoms conservatively. This is triage support, not a diagnosis.
Return JSON only: {"severity":"LOW|MODERATE|HIGH", "specialty":"one allowed specialty", "reason":"brief, patient-safe explanation"}.
Allowed specialties: General Medicine, Cardiology, Neurology, Gastroenterology, Pulmonology,
Dermatology, Orthopedics, Ophthalmology, ENT, Emergency Medicine. Use HIGH and Emergency Medicine
for possible emergency red flags. If uncertain, choose MODERATE and General Medicine. Do not give a diagnosis.""",
        {"conversation": user_messages},
    )
    if not result or result.get("severity") not in {"LOW", "MODERATE", "HIGH"} or result.get("specialty") not in SPECIALTIES:
        return None
    return {
        "severity": result["severity"],
        "specialty": result["specialty"],
        "reason": str(result.get("reason", "AI triage assessment.")).strip(),
        "decision_source": "llm",
    }


def extract_symptom_summary(conversation_history: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Use the LLM to extract report fields from the complete conversation."""
    messages = [
        {"role": item.get("role"), "content": str(item.get("content", ""))}
        for item in conversation_history
        if item.get("role") in {"user", "assistant"} and item.get("content")
    ]
    result = _complete(
        """Extract only facts explicitly stated by the user in this health-chat conversation.
Ignore greetings, acknowledgements, questions from the assistant, and unsupported inferences.
Return JSON only with exactly these fields:
{"primary_symptom":"string or Not specified", "duration":"string or Not specified",
"severity":"string or Not specified", "severity_rating":null, "associated_symptoms":[],
"medical_history":"string or None reported", "pain_type":"string or Not specified",
"location":"string or Not specified", "pattern":"string or Not specified"}.
The primary_symptom must be the user's actual health concern, never a greeting such as hi or hello.
severity_rating must be an integer from 1 to 10 only when explicitly supplied.""",
        {"conversation": messages},
    )
    if not result or not isinstance(result.get("primary_symptom"), str):
        return None
    defaults = {
        "duration": "Not specified", "severity": "Not specified", "severity_rating": None,
        "associated_symptoms": [], "medical_history": "None reported", "pain_type": "Not specified",
        "location": "Not specified", "pattern": "Not specified",
    }
    summary = {"primary_symptom": result["primary_symptom"].strip() or "Not specified", **defaults}
    for key in defaults:
        if key in result:
            summary[key] = result[key]
    if not isinstance(summary["associated_symptoms"], list):
        summary["associated_symptoms"] = []
    if not isinstance(summary["severity_rating"], int) or not 1 <= summary["severity_rating"] <= 10:
        summary["severity_rating"] = None
    return summary
