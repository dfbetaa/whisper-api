import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from app.models import TranscriptionResponse
from app.transcriber import transcribe_audio

app = FastAPI(
    title="Whisper Transcription API",
    description="A REST API for transcribing audio to text using OpenAI Whisper.",
    version="1.0.0"
)

ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4"}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25 MB


@app.get("/")
def root():
    return {"status": "ok", "message": "Whisper API is running"}


@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {extension}. Allowed: {allowed}",
        )

    audio_bytes = await file.read()

    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(audio_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum allowed size is {MAX_FILE_SIZE // (1024 * 1024)} MB",
        )

    try:
        result = transcribe_audio(audio_bytes, extension)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {exc}")

    return TranscriptionResponse(**result)
