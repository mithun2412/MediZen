# app/services/pdf_service.py

import os
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

def generate_pdf_report(report_text, filename=None):
    """
    Generate a PDF report from text content
    For now, we'll save as a text file with .txt extension
    Since ReportLab might not be installed, we'll keep it simple
    """
    try:
        # Create reports directory if it doesn't exist
        os.makedirs("reports", exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.txt"
        
        # Ensure filename ends with .txt (since we're not using PDF for now)
        if not filename.endswith('.txt'):
            filename = filename.replace('.pdf', '.txt')
        
        filepath = os.path.join("reports", filename)
        
        # Write the report as a text file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("HEALTH ASSESSMENT REPORT\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 80 + "\n\n")
            
            # Write the report content
            if isinstance(report_text, str):
                f.write(report_text)
            elif isinstance(report_text, dict):
                # Format dictionary content
                for key, value in report_text.items():
                    f.write(f"\n{key.upper()}:\n")
                    f.write("-" * 40 + "\n")
                    if isinstance(value, list):
                        for item in value:
                            f.write(f"  • {item}\n")
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            f.write(f"  {sub_key}: {sub_value}\n")
                    else:
                        f.write(f"  {value}\n")
            else:
                f.write(str(report_text))
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("End of Report\n")
        
        return {
            "success": True,
            "filename": filename,
            "filepath": filepath
        }
        
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def generate_health_report(data, user_name="Patient", output_path=None):
    """
    Generate a health report from conversation data
    """
    content = {
        'Patient': user_name,
        'Date': datetime.now().strftime('%Y-%m-%d'),
    }
    
    # Extract relevant information
    if 'diagnosis' in data:
        content['Diagnosis'] = data['diagnosis']
    if 'symptoms' in data:
        content['Symptoms'] = data['symptoms']
    if 'severity' in data:
        content['Severity'] = data['severity']
    if 'recommendations' in data:
        content['Recommendations'] = data['recommendations']
    if 'medications' in data:
        content['Medications'] = data['medications']
    if 'follow_up' in data:
        content['Follow-up'] = data['follow_up']
    if 'summary' in data:
        content['Summary'] = data['summary']
    
    return generate_pdf_report(content, output_path)