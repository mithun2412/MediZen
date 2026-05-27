import json

from app.llm.groq_client import client


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

SEVERITY_SYSTEM_PROMPT = """

You are MediZen AI.

You are responsible for analyzing
healthcare conversation severity.

Your task:

1. Analyze symptoms contextually.
2. Detect healthcare urgency.
3. Identify emergencies.
4. Classify severity into:

- Low
- Moderate
- High

IMPORTANT:

- Use contextual medical reasoning.
- Do NOT use hardcoded logic.
- Understand previous conversation context.
- Consider duration and symptom progression.
- Severe symptoms should escalate severity.
- Mild symptoms should remain low severity.

Return STRICT JSON ONLY.

Example:

{
  "severity": "Moderate",
  "reason": "Symptoms suggest possible viral infection requiring monitoring."
}

"""


# ─────────────────────────────────────────────
# AI SEVERITY ANALYSIS
# ─────────────────────────────────────────────

def analyze_severity(

    conversation_history: list
):

    try:

        messages = [

            {
                "role": "system",

                "content":
                    SEVERITY_SYSTEM_PROMPT
            }
        ]

        messages.extend(
            conversation_history
        )

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=messages,

            temperature=0.2,

            max_tokens=200,
        )

        ai_response = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        # CLEAN JSON
        ai_response = ai_response.replace(
            "```json",
            ""
        )

        ai_response = ai_response.replace(
            "```",
            ""
        ).strip()

        parsed = json.loads(
            ai_response
        )

        return {

            "severity":

                parsed.get(
                    "severity",
                    "Moderate"
                ),

            "reason":

                parsed.get(
                    "reason",
                    ""
                )
        }

    except Exception as e:

        print(
            "Severity Error:",
            e
        )

        return {

            "severity": "Moderate",

            "reason":

                "Unable to determine severity."
        }