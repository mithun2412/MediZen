from typing import List, Dict, Any, Optional
import json
from app.llm.groq_client import client

POST_REPORT_SYSTEM_PROMPT = """
You are MediZen AI, a healthcare assistant for post-report questions.

You answer questions about the health assessment report that was generated.

RULES:
1. Use the report content to answer questions
2. If the question is about symptoms, refer to the information in the report
3. If the question is about recommendations, reference the report's recommendations
4. Be helpful and informative
5. If you don't know the answer, suggest consulting a healthcare professional
"""

def clean_messages_for_api(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Clean messages to remove fields that are not supported by the API.
    """
    cleaned = []
    for msg in messages:
        cleaned_msg = {
            "role": msg.get("role", ""),
            "content": msg.get("content", "")
        }
        if cleaned_msg["role"] and cleaned_msg["content"]:
            cleaned.append(cleaned_msg)
    return cleaned

def generate_post_report_answer(
    user_input: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generate answers for post-report questions with follow-up options.
    """
    try:
        conversation_history = conversation_history or []
        
        # Clean conversation history for API
        cleaned_history = clean_messages_for_api(conversation_history)
        
        messages = [
            {"role": "system", "content": POST_REPORT_SYSTEM_PROMPT}
        ]
        
        # Add cleaned conversation history (last 10 messages)
        if cleaned_history:
            for msg in cleaned_history[-10:]:
                messages.append(msg)
        
        # Add the current user question
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Get response
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Generate follow-up questions
        followup_options = generate_post_report_followups(
            cleaned_history, 
            user_input, 
            ai_response
        )
        
        return {
            "response": ai_response,
            "followup_options": followup_options
        }
        
    except Exception as e:
        print(f"Post Report Answer Error: {e}")
        return {
            "response": "I'm sorry, I'm unable to answer your question right now. Please consult a healthcare professional.",
            "followup_options": [
                "Can you explain the report in simpler terms?",
                "What should I do next?",
                "Should I schedule a follow-up appointment?",
                "Are there any risks I should be aware of?"
            ]
        }

def generate_post_report_followups(
    conversation_history: List[Dict[str, Any]],
    user_question: str,
    ai_response: str
) -> List[str]:
    """
    Generate follow-up questions after a report has been generated.
    """
    try:
        # Prepare context from conversation history
        context = ""
        for msg in conversation_history[-6:]:
            if msg.get("role") == "user":
                context += f"User: {msg.get('content')}\n"
            elif msg.get("role") == "assistant":
                context += f"Assistant: {msg.get('content')}\n"

        followup_prompt = f"""
Based on this healthcare conversation and the user's latest question, generate 3-4 relevant follow-up questions.

Context:
{context}

User's Question: {user_question}

AI Response: {ai_response}

Generate 3-4 helpful follow-up questions related to the health report discussion.
Return ONLY a JSON array of strings.
Example: ["What are the treatment options?", "How can I manage these symptoms at home?", "Should I get a second opinion?"]
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You generate relevant medical follow-up questions. Return ONLY a JSON array of strings."},
                {"role": "user", "content": followup_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        followup_text = response.choices[0].message.content.strip()
        followup_text = followup_text.replace("```json", "").replace("```", "").strip()

        try:
            followup_options = json.loads(followup_text)
            if isinstance(followup_options, list) and len(followup_options) > 0:
                return followup_options[:4]
        except:
            pass

        return [
            "Can you explain this in more detail?",
            "What are the next steps I should take?",
            "How serious is this condition?",
            "Should I consult a specialist?"
        ]

    except Exception as e:
        print(f"Error generating post-report follow-ups: {e}")
        return [
            "Can you explain this in more detail?",
            "What are the next steps?",
            "Should I consult a specialist?",
            "Are there any lifestyle changes I should make?"
        ]