import os
import shutil

from fastapi import (

    APIRouter,

    UploadFile,

    File,

    HTTPException,

    Form
)

from app.services.image_ai_service import (
    analyze_medical_image
)

from app.services.medical_ocr_service import (
    analyze_medical_report_image
)

from app.services.pdf_service import (
    generate_pdf_report
)

from app.services.pdf_rag_service import (

    build_vector_store,

    ask_pdf_question
)

router = APIRouter()

# ─────────────────────────────────────────────
# CREATE UPLOAD FOLDER
# ─────────────────────────────────────────────

os.makedirs(

    "uploads",

    exist_ok=True
)

# ─────────────────────────────────────────────
# IMAGE UPLOAD + OCR + AI
# ─────────────────────────────────────────────

@router.post("/image")
async def upload_medical_image(

    file: UploadFile = File(...)
):

    try:

        # VALIDATE IMAGE
        if not file.content_type.startswith(

            "image/"
        ):

            raise HTTPException(

                status_code=400,

                detail=
                    "Only image uploads allowed."
            )

        # SAVE FILE
        file_path = os.path.join(

            "uploads",

            file.filename
        )

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(

                file.file,

                buffer
            )

        # ─────────────────────────
        # OCR ANALYSIS
        # ─────────────────────────

        ocr_result = (

            analyze_medical_report_image(
                file_path
            )
        )

        # IF OCR DETECTS REPORT
        if ocr_result["success"]:

            report_text = f"""

MediZen AI Medical Report Analysis

OCR Extracted Text:

{ocr_result['extracted_text']}

────────────────────────────

AI Medical Explanation:

{ocr_result['analysis']}

"""

            pdf_result = (

                generate_pdf_report(
                    report_text
                )
            )

            pdf_url = None

            if pdf_result["success"]:

                pdf_url = (

                    f"/reports/"
                    f"{pdf_result['filename']}"
                )

            return {

                "success": True,

                "type":
                    "medical_report",

                "image_url":

                    f"/uploads/{file.filename}",

                "analysis":

                    ocr_result[
                        "analysis"
                    ],

                "extracted_text":

                    ocr_result[
                        "extracted_text"
                    ],

                "pdf_url":
                    pdf_url
            }

        # ─────────────────────────
        # NORMAL IMAGE AI
        # ─────────────────────────

        image_result = (

            analyze_medical_image(
                file_path
            )
        )

        report_text = f"""

MediZen AI Image Analysis Report

Prediction:
{image_result['prediction']}

Confidence:
{image_result['confidence']}%

Severity:
{image_result['severity']}

────────────────────────────

AI Analysis:

{image_result['analysis']}

"""

        pdf_result = (

            generate_pdf_report(
                report_text
            )
        )

        pdf_url = None

        if pdf_result["success"]:

            pdf_url = (

                f"/reports/"
                f"{pdf_result['filename']}"
            )

        return {

            "success": True,

            "type":
                "medical_image",

            "image_url":

                f"/uploads/{file.filename}",

            "prediction":

                image_result[
                    "prediction"
                ],

            "confidence":

                image_result[
                    "confidence"
                ],

            "severity":

                image_result[
                    "severity"
                ],

            "analysis":

                image_result[
                    "analysis"
                ],

            "pdf_url":
                pdf_url
        }

    except Exception as e:

        print(
            "Image Upload Error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ─────────────────────────────────────────────
# PDF UPLOAD + VECTOR STORE
# ─────────────────────────────────────────────

@router.post("/pdf")
async def upload_pdf(

    file: UploadFile = File(...)
):

    try:

        # VALIDATE PDF
        if file.content_type != (

            "application/pdf"
        ):

            raise HTTPException(

                status_code=400,

                detail=
                    "Only PDF uploads allowed."
            )

        # SAVE FILE
        file_path = os.path.join(

            "uploads",

            file.filename
        )

        with open(file_path, "wb") as buffer:

            shutil.copyfileobj(

                file.file,

                buffer
            )

        # ─────────────────────────
        # BUILD VECTOR STORE
        # ─────────────────────────

        rag_result = (

            build_vector_store(
                file_path
            )
        )

        return {

            "success": True,

            "message":

                "PDF uploaded and "
                "processed successfully.",

            "pdf_file":

                f"/uploads/{file.filename}",

            "chunks_indexed":

                rag_result["chunks"]
        }

    except Exception as e:

        print(
            "PDF Upload Error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )


# ─────────────────────────────────────────────
# ASK QUESTIONS FROM PDF
# ─────────────────────────────────────────────

@router.post("/pdf/chat")
async def chat_with_pdf(

    question: str = Form(...)
):

    try:

        response = ask_pdf_question(
            question
        )

        return response

    except Exception as e:

        print(
            "PDF Chat Error:",
            e
        )

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )