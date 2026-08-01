import PyPDF2
import re
from typing import Dict, Any, List
from datetime import datetime

def process_report_pdf(file_path: str) -> Dict[str, Any]:
    """
    Process a PDF report and extract information
    """
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        
        # Extract parameters
        parameters = extract_medical_parameters(text)
        
        # Generate summary
        summary = generate_summary(text, parameters)
        
        return {
            "success": True,
            "report_id": int(datetime.now().timestamp()),
            "full_text": text,
            "parameters_count": len(parameters),
            "parameters": parameters,
            "summary": summary
        }
        
    except Exception as e:
        print(f"Process PDF Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "report_id": None,
            "parameters_count": 0,
            "summary": "Failed to process PDF"
        }

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file
    """
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"PDF Text Extraction Error: {e}")
        return ""

def extract_medical_parameters(text: str) -> List[Dict[str, Any]]:
    """
    Extract medical parameters from text
    """
    parameters = []
    
    # Common medical parameters to look for
    param_patterns = {
        "blood_pressure": r"Blood\s*Pressure\s*[:]\s*(\d+)\/(\d+)",
        "heart_rate": r"Heart\s*Rate\s*[:]\s*(\d+)\s*(?:bpm|beats)",
        "temperature": r"Temperature\s*[:]\s*(\d+\.?\d*)\s*(?:°C|C)",
        "weight": r"Weight\s*[:]\s*(\d+\.?\d*)\s*(?:kg|KG)",
        "height": r"Height\s*[:]\s*(\d+\.?\d*)\s*(?:cm|CM)",
        "bmi": r"BMI\s*[:]\s*(\d+\.?\d*)",
        "glucose": r"Glucose\s*[:]\s*(\d+\.?\d*)",
        "cholesterol": r"Cholesterol\s*[:]\s*(\d+\.?\d*)"
    }
    
    for param, pattern in param_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            parameters.append({
                "parameter": param.replace("_", " ").title(),
                "value": matches[0] if len(matches) == 1 else matches,
                "raw_text": text
            })
    
    return parameters

def generate_summary(text: str, parameters: List[Dict]) -> str:
    """
    Generate a summary of the report
    """
    try:
        # Get first 500 characters as summary
        summary = text[:500] + "..." if len(text) > 500 else text
        
        if parameters:
            summary += f"\n\nExtracted {len(parameters)} medical parameters."
        
        return summary
    except Exception as e:
        print(f"Summary Generation Error: {e}")
        return "Summary generation failed"