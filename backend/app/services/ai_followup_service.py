"""LLM-led symptom assessment and follow-up orchestration."""
import json
from typing import Any, Dict, List, Optional

from app.llm.groq_client import client


FOLLOWUP_SYSTEM_PROMPT = """
You are MediZen AI's symptom-assessment assistant. Analyse the user's actual
words and the complete conversation to decide what matters clinically. Do not
follow a fixed questionnaire and do not use canned symptom lists.

Your job is to:
- identify the reported concern and what is already known;
- ask the single most useful next question, tailored to that concern;
- avoid asking for facts already supplied;
- determine when there is enough information for a concise symptom assessment
  report, then set report_ready to true;
- immediately advise emergency services for red-flag symptoms. In that case,
  set report_ready to true so the safety report can be generated.

Ask only one clear question per turn. You may ask about onset, severity,
location, triggers, associated symptoms, relevant health history, medication,
or allergies only when it will change the assessment. Do not diagnose or
claim certainty. Do not tell users to stop prescribed medication.

Return strict JSON only, with this exact shape:
{
  "response": "your helpful response or next question",
  "report_ready": false,
  "followup_options": ["optional concise answer", "optional concise answer"],
  "assessment_summary": "brief internal summary of facts collected",
  "reason": "why this is the best next action"
}

followup_options is optional. Include 0 to 4 options only when they naturally
fit the question; create them from the user's specific context, never from a
predefined list. When report_ready is true, return an empty followup_options
array.
"""


def clean_messages_for_api(messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Keep only valid chat turns; persisted history is the source of truth."""
    return [
        {"role": message["role"], "content": message["content"]}
        for message in messages
        if message.get("role") in {"user", "assistant", "system"} and message.get("content")
    ]


def _parse_json_response(content: str) -> Dict[str, Any]:
    """Accept JSON in a fenced response without inventing a canned answer."""
    value = (content or "").strip()
    if value.startswith("```"):
        value = value.split("\n", 1)[1] if "\n" in value else ""
        value = value.rsplit("```", 1)[0].strip()
    start, end = value.find("{"), value.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Model response did not contain a JSON object")
    parsed = json.loads(value[start:end + 1])
    if not isinstance(parsed, dict) or not isinstance(parsed.get("response"), str):
        raise ValueError("Model response is missing a text response")
    return parsed


def generate_ai_followup(
    user_input: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Let the LLM choose the symptom-specific next step or report readiness."""
    try:
        history = clean_messages_for_api(conversation_history or [])
        messages = [{"role": "system", "content": FOLLOWUP_SYSTEM_PROMPT}, *history]
        # The route normally persists the latest user turn before this call.
        if user_input and (not history or history[-1] != {"role": "user", "content": user_input}):
            messages.append({"role": "user", "content": user_input})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            max_tokens=500,
        )
        result = _parse_json_response(completion.choices[0].message.content)
        report_ready = bool(result.get("report_ready", False))
        options = result.get("followup_options", [])
        options = [str(option).strip() for option in options if str(option).strip()][:4] if isinstance(options, list) else []

        return {
            "response": result["response"].strip(),
            "report_ready": report_ready,
            "followup_options": [] if report_ready else options,
            "assessment_summary": str(result.get("assessment_summary", "")).strip(),
            "reason": str(result.get("reason", "")).strip(),
        }
    except Exception as error:
        print(f"AI Followup Error: {error}")
        return {
            "response": "I’m unable to assess that right now. Please try again, or seek medical care urgently if your symptoms are severe or worsening.",
            "report_ready": False,
            "followup_options": [],
            "assessment_summary": "",
            "reason": "The symptom-assessment model was unavailable.",
        }
