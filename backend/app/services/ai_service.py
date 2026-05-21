import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 🚨 Emergency keywords
EMERGENCY_KEYWORDS = [
    "chest pain", "chest tightness", "heart attack",
    "can't breathe", "cannot breathe", "difficulty breathing",
    "shortness of breath", "not breathing", "trouble breathing",
    "stroke", "face drooping", "arm weakness", "speech difficulty",
    "unconscious", "unresponsive", "collapsed", "fainting",
    "seizure", "convulsion",
    "severe bleeding", "coughing blood", "vomiting blood",
    "overdose", "poisoning",
    "suicidal", "suicide",
    "severe allergic", "anaphylaxis", "throat swelling",
    "heart racing", "severe chest"
]

def check_emergency(symptom_text: str) -> bool:
    text_lower = symptom_text.lower()
    return any(keyword in text_lower for keyword in EMERGENCY_KEYWORDS)

def extract_severity(text: str, is_emergency: bool) -> str:
    if is_emergency:
        return "Critical"
    text_lower = text.lower()
    if "high" in text_lower or "severe" in text_lower or "emergency" in text_lower or "urgent" in text_lower:
        return "High"
    elif "moderate" in text_lower or "medium" in text_lower:
        return "Moderate"
    else:
        return "Low"

def extract_remedies(text: str) -> list:
    """Extract HOME REMEDIES section as a list."""
    remedies = []
    lines = text.split("\n")
    in_remedies = False
    for line in lines:
        if "HOME REMEDIES" in line.upper():
            in_remedies = True
            continue
        if in_remedies:
            # Stop at next section
            if line.strip().startswith("**") and "REMEDIES" not in line.upper():
                break
            stripped = line.strip().lstrip("-•*123456789. ")
            if stripped:
                remedies.append(stripped)
    return remedies[:4]  # max 4

def extract_when_to_see_doctor(text: str) -> str:
    """Extract WHEN TO SEE A DOCTOR section."""
    lines = text.split("\n")
    in_section = False
    result = []
    for line in lines:
        if "WHEN TO SEE" in line.upper():
            in_section = True
            continue
        if in_section:
            if line.strip().startswith("**") and "WHEN" not in line.upper():
                break
            stripped = line.strip().lstrip("-•*123456789. ")
            if stripped:
                result.append(stripped)
    return " ".join(result[:2])

def analyze_symptoms(symptom: str) -> dict:
    is_emergency = check_emergency(symptom)

    emergency_note = ""
    if is_emergency:
        emergency_note = """
⚠️ EMERGENCY WARNING: The symptoms described may indicate a life-threatening condition.
Start your response with: "🚨 EMERGENCY: Seek immediate medical help. Call 112 or go to the nearest emergency room NOW."
"""

    prompt = f"""You are an expert AI medical assistant. A patient has reported the following symptoms:

Symptoms: {symptom}
{emergency_note}
Please analyze these symptoms and provide a detailed response in the following format:

**POSSIBLE CONDITIONS:**
List 2-3 possible medical conditions that may be causing these symptoms.

**SEVERITY LEVEL:**
State the severity as one of: Low / Moderate / High / Critical
- Low: Minor issue, can be managed at home
- Moderate: Should see a doctor within 1-2 days
- High: Needs immediate medical attention
- Critical: Emergency — call ambulance immediately

**HOME REMEDIES:**
List 3-4 practical home remedies or self-care tips.

**WHEN TO SEE A DOCTOR:**
Clearly explain when and why the patient should visit a doctor.

**DISCLAIMER:**
⚠️ This analysis is for informational purposes only and is NOT professional medical advice.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert AI medical assistant. Always provide structured, helpful medical information with appropriate disclaimers."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1024,
            temperature=0.7,
        )

        analysis_text = response.choices[0].message.content
        severity  = extract_severity(analysis_text, is_emergency)
        remedies  = extract_remedies(analysis_text)
        when_doc  = extract_when_to_see_doctor(analysis_text)

        return {
            "analysis": analysis_text,
            "severity": severity,
            "remedies": remedies,
            "when_to_see_doctor": when_doc,
            "is_emergency": is_emergency
        }

    except Exception as e:
        print(f"Groq API Error: {e}")
        raise Exception(f"AI service error: {str(e)}")


# ─────────────────────────────────────────
# 🤖 AI FOLLOW-UP QUESTIONS
# ─────────────────────────────────────────

def generate_followup_question(symptom: str, conversation: list) -> dict:
    """
    Given initial symptoms + conversation history,
    returns next follow-up question OR final analysis.
    """

    # Count how many AI turns have happened
    ai_turns = [m for m in conversation if m["role"] == "assistant"]

    # After 4 AI questions, force final analysis
    force_final = len(ai_turns) >= 4

    system_prompt = """You are an expert AI medical assistant conducting a symptom interview.

Your job is to ask ONE short follow-up question at a time to better understand the patient's condition.

Rules:
- Ask only ONE question per response — never two
- Keep questions short, clear, and empathetic
- Focus on: duration, severity (1-10), location, triggers, associated symptoms, medications taken
- After gathering enough info (3-5 exchanges), provide a final analysis
- To give final analysis, start your ENTIRE response with the token: [FINAL_ANALYSIS]
- After [FINAL_ANALYSIS], return ONLY valid JSON in this exact format:
{
  "possible_conditions": ["condition1", "condition2"],
  "severity": "Low|Moderate|High|Critical",
  "is_emergency": true/false,
  "remedies": ["remedy1", "remedy2", "remedy3"],
  "when_to_see_doctor": "Clear advice on when to visit a doctor",
  "doctor_advice": "Specialist to consult if needed"
}
- Never add text before or after the JSON when giving final analysis
- Never use markdown code blocks around the JSON"""

    user_context = f"Patient's initial symptoms: {symptom}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_context},
        *conversation
    ]

    # If enough turns, instruct AI to wrap up
    if force_final:
        messages.append({
            "role": "user",
            "content": "Please now give me the final analysis based on everything I've told you."
        })

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # same model you use
            messages=messages,
            max_tokens=600,
            temperature=0.4,
        )

        reply = response.choices[0].message.content.strip()

        # ── Check if AI returned final analysis ──
        if reply.startswith("[FINAL_ANALYSIS]"):
            import json, re

            json_str = reply[len("[FINAL_ANALYSIS]"):].strip()

            # Strip accidental markdown fences if model adds them
            json_str = re.sub(r"^```json|^```|```$", "", json_str, flags=re.MULTILINE).strip()

            try:
                analysis = json.loads(json_str)

                # Normalize severity to match your existing extract_severity style
                severity_map = {
                    "low":      "Low",
                    "moderate": "Moderate",
                    "high":     "High",
                    "critical": "Critical"
                }
                raw_sev = analysis.get("severity", "Low").lower()
                analysis["severity"] = severity_map.get(raw_sev, "Low")

                # If emergency detected, override severity
                if analysis.get("is_emergency"):
                    analysis["severity"] = "Critical"

                return {
                    "is_done":        True,
                    "question":       None,
                    "final_analysis": analysis
                }

            except json.JSONDecodeError:
                # JSON parse failed — ask AI to continue instead of crashing
                return {
                    "is_done":        False,
                    "question":       "Could you describe your symptoms in a bit more detail?",
                    "final_analysis": None
                }

        # ── Normal follow-up question ──
        return {
            "is_done":        False,
            "question":       reply,
            "final_analysis": None
        }

    except Exception as e:
        print(f"Groq Follow-Up Error: {e}")
        raise Exception(f"AI follow-up error: {str(e)}")