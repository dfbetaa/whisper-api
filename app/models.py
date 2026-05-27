from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    """Schema returned by the /transcribe endpoint."""
    text: str
    language: str
    duration_seconds: float
