from app.llm.groq_client import client


# ─────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────

REPORT_SYSTEM_PROMPT = """

You are MediZen AI.

You are responsible for generating
professional healthcare reports.

Generate a well-structured healthcare report.

The report should contain:

1. Symptom Summary
2. Severity Level
3. Clinical Observation
4. Home Care Recommendations
5. Emergency Guidance
6. Suggested Next Steps

IMPORTANT:

- Use conversational history context.
- Keep the report professional.
- Do NOT prescribe medicines.
- Encourage doctor consultation for severe symptoms.
- Generate clean readable formatting.
- Avoid unnecessary repetition.
- Be concise but medically informative.

"""


# ─────────────────────────────────────────────
# AI REPORT GENERATION
# ─────────────────────────────────────────────

def generate_ai_report(

    conversation_history: list,

    severity: str
):

    try:

        messages = [

            {
                "role": "system",

                "content":
                    REPORT_SYSTEM_PROMPT
            }
        ]

        # PREVIOUS CONVERSATION
        messages.extend(
            conversation_history
        )

        # FINAL REPORT REQUEST
        messages.append({

            "role": "user",

            "content": f"""

Generate a complete healthcare report.

Severity Level:
{severity}

The report should contain:

- Symptom Summary
- Severity Explanation
- Clinical Observation
- Home Remedies
- Emergency Guidance
- Suggested Next Steps

"""
        })

        # ─────────────────────────
        # GROQ RESPONSE
        # ─────────────────────────

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=messages,

            temperature=0.3,

            max_tokens=700,
        )

        report = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return report

    except Exception as e:

        print(
            "AI Report Error:",
            e
        )

        return (

            "Unable to generate "
            "healthcare report."
        )