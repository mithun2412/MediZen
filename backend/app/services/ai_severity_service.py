from typing import List, Dict, Any

def analyze_severity(conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze the severity of symptoms based on conversation history.
    """
    try:
        # Extract all user messages
        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
        all_text = " ".join([msg.get("content", "").lower() for msg in user_messages])
        
        # Define severity keywords
        high_risk_keywords = [
            "severe", "emergency", "chest pain", "heart", "stroke", "bleeding",
            "unconscious", "difficulty breathing", "severe pain", "7", "8", "9", "10"
        ]
        
        moderate_risk_keywords = [
            "moderate", "pain", "fever", "infection", "injury", "4", "5", "6"
        ]
        
        low_risk_keywords = [
            "mild", "minor", "slight", "small", "1", "2", "3"
        ]
        
        # Check for risk level
        high_score = sum(1 for keyword in high_risk_keywords if keyword in all_text)
        moderate_score = sum(1 for keyword in moderate_risk_keywords if keyword in all_text)
        low_score = sum(1 for keyword in low_risk_keywords if keyword in all_text)
        
        # Determine severity
        if high_score >= 1:
            severity = "HIGH"
            reason = "High-risk symptoms detected including chest pain, severe symptoms, or emergency indicators."
        elif moderate_score >= 2:
            severity = "MODERATE"
            reason = "Moderate symptoms detected that require medical attention."
        else:
            severity = "LOW"
            reason = "Mild symptoms detected. Continue monitoring."
        
        return {
            "severity": severity,
            "reason": reason
        }
        
    except Exception as e:
        print(f"Severity Analysis Error: {e}")
        return {
            "severity": "MODERATE",
            "reason": "Unable to analyze severity. Please consult a healthcare professional."
        }