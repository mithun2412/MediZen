import os
import uuid

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

from app.vision.image_predictor import (
    predict_skin_image
)

router = APIRouter(

    prefix="/analyze-image",

    tags=["Medical Vision AI"]
)


# ─────────────────────────────────────────────
# IMAGE ANALYSIS ROUTE
# ─────────────────────────────────────────────

@router.post("/")
async def analyze_image(

    file: UploadFile = File(...)
):

    # validate image type

    if not file.content_type.startswith(
        "image/"
    ):

        raise HTTPException(

            status_code=400,

            detail="Only image files allowed"
        )

    # create uploads folder

    os.makedirs(
        "uploads",
        exist_ok=True
    )

    # generate unique filename

    filename = f"{uuid.uuid4()}_{file.filename}"

    file_path = os.path.join(
        "uploads",
        filename
    )

    # save uploaded image

    with open(file_path, "wb") as f:

        content = await file.read()

        f.write(content)

    # AI prediction

    result = predict_skin_image(
        file_path
    )

    return {

        "success": True,

        "filename": filename,

        "analysis": result
    }