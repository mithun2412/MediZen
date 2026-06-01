import json

from app.llm.groq_client import client


POST_REPORT_SYSTEM_PROMPT = """
You are MediZen AI.

A healthcare assessment report has already been generated.

Your responsibilities:

1. Answer the user's healthcare questions.
2. Explain medical terms mentioned in the report.
3. Explain severity and recommendations.
4. Maintain conversation context.
5. DO NOT generate another healthcare report.
6. DO NOT restart symptom assessment.
7. DO NOT ask follow-up assessment questions.
8. Answer naturally and conversationally.

Return STRICT JSON ONLY.

Example:

{
  "response": "Musculoskeletal chest pain is pain originating from muscles, joints, cartilage, or ligaments of the chest wall.",
  "options": [],
  "report_ready": true
}
"""


def generate_post_report_answer(
    user_input: str,
    conversation_history: list = None
):

    try:

        conversation_history = (
            conversation_history or []
        )

        messages = [

            {
                "role": "system",
                "content":
                    POST_REPORT_SYSTEM_PROMPT
            }
        ]

        messages.extend(
            conversation_history
        )

        messages.append({

            "role": "user",

            "content": user_input
        })

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=messages,

            temperature=0.3,

            max_tokens=500
        )

        ai_response = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

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

            "response":
                parsed.get(
                    "response",
                    ""
                ),

            "options": [],

            "allow_custom_input":
                True,

            "report_ready":
                True
        }

    except Exception as e:

        print(
            "Post Report Error:",
            e
        )

        return {

            "response":
                "Sorry, I couldn't answer that question.",

            "options": [],

            "allow_custom_input":
                True,

            "report_ready":
                True
        }