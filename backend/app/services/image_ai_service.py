from app.llm.groq_client import client

from app.services.vision_service import (
    analyze_image_with_vision
)


def analyze_medical_image(

    image_path: str
):

    try:

        # Vision AI

        vision_result = (

            analyze_image_with_vision(
                image_path
            )
        )

        prompt = f"""

You are MediZen AI.

Medical Image Findings:

{vision_result}

Generate a report with:

1. Possible condition
2. Symptoms
3. Severity
4. Precautions
5. When medical attention is needed

Do not prescribe medicines.

"""

        response = client.chat.completions.create(

            model=
            "llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",

                    "content":
                        prompt
                }
            ],

            temperature=0.3,

            max_tokens=600
        )

        report = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return {

            "success": True,

            "prediction":
                "Vision AI Analysis",

            "confidence":
                95,

            "severity":
                "Moderate",

            "analysis":
                report,

            "vision_analysis":
                vision_result
        }

    except Exception as e:

        print(
            "Vision AI Error:",
            e
        )

        return {

            "success": False,

            "prediction":
                "Unknown",

            "confidence":
                0,

            "severity":
                "Unknown",

            "analysis":
                str(e)
        }