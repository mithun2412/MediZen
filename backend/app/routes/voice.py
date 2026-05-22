import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from groq import Groq
import io

router = APIRouter(prefix="/voice", tags=["voice"])
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Convert user's voice recording → text using Groq Whisper."""
    try:
        audio_bytes = await file.read()

        transcription = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=(file.filename or "audio.webm", audio_bytes),
            response_format="text",
            language="en",
        )

        return {"transcript": transcription}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")