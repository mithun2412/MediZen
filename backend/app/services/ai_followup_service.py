import json

from app.llm.groq_client import client


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

FOLLOWUP_SYSTEM_PROMPT = """

You are MediZen AI,
an advanced conversational healthcare assistant.

Your responsibilities:

1. Understand healthcare conversations naturally.
2. Ask intelligent follow-up questions.
3. Maintain conversation context.
4. NEVER repeat previous questions.
5. Ask ONLY ONE follow-up question at a time.
6. Generate short selectable options whenever useful.
7. Decide when enough medical information exists.
8. If enough information exists:
   set report_ready = true.
9. Never prescribe medicines.
10. Encourage professional consultation for severe symptoms.
11. Once report_ready has been reached and a final assessment has been generated,
    DO NOT generate another assessment report.
12. After the report is generated, switch to Q&A mode.
13. Answer questions about the report, symptoms, medical concepts, or recommendations.
14. Do not restart the assessment unless the user clearly starts a new health issue.

IMPORTANT:
- All reasoning must come from AI.
- No hardcoded medical logic.
- Responses should feel human and conversational.
- Keep responses concise and medically relevant.
- Always understand previous messages.

RESPONSE FORMAT:

Return STRICT JSON ONLY.

Example:

{
  "response": "Since when have you had chest pain?",
  "options": [
    "1 day",
    "3 days",
    "1 week",
    "More than 2 weeks"
  ],
  "allow_custom_input": true,
  "report_ready": false
}

If enough information exists:

{
  "response": "Based on your symptoms, your condition may require medical attention.",
  "options": [],
  "allow_custom_input": true,
  "report_ready": true
}

"""


# ─────────────────────────────────────────────
# AI FOLLOW-UP ENGINE
# ─────────────────────────────────────────────

def generate_ai_followup(

    user_input: str,

    conversation_history: list = None
):

    try:

        conversation_history = (
            conversation_history or []
        )

        # ─────────────────────────
        # BUILD CHAT CONTEXT
        # ─────────────────────────

        messages = [

            {
                "role": "system",

                "content":
                    FOLLOWUP_SYSTEM_PROMPT
            }
        ]

        # ADD PREVIOUS HISTORY
        messages.extend(
            conversation_history
        )

        # ADD CURRENT USER MESSAGE
        messages.append({

            "role": "user",

            "content": user_input
        })

        # ─────────────────────────
        # GROQ RESPONSE
        # ─────────────────────────

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=messages,

            temperature=0.3,

            max_tokens=500,
        )

        ai_response = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        # ─────────────────────────
        # CLEAN RESPONSE
        # ─────────────────────────

        ai_response = ai_response.replace(

            "```json",

            ""
        )

        ai_response = ai_response.replace(

            "```",

            ""
        ).strip()

        # ─────────────────────────
        # PARSE JSON
        # ─────────────────────────

        print("\n===== RAW AI RESPONSE =====")
        print(repr(ai_response))
        print("===========================\n")

        try:

            parsed = json.loads(
                ai_response
            )

        except Exception as e:

            print("JSON PARSE ERROR:", e)

            return {

                "response":
                    ai_response
                    if ai_response
                    else "Could you provide a little more information?",

                "options": [],

                "allow_custom_input": True,

                "report_ready": False
            }

        return {

            "response":

                parsed.get(
                    "response",
                    ""
                ),

            "options":

                parsed.get(
                    "options",
                    []
                ),

            # ALWAYS ALLOW USER INPUT
            "allow_custom_input":

                parsed.get(
                    "allow_custom_input",
                    True
                ),

            "report_ready":

                parsed.get(
                    "report_ready",
                    False
                )
        }

    except Exception as e:

        print(
            "AI Followup Error:",
            e
        )

        return {

            "response":

                "I'm sorry, I'm unable "
                "to continue the healthcare "
                "conversation right now.",

            "options": [],

            "allow_custom_input": True,

            "report_ready": False
        }