import os
from PIL import Image
from dotenv import load_dotenv
from google import genai
from groq import Groq

# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GEMINI_API_KEY:
    raise Exception("GEMINI_API_KEY not found")

if not GROQ_API_KEY:
    raise Exception("GROQ_API_KEY not found")

# =====================================================
# CLIENTS
# =====================================================

gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

groq_client = Groq(
    api_key=GROQ_API_KEY
)

# =====================================================
# IMAGE ANALYSIS USING GEMINI VISION
# =====================================================

def analyze_image(image_path):

    image = Image.open(image_path)

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            """
            Analyze this medical image carefully.

            Return:
            1. Visible findings
            2. Possible conditions
            3. Severity indicators
            4. Skin appearance
            5. Signs of infection if any

            Do NOT provide a diagnosis.
            """,
            image
        ]
    )

    return response.text


# =====================================================
# MEDICAL REASONING USING GROQ
# =====================================================

def get_medical_explanation(image_description):

    prompt = f"""
You are MediZen AI.

Medical Image Analysis:

{image_description}

Provide:

1. What is visible
2. Possible causes
3. Home care recommendations
4. Whether the condition appears mild, moderate, or severe
5. When the user should consult a doctor

Important:
- Do not make a definitive diagnosis.
- Clearly mention uncertainty.
- Use patient-friendly language.
"""

    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# =====================================================
# MAIN PIPELINE
# =====================================================

def analyze_medical_image(image_path):

    print("Analyzing image with Gemini Vision...")

    image_description = analyze_image(image_path)

    print("\n=== GEMINI IMAGE DESCRIPTION ===\n")
    print(image_description)

    print("\nGenerating medical explanation using Groq...\n")

    final_response = get_medical_explanation(
        image_description
    )

    return {
        "image_description": image_description,
        "medical_response": final_response
    }


# =====================================================
# TEST
# =====================================================

if __name__ == "__main__":

    IMAGE_PATH = "test_image.jpg"  # Change this

    result = analyze_medical_image(
        IMAGE_PATH
    )

    print("\n==============================")
    print("FINAL MEDIZEN RESPONSE")
    print("==============================\n")

    print(result["medical_response"])