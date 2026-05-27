from app.services.ai_report_service import (
    generate_ai_report
)

conversation_history = [

    {
        "role": "user",

        "content":
            "I have fever and weakness"
    },

    {
        "role": "assistant",

        "content":
            "Since when?"
    },

    {
        "role": "user",

        "content":
            "5 days"
    }
]

report = generate_ai_report(

    conversation_history=
        conversation_history,

    severity="Moderate"
)

print(report)