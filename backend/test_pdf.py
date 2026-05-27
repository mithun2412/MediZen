from app.services.pdf_service import (
    generate_pdf_report
)

report = """

MediZen AI Healthcare Report

Symptoms:
Fever and weakness

Severity:
Moderate

Clinical Observation:
Possible viral infection.

Home Care:
- Drink water
- Rest properly

"""

result = generate_pdf_report(
    report
)

print(result)