from app.services.ai_severity_service import (
    analyze_severity
)

conversation_history = [

    {
        "role": "user",

        "content":
            "I have chest pain"
    },

    {
        "role": "assistant",

        "content":
            "Since when?"
    },

    {
        "role": "user",

        "content":
            "1 week with breathing difficulty"
    }
]

result = analyze_severity(
    conversation_history
)

print(result)