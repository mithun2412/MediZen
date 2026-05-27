import os
import uuid

from reportlab.platypus import (

    SimpleDocTemplate,

    Paragraph,

    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.lib.pagesizes import letter


# ─────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────

def generate_pdf_report(

    report_text: str
):

    try:

        # CREATE REPORTS FOLDER
        os.makedirs(

            "reports",

            exist_ok=True
        )

        # UNIQUE FILENAME
        filename = (
            f"{uuid.uuid4()}.pdf"
        )

        file_path = os.path.join(

            "reports",

            filename
        )

        # PDF DOCUMENT
        doc = SimpleDocTemplate(

            file_path,

            pagesize=letter
        )

        styles = getSampleStyleSheet()

        elements = []

        # TITLE
        title = Paragraph(

            "<b>MediZen AI Healthcare Report</b>",

            styles["Title"]
        )

        elements.append(title)

        elements.append(
            Spacer(1, 20)
        )

        # REPORT CONTENT
        paragraphs = report_text.split("\n")

        for line in paragraphs:

            if line.strip():

                paragraph = Paragraph(

                    line,

                    styles["BodyText"]
                )

                elements.append(
                    paragraph
                )

                elements.append(
                    Spacer(1, 10)
                )

        # BUILD PDF
        doc.build(elements)

        return {

            "success": True,

            "filename": filename,

            "file_path": file_path
        }

    except Exception as e:

        print(
            "PDF Generation Error:",
            e
        )

        return {

            "success": False,

            "filename": None,

            "file_path": None
        }