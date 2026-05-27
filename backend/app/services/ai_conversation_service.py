from app.llm.groq_client import client


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """

You are MediZen AI.

You are an intelligent conversational AI assistant.

Responsibilities:

1. Answer normal general questions naturally.
2. Handle healthcare conversations intelligently.
3. Maintain conversational context.
4. Be friendly and professional.
5. Ask relevant follow-up questions when necessary.
6. Never provide dangerous medical advice.
7. Never prescribe medicines.
8. Encourage professional consultation for severe symptoms.
9. Keep responses conversational and human-like.

IMPORTANT:
- Responses must be AI-generated dynamically.
- Do NOT use static chatbot behavior.
- Do NOT repeat previous questions.
- Understand previous conversation context.

"""


# ─────────────────────────────────────────────
# AI CONVERSATION ENGINE
# ─────────────────────────────────────────────

def generate_ai_response(

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
                    SYSTEM_PROMPT
            }
        ]

        # PREVIOUS CONVERSATION
        messages.extend(
            conversation_history
        )

        # CURRENT USER MESSAGE
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

            temperature=0.5,

            max_tokens=400,
        )

        ai_response = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return ai_response

    except Exception as e:

        print(
            "AI Conversation Error:",
            e
        )

        return (

            "I'm currently unable "
            "to process your request."
        )