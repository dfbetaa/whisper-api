import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from app.models import TranscriptionResponse
from app.transcriber import transcribe_audio

# Create the FastAPI application.
# title and description show up in the auto-generated docs.
app = FastAPI(
    title="Whisper Transcription API",
    description="A REST API for transcribing audio to text using OpenAI Whisper.",
    version="1.0.0"
)

# Audio formats we accept.
# If someone sends a .pdf or an image, we reject it before trying to
# transcribe something that makes no sense.
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4"}

@app.get("/")
def root():
    """
    Root endpoint — used to verify the server is alive.
    This pattern is known as a 'health check'.
    """
    return {"status": "ok", "message": "Whisper API is running"}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)):
    """
    Main endpoint — receives an audio file and returns its transcription.
    """

    # Make sure the upload has a filename (that is where we read the extension from).
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Extract the file extension to validate it.
    # For example, from "audio.mp3" we extract ".mp3".
    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        # HTTPException stops execution and returns an HTTP error.
        # 400 means "Bad Request" — the client sent something invalid.
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format: {extension}. Allowed formats: {allowed}"
        )

    # Read the file contents as bytes.
    # await is needed because reading a file can take time; async/await lets
    # the server handle other requests while it waits.
    audio_bytes = await file.read()

    # Reject empty files.
    if len(audio_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    # Call our transcription function.
    # Wrapped in try/except to return a controlled HTTP error instead of
    # leaking a raw stack trace if Whisper fails.
    try:
        result = transcribe_audio(audio_bytes)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {exc}"
        )

    # Convert the dict into the Pydantic model.
    # Pydantic validates that every field is present and correctly typed.
    return TranscriptionResponse(**result)
