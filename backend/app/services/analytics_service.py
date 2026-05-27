from collections import Counter

from app.llm.groq_client import client


# ─────────────────────────────────────────────
# GENERATE HEALTH ANALYTICS
# ─────────────────────────────────────────────

def generate_health_analytics(

    symptom_history: list
):

    try:

        # ─────────────────────────
        # EXTRACT SYMPTOMS
        # ─────────────────────────

        all_symptoms = []

        severity_counts = Counter()

        for item in symptom_history:

            symptom = item.get(
                "symptom",
                ""
            )

            severity = item.get(
                "severity",
                "Moderate"
            )

            all_symptoms.append(
                symptom
            )

            severity_counts[
                severity
            ] += 1

        # ─────────────────────────
        # MOST COMMON SYMPTOMS
        # ─────────────────────────

        symptom_counter = Counter(
            all_symptoms
        )

        common_symptoms = (

            symptom_counter
            .most_common(5)
        )

        # ─────────────────────────
        # AI HEALTH INSIGHTS
        # ─────────────────────────

        history_text = "\n".join(

            [
                f"- {item['symptom']} "
                f"({item['severity']})"

                for item in symptom_history
            ]
        )

        prompt = f"""

You are MediZen AI.

Analyze this healthcare history.

Symptom History:

{history_text}

Your task:

1. Detect recurring symptoms.
2. Explain possible health trends.
3. Explain possible lifestyle concerns.
4. Give preventive suggestions.
5. Encourage medical consultation if needed.

IMPORTANT:
- Keep response professional.
- Do NOT prescribe medicines.
- Keep insights concise.

"""

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",

                    "content": prompt
                }
            ],

            temperature=0.3,

            max_tokens=500,
        )

        ai_insights = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return {

            "success": True,

            "total_cases":
                len(symptom_history),

            "common_symptoms":
                common_symptoms,

            "severity_distribution":
                dict(severity_counts),

            "ai_insights":
                ai_insights
        }

    except Exception as e:

        print(
            "Analytics Error:",
            e
        )

        return {

            "success": False,

            "total_cases": 0,

            "common_symptoms": [],

            "severity_distribution": {},

            "ai_insights":

                "Unable to generate "
                "health analytics."
        }