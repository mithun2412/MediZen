import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.llm.groq_client import client

def generate_ai_report(
    conversation_history: List[Dict[str, Any]],
    severity: str = "MODERATE",
    hospitals: List[Dict[str, Any]] = None,
    google_maps_link: str = None
) -> str:
    """
    Generate a comprehensive medical report.
    """
    try:
        # Extract symptoms data
        symptoms_data = extract_symptoms_data(conversation_history)
        
        # Generate the report
        report = generate_complete_report(
            symptoms_data,
            severity,
            hospitals or [],
            google_maps_link
        )
        
        return report
            
    except Exception as e:
        print(f"Report Generation Error: {e}")
        return generate_fallback_report(conversation_history, severity)

def extract_symptoms_data(conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract structured symptom data from conversation history."""
    symptoms_data = {
        "primary_symptom": "Not specified",
        "duration": "Not specified",
        "severity": "Not specified",
        "severity_rating": None,
        "associated_symptoms": [],
        "medical_history": "None reported",
        "pain_type": "Not specified",
        "location": "Not specified",
        "pattern": "Not specified"
    }
    
    user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]
    
    for i, msg in enumerate(user_messages):
        content = msg.get("content", "").lower()
        original = msg.get("content", "")
        
        # Primary symptom (first user message)
        if i == 0 and "symptom" not in symptoms_data["primary_symptom"]:
            if "have" in content or "feeling" in content or "experiencing" in content:
                parts = original.split("have", 1) if "have" in content else original.split("feeling", 1) if "feeling" in content else [original]
                if len(parts) > 1:
                    symptoms_data["primary_symptom"] = parts[1].strip()[:100]
            else:
                symptoms_data["primary_symptom"] = original[:100]
        
        # Duration
        duration_keywords = ["day", "week", "month", "year", "hour", "for", "since"]
        if any(keyword in content for keyword in duration_keywords):
            for sentence in original.split('.'):
                if any(keyword in sentence.lower() for keyword in duration_keywords):
                    symptoms_data["duration"] = sentence.strip()
                    break
        
        # Severity rating
        import re
        severity_match = re.search(r'\b([1-9]|10)\b', content)
        if severity_match:
            symptoms_data["severity_rating"] = int(severity_match.group(1))
        
        # Associated symptoms
        if "also" in content or "additional" in content or "plus" in content:
            for sentence in original.split('.'):
                if any(keyword in sentence.lower() for keyword in ["also", "additional", "plus"]):
                    if len(sentence.strip()) > 10:
                        symptoms_data["associated_symptoms"].append(sentence.strip())
        
        # Medical history
        history_keywords = ["history", "medical", "condition", "diagnosed", "diabetes", "heart", "blood pressure", "asthma"]
        if any(keyword in content for keyword in history_keywords):
            for sentence in original.split('.'):
                if any(keyword in sentence.lower() for keyword in history_keywords):
                    symptoms_data["medical_history"] = sentence.strip()
                    break
        
        # Pain type
        pain_keywords = ["sharp", "dull", "burning", "aching", "stabbing", "throbbing"]
        for keyword in pain_keywords:
            if keyword in content:
                symptoms_data["pain_type"] = keyword.capitalize()
                break
        
        # Location
        location_keywords = ["chest", "head", "back", "stomach", "abdomen", "leg", "arm", "neck", "shoulder"]
        for keyword in location_keywords:
            if keyword in content:
                symptoms_data["location"] = keyword.capitalize()
                break
        
        # Pattern
        pattern_keywords = ["comes and goes", "constant", "intermittent", "worse when", "better when"]
        for keyword in pattern_keywords:
            if keyword in content:
                symptoms_data["pattern"] = keyword.capitalize()
                break
    
    return symptoms_data

def generate_complete_report(
    symptoms: Dict[str, Any],
    severity: str,
    hospitals: List[Dict[str, Any]],
    google_maps_link: str
) -> str:
    """Generate the complete report with all sections."""
    
    severity_config = {
        "HIGH": {"icon": "🔴", "label": "HIGH RISK — Prompt Medical Evaluation Recommended"},
        "MODERATE": {"icon": "🟡", "label": "MODERATE RISK — Medical Evaluation Recommended"},
        "LOW": {"icon": "🟢", "label": "LOW RISK — Monitor Symptoms"}
    }
    
    severity_info = severity_config.get(severity.upper(), severity_config["MODERATE"])
    
    report = f"""
# MediZen AI Symptom Assessment Report

## Information Collected

| Category | Details |
|----------|---------|
| **Primary Symptom** | {symptoms.get('primary_symptom', 'Not specified')} |
| **Pain Type** | {symptoms.get('pain_type', 'Not specified')} |
| **Location** | {symptoms.get('location', 'Not specified')} |
| **Duration** | {symptoms.get('duration', 'Not specified')} |
| **Pattern** | {symptoms.get('pattern', 'Not specified')} |
| **Severity** | {symptoms.get('severity_rating', 'N/A')}/10 |
| **Associated Symptoms** | {', '.join(symptoms.get('associated_symptoms', ['None'])) if symptoms.get('associated_symptoms') else 'None'} |
| **Medical History** | {symptoms.get('medical_history', 'None reported')} |

## Severity Assessment

### {severity_info['icon']} {severity_info['label']}

**Because you have:**

"""
    # Build severity reasoning
    reasons = []
    if symptoms.get('medical_history') and 'heart' in symptoms.get('medical_history', '').lower():
        reasons.append("A history of heart disease")
    if symptoms.get('severity_rating') and symptoms['severity_rating'] >= 7:
        reasons.append(f"Reported symptom intensity of {symptoms['severity_rating']}/10")
    if symptoms.get('duration'):
        reasons.append(f"Symptoms persisting for {symptoms['duration']}")
    if symptoms.get('associated_symptoms'):
        reasons.append(f"Associated symptoms: {', '.join(symptoms['associated_symptoms'][:2])}")
    
    if not reasons:
        reasons = ["Symptoms described with concerning characteristics"]
    
    for reason in reasons:
        report += f"- {reason}\n"
    
    primary_symptom = symptoms.get('primary_symptom', 'the reported symptom')
    report += f"""
**The cause of {primary_symptom} cannot be determined without an in-person clinical assessment.**

## Possible Causes

*These are possibilities, not a diagnosis:*

"""
    causes = generate_possible_causes(symptoms)
    for cause in causes:
        report += f"- {cause}\n"
    
    report += f"""
**The possibilities above are not a diagnosis. A clinician can assess your symptoms and medical history in context.**

## Recommended Action

### Seek Medical Care Soon

You should arrange evaluation by a healthcare professional within the next {get_timeframe(severity)}, and sooner if symptoms worsen.

### Seek Emergency Care Immediately If You Develop:

"""
    emergency_signs = generate_emergency_signs(symptoms)
    for sign in emergency_signs:
        report += f"- {sign}\n"
    
    report += f"""
## Precautions

"""
    precautions = generate_precautions_list(symptoms)
    for precaution in precautions:
        report += f"✅ {precaution}\n"
    
    referral_specialty = hospitals[0].get("recommended_specialty", "General Medicine") if hospitals else "General Medicine"
    report += f"""
## Specialist Recommendation

Based on the symptoms described, consider starting with **{referral_specialty}** care.

{generate_specialist(symptoms)}

## Find Nearby Care

Use the link below to search for nearby hospitals and clinics that offer **{referral_specialty}** services.

📍 [Find nearby {referral_specialty} care]({google_maps_link if google_maps_link else 'https://www.google.com/maps/search/hospitals/'})

## Overall Assessment

### Risk Level: {severity.upper()}

"""
    overall = generate_overall_assessment(symptoms, severity)
    report += overall
    
    report += f"""
---

*This report was generated by MediZen AI on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
"""
    
    return report

def generate_possible_causes(symptoms: Dict[str, Any]) -> List[str]:
    """Generate possible causes based on symptoms."""
    primary = symptoms.get('primary_symptom', '').lower()
    
    if 'chest' in primary:
        return [
            "Heart-related chest pain (angina or other cardiac conditions)",
            "Respiratory infection affecting the lungs or airways",
            "Inflammation of the chest wall muscles or ribs",
            "Acid reflux (GERD)",
            "Pleuritic chest pain (pain related to lung lining inflammation)"
        ]
    elif 'head' in primary or 'headache' in primary:
        return [
            "Tension headaches or migraines",
            "Sinusitis or sinus infection",
            "Stress-related headaches",
            "Eye strain or vision problems",
            "Dehydration or lack of sleep"
        ]
    elif 'stomach' in primary:
        return [
            "Food poisoning or gastroenteritis",
            "Acid reflux or ulcers",
            "Irritable bowel syndrome",
            "Food allergies or intolerances",
            "Gallstones or kidney stones"
        ]
    elif 'fever' in primary:
        return [
            "Viral or bacterial infection",
            "Influenza or common cold",
            "Urinary tract infection",
            "Pneumonia or respiratory infection",
            "Autoimmune conditions"
        ]
    else:
        return [
            "Infections (viral or bacterial)",
            "Inflammatory conditions",
            "Stress or anxiety-related symptoms",
            "Lifestyle factors (diet, sleep, exercise)",
            "Underlying medical conditions"
        ]

def generate_emergency_signs(symptoms: Dict[str, Any]) -> List[str]:
    """Generate emergency warning signs."""
    primary = symptoms.get('primary_symptom', '').lower()
    if 'head' in primary or 'migraine' in primary:
        return [
            "A sudden, severe 'worst-ever' headache",
            "New weakness, numbness, confusion, fainting, or trouble speaking",
            "New loss of vision, double vision, or trouble walking",
            "Headache after a significant head injury",
            "Fever with a stiff neck or a rapidly worsening headache",
        ]
    if any(term in primary for term in ['stomach', 'abdomen', 'abdominal', 'belly']):
        return [
            "Severe or rapidly worsening abdominal pain",
            "Repeated vomiting or inability to keep fluids down",
            "Blood in vomit or stool, or black/tarry stool",
            "A rigid or very tender abdomen, fainting, or confusion",
            "Pregnancy with abdominal pain or vaginal bleeding",
        ]
    if any(term in primary for term in ['breath', 'cough', 'fever']):
        return [
            "Severe difficulty breathing, blue lips, or inability to speak full sentences",
            "Chest pain, confusion, fainting, or new severe weakness",
            "High fever with stiff neck, rash, or severe dehydration",
            "Symptoms that worsen quickly or do not improve as expected",
        ]
    signs = [
        "Chest pressure, squeezing, or heaviness",
        "Pain spreading to the arm, shoulder, neck, jaw, or back",
        "Severe shortness of breath",
        "Fainting or near-fainting",
        "Cold sweats",
        "Sudden severe worsening of pain",
        "Blue lips or difficulty breathing"
    ]
    return signs

def generate_precautions_list(symptoms: Dict[str, Any]) -> List[str]:
    """Generate precautions."""
    primary = symptoms.get('primary_symptom', '').lower()
    
    precautions = [
        "Avoid strenuous exercise until evaluated.",
        "Stay hydrated.",
        "Avoid smoking or vaping.",
        "Get adequate rest."
    ]
    
    if 'chest' in primary:
        precautions = [
            "Avoid strenuous exercise until evaluated.",
            "Take prescribed heart medications exactly as directed.",
            "Stay hydrated.",
            "Avoid smoking or vaping.",
            "Get adequate rest.",
            "Monitor whether the pain occurs during activity or at rest."
        ]
    elif 'head' in primary or 'migraine' in primary:
        precautions = [
            "Rest in a quiet, dimly lit room if that helps.",
            "Drink fluids and eat regular meals if you can.",
            "Avoid driving or operating machinery if you feel dizzy or have vision changes.",
            "Keep a note of triggers, onset, and changes in symptoms.",
        ]
    elif any(term in primary for term in ['stomach', 'abdomen', 'abdominal', 'belly']):
        precautions = [
            "Take small sips of water or oral rehydration fluid if tolerated.",
            "Avoid alcohol and foods that make symptoms worse.",
            "Avoid taking new medicines unless a clinician or pharmacist advises it.",
            "Monitor pain location, fever, vomiting, and bowel changes.",
        ]
    
    return precautions

def generate_specialist(symptoms: Dict[str, Any]) -> str:
    """Generate specialist recommendation."""
    primary = symptoms.get('primary_symptom', '').lower()
    
    if 'chest' in primary:
        return "**Cardiologist**\nOr an emergency physician if symptoms worsen"
    elif 'head' in primary:
        return "**Neurologist**\nOr a general physician for initial evaluation"
    elif 'stomach' in primary:
        return "**Gastroenterologist**\nOr a general physician for initial evaluation"
    else:
        return "**General Physician**\nFor initial evaluation and referral to a specialist if needed"

def get_timeframe(severity: str) -> str:
    """Get recommended timeframe based on severity."""
    timeframes = {
        "HIGH": "24 hours",
        "MODERATE": "24-48 hours",
        "LOW": "1 week"
    }
    return timeframes.get(severity.upper(), "24-48 hours")

def generate_overall_assessment(symptoms: Dict[str, Any], severity: str) -> str:
    """Generate overall assessment."""
    primary = symptoms.get('primary_symptom', '').lower()
    
    if 'chest' in primary:
        return """Because chest pain with a history of heart disease can sometimes indicate a serious cardiac condition, I would not recommend ignoring this symptom. A medical evaluation is warranted even though the pain has been occurring intermittently.

If you'd like, I can continue with a more detailed cardiac assessment by asking additional questions (what triggers the pain, age, medications, whether it occurs during exertion, etc.)."""
    else:
        return f"""Based on your symptoms, this is a {severity.lower()}-risk situation. Please follow the recommended actions above and consult a healthcare professional for proper evaluation."""

def generate_fallback_report(conversation_history: List[Dict[str, Any]], severity: str) -> str:
    """Generate a fallback report."""
    return f"""
# MediZen AI Symptom Assessment Report

## Information Collected

Based on your conversation, the following information was gathered:
- Your symptoms have been analyzed
- Severity assessment: {severity}

## Severity Assessment

**{severity} RISK — Please consult a healthcare professional**

## Recommended Action

Please seek medical attention for proper evaluation.

## Precautions

- Monitor your symptoms
- Stay hydrated
- Get adequate rest
- Seek immediate medical attention if symptoms worsen

---

*This report was generated by MediZen AI. Please consult a healthcare professional for accurate diagnosis.*
"""

def generate_pdf_report(report_text: str) -> Dict[str, Any]:
    """Generate PDF from report text."""
    # This function should be in pdf_service.py
    # Returning placeholder
    return {
        "success": True,
        "filename": f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    }
