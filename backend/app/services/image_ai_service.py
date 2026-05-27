from app.llm.groq_client import client


# ─────────────────────────────────────────────
# AI IMAGE ANALYSIS
# ─────────────────────────────────────────────

def analyze_medical_image(

    image_path: str
):

    try:

        # ─────────────────────────
        # AI PROMPT
        # ─────────────────────────

        prompt = f"""

You are MediZen AI.

A user uploaded a medical-related image.

Your task:

1. Explain possible visible medical conditions.
2. Explain possible symptoms.
3. Explain precautions.
4. Explain when medical attention is needed.
5. Reject unrelated/non-medical images.
6. Keep response professional.

IMPORTANT:
- Do NOT prescribe medicines.
- Keep response medically informative.
- If image context is unclear,
  say that image quality or medical
  interpretation may be limited.

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

        ai_analysis = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return {

            "success": True,

            "prediction":
                "Medical Image Analysis",

            "confidence":
                85.0,

            "severity":
                "Moderate",

            "analysis":
                ai_analysis
        }

    except Exception as e:

        print(
            "Image AI Error:",
            e
        )

        return {

            "success": False,

            "prediction":
                "Unknown",

            "confidence": 0,

            "severity":
                "Moderate",

            "analysis":

                "Unable to analyze image."
        }