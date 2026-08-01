# app/services/healthcare_validator.py

import re
from typing import Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class HealthcareValidator:
    """
    Validates if a document is healthcare/medical related
    """
    
    # Medical keywords for validation
    MEDICAL_KEYWORDS = [
        # Medical specialties
        'cardiology', 'dermatology', 'neurology', 'oncology', 
        'pediatrics', 'psychiatry', 'radiology', 'surgery',
        'orthopedics', 'ophthalmology', 'gynecology', 'urology',
        'endocrinology', 'gastroenterology', 'hematology',
        'nephrology', 'pulmonology', 'rheumatology',
        
        # Medical terms
        'diagnosis', 'treatment', 'prescription', 'medication',
        'patient', 'hospital', 'clinic', 'doctor', 'nurse',
        'symptom', 'disease', 'disorder', 'condition',
        'therapy', 'surgery', 'procedure', 'examination',
        'test result', 'lab report', 'pathology', 'radiology',
        'blood pressure', 'heart rate', 'temperature',
        'glucose', 'cholesterol', 'hemoglobin', 'blood sugar',
        'white blood cell', 'red blood cell', 'platelet',
        
        # Medical tests
        'mri', 'ct scan', 'x-ray', 'ultrasound', 'ecg', 'eeg',
        'blood test', 'urine test', 'biopsy', 'endoscopy',
        'colonoscopy', 'bronchoscopy', 'angiography', 'echocardiogram',
        
        # Diseases/Conditions
        'cancer', 'diabetes', 'hypertension', 'asthma',
        'arthritis', 'alzheimer', 'parkinson', 'epilepsy',
        'tuberculosis', 'pneumonia', 'hepatitis', 'hiv',
        'covid', 'influenza', 'infection', 'inflammation',
        'stroke', 'heart attack', 'myocardial infarction',
        
        # Healthcare documents
        'medical record', 'health record', 'clinical report',
        'discharge summary', 'admission note', 'consultation',
        'referral', 'insurance claim', 'medicare', 'medicaid',
        
        # Medications
        'aspirin', 'ibuprofen', 'paracetamol', 'amoxicillin',
        'metformin', 'atorvastatin', 'omeprazole', 'losartan',
        'albuterol', 'lisinopril', 'simvastatin', 'metoprolol',
        'warfarin', 'clopidogrel', 'furosemide'
    ]
    
    # Medical abbreviations
    MEDICAL_ABBREVIATIONS = [
        'bp', 'hr', 'rr', 'spo2', 'bmi', 'bun', 'cr', 'wbc',
        'rbc', 'hgb', 'hct', 'plt', 'pt', 'ptt', 'inr', 'esr',
        'crp', 'ldl', 'hdl', 'trig', 'hba1c', 'tsh', 't3', 't4',
        'psa', 'ca-125', 'cea', 'afp', 'hcg', 'ldh', 'ast', 'alt',
        'b12', 'folate', 'ferritin', 'iron', 'hgb', 'hct'
    ]
    
    @classmethod
    def validate_healthcare_document(cls, text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate if document is healthcare related
        
        Returns:
            (is_healthcare, message, details)
        """
        if not text or len(text.strip()) < 10:
            return False, "Document content is too short to validate", {}
        
        text_lower = text.lower()
        
        # Check for medical keywords
        found_keywords = []
        for keyword in cls.MEDICAL_KEYWORDS:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        # Check for medical abbreviations
        found_abbr = []
        for abbr in cls.MEDICAL_ABBREVIATIONS:
            # Check for abbreviation as whole word or with punctuation
            pattern = rf'\b{abbr}\b'
            if re.search(pattern, text_lower):
                found_abbr.append(abbr)
        
        # Check for medical patterns (blood pressure, glucose, etc.)
        medical_patterns = [
            (r'\b\d{2,3}\s*/\s*\d{2,3}\b', 'blood_pressure'),
            (r'\bglucose\s*\d{2,3}\b', 'glucose'),
            (r'\btemperature\s*\d{2,3}\.\d\b', 'temperature'),
            (r'\bheart rate\s*\d{2,3}\b', 'heart_rate'),
            (r'\bweight\s*\d{2,3}\s*(kg|lbs|lb)\b', 'weight'),
            (r'\bheight\s*\d{2,3}\s*(cm|in|ft)\b', 'height'),
            (r'\bcholesterol\s*\d{2,3}\b', 'cholesterol'),
        ]
        
        found_patterns = []
        for pattern, name in medical_patterns:
            if re.search(pattern, text_lower):
                found_patterns.append(name)
        
        # Calculate score
        total_score = len(found_keywords) + len(found_abbr) + len(found_patterns)
        
        # Decision with confidence
        details = {
            "keywords_found": found_keywords[:20],
            "abbreviations_found": found_abbr[:10],
            "patterns_found": found_patterns,
            "total_indicators": total_score,
            "keyword_count": len(found_keywords),
            "abbreviation_count": len(found_abbr),
            "pattern_count": len(found_patterns)
        }
        
        if total_score >= 5:
            return True, f"Healthcare document confirmed with {total_score} medical indicators", details
        elif total_score >= 2 and len(text) > 200:
            return True, f"Likely healthcare document with {total_score} medical indicators", details
        elif total_score >= 1 and len(text) > 500:
            return True, f"Possible healthcare document with {total_score} medical indicators", details
        else:
            return False, "This does not appear to be a healthcare/medical document. MediZen AI is designed for healthcare-related content only.", details
    
    @classmethod
    def get_healthcare_indicators(cls, text: str) -> Dict[str, Any]:
        """Get detailed healthcare indicators without validation"""
        text_lower = text.lower()
        
        found_keywords = [kw for kw in cls.MEDICAL_KEYWORDS if kw.lower() in text_lower]
        found_abbr = [abbr for abbr in cls.MEDICAL_ABBREVIATIONS 
                     if re.search(rf'\b{abbr}\b', text_lower)]
        
        return {
            "keywords_found": found_keywords[:10],
            "abbreviations_found": found_abbr[:10],
            "total_indicators": len(found_keywords) + len(found_abbr),
            "is_healthcare": len(found_keywords) + len(found_abbr) >= 2
        }