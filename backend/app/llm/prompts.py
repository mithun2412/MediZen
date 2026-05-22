# ─────────────────────────────────────────────
# QUESTION REFINEMENT PROMPT
# ─────────────────────────────────────────────

QUESTION_REFINE_SYSTEM = """
You are MediZen AI.

Behave like ChatGPT or Claude.

RULES:
- Ask ONE question at a time
- Sound natural and caring
- Keep responses short
- Avoid robotic language
- Ask conversationally
- Sound like a healthcare assistant

Examples:
"Understood. When did this start?"
"Got it. Is the pain sharp or dull?"
"Are you also feeling dizzy or tired?"

Return ONLY the question.
"""


# ─────────────────────────────────────────────
# FINAL ANALYSIS PROMPT
# ─────────────────────────────────────────────

FINAL_ANALYSIS_SYSTEM = """
You are MediZen AI.

You are an advanced healthcare AI assistant.

IMPORTANT RULES:

- Return ONLY valid JSON
- No markdown
- No explanations outside JSON
- No ```json blocks
- No extra text

Return EXACTLY in this format:

{
  "possible_conditions": [
    "Condition name"
  ],

  "severity": "Low|Moderate|High|Critical",

  "is_emergency": false,

  "medications": [
    {
      "name": "",
      "purpose": "",
      "dosage": "",
      "warning": ""
    }
  ],

  "remedies": [
    ""
  ],

  "when_to_see_doctor": "",

  "doctor_advice": "",

  "tests": []
}

Use:
- symptom duration
- severity
- fever
- stress
- medication usage
- frequency

to generate medical reasoning.
"""



CLINICAL_QUESTIONS = {

    "headache": [

        {
            "key": "duration",
            "question": "How long have you been experiencing the headache?",
            "type": "duration"
        },

        {
            "key": "severity",
            "question": "How severe is the headache on a scale of 1-10?",
            "type": "severity"
        },

        {
            "key": "frequency",
            "question": "Is the headache constant or does it come and go?",
            "type": "frequency"
        },

        {
            "key": "vision",
            "question": "Do you have blurred vision or light sensitivity?",
            "type": "yes_no"
        },

        {
            "key": "nausea",
            "question": "Are you experiencing nausea or vomiting?",
            "type": "yes_no"
        }
    ],

    "chest pain": [

        {
            "key": "duration",
            "question": "When did the chest pain start?",
            "type": "duration"
        },

        {
            "key": "severity",
            "question": "How severe is the chest pain?",
            "type": "severity"
        },

        {
            "key": "breathing",
            "question": "Are you having difficulty breathing?",
            "type": "yes_no"
        },

        {
            "key": "location",
            "question": "Does the pain spread to your arm, neck, or jaw?",
            "type": "yes_no"
        },

        {
            "key": "dizziness",
            "question": "Are you feeling dizzy or sweating excessively?",
            "type": "yes_no"
        }
    ],

    "fever": [

        {
            "key": "duration",
            "question": "How long have you had fever?",
            "type": "duration"
        },

        {
            "key": "temperature",
            "question": "What is your temperature if known?",
            "type": "temperature"
        },

        {
            "key": "cough",
            "question": "Do you also have cough or sore throat?",
            "type": "yes_no"
        },

        {
            "key": "fatigue",
            "question": "Are you feeling weak or fatigued?",
            "type": "yes_no"
        }
    ],


   

    "mental_health": [

        {
            "key": "stress",
            "question": "How stressed or anxious are you feeling?",
            "type": "severity"
        },

        {
            "key": "sleep",
            "question": "Are you sleeping properly?",
            "type": "yes_no"
        },

        {
            "key": "panic",
            "question": "Have you experienced panic attacks recently?",
            "type": "yes_no"
        },

        {
            "key": "focus",
            "question": "Are you finding it difficult to focus?",
            "type": "yes_no"
        }
    ],

    "default": [

        {
            "key": "duration",
            "question": "When did the symptoms start?",
            "type": "duration"
        },

        {
            "key": "severity",
            "question": "How severe are the symptoms?",
            "type": "severity"
        },

        {
            "key": "frequency",
            "question": "Are the symptoms constant or occasional?",
            "type": "frequency"
        }
    ]
}