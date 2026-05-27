from app.services.ai_conversation_service import (
    generate_ai_response
)

response = generate_ai_response(

    user_input=
    "I have chest pain",

    conversation_history=[]
)

print(response)