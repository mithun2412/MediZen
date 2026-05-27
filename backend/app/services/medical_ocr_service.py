import cv2
import pytesseract

from PIL import Image

from app.llm.groq_client import client


# ─────────────────────────────────────────────
# TESSERACT PATH (WINDOWS)
# ─────────────────────────────────────────────

pytesseract.pytesseract.tesseract_cmd = (

    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


# ─────────────────────────────────────────────
# OCR + AI ANALYSIS
# ─────────────────────────────────────────────

def analyze_medical_report_image(

    image_path: str
):

    try:

        # ─────────────────────────
        # READ IMAGE
        # ─────────────────────────

        image = cv2.imread(
            image_path
        )

        if image is None:

            raise Exception(
                "Unable to read image."
            )

        # ─────────────────────────
        # OCR EXTRACTION
        # ─────────────────────────

        extracted_text = (

            pytesseract.image_to_string(
                image
            )
        )

        # CLEAN TEXT
        extracted_text = (
            extracted_text.strip()
        )

        # ─────────────────────────
        # VALIDATION
        # ─────────────────────────

        if len(extracted_text) < 20:

            return {

                "success": False,

                "analysis":

                    "Unable to detect "
                    "medical report text.",

                "extracted_text": ""
            }

        # ─────────────────────────
        # AI ANALYSIS
        # ─────────────────────────

        prompt = f"""

You are MediZen AI.

A user uploaded a medical report image.

Extracted OCR text:

{extracted_text}

Your responsibilities:

1. Explain the medical report clearly.
2. Explain abnormal values if present.
3. Explain possible meaning.
4. Explain precautions.
5. Explain when doctor consultation is needed.
6. Reject unrelated/non-medical reports.

IMPORTANT:
- Do NOT prescribe medicines.
- Keep response medically informative.
- Keep explanation user-friendly.
- Explain values in simple terms.

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

            max_tokens=700,
        )

        ai_analysis = (

            response
            .choices[0]
            .message
            .content
            .strip()
        )

        # ─────────────────────────
        # RETURN
        # ─────────────────────────

        return {

            "success": True,

            "analysis":
                ai_analysis,

            "extracted_text":
                extracted_text
        }

    except Exception as e:

        print(
            "Medical OCR Error:",
            e
        )

        return {

            "success": False,

            "analysis":

                "Unable to analyze "
                "medical report.",

            "extracted_text": ""
        }