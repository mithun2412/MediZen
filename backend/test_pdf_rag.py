from app.services.pdf_rag_service import (

    build_vector_store,

    ask_pdf_question
)

# LOAD PDF
build_vector_store(
    "sample_report.pdf"
)

# ASK QUESTION
response = ask_pdf_question(

    "What is the hemoglobin level?"
)

print(response)