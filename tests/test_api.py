import io
import struct
import wave
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import MAX_FILE_SIZE, app

client = TestClient(app)


def make_wav(duration_sec: int = 1, sample_rate: int = 16000) -> bytes:
    """Build a minimal silent WAV in memory."""
    buf = io.BytesIO()
    n_frames = sample_rate * duration_sec
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack("<" + "h" * n_frames, *([0] * n_frames)))
    return buf.getvalue()


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Whisper API is running"}


def test_rejects_unsupported_format():
    response = client.post(
        "/transcribe",
        files={"file": ("document.pdf", b"fake content", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Unsupported format" in response.json()["detail"]


def test_rejects_empty_file():
    response = client.post(
        "/transcribe",
        files={"file": ("audio.wav", b"", "audio/wav")},
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]


def test_rejects_oversized_file():
    oversized = b"0" * (MAX_FILE_SIZE + 1)
    response = client.post(
        "/transcribe",
        files={"file": ("audio.wav", oversized, "audio/wav")},
    )
    assert response.status_code == 413
    assert "25 MB" in response.json()["detail"]


def test_transcription_success():
    audio = make_wav()
    mock_result = {
        "text": "hello world",
        "language": "en",
        "duration_seconds": 1.0,
    }
    with patch("app.main.transcribe_audio", return_value=mock_result):
        response = client.post(
            "/transcribe",
            files={"file": ("audio.wav", audio, "audio/wav")},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "hello world"
    assert body["language"] == "en"
    assert "duration_seconds" in body


def test_transcription_error_returns_500():
    audio = make_wav()
    with patch("app.main.transcribe_audio", side_effect=RuntimeError("model crash")):
        response = client.post(
            "/transcribe",
            files={"file": ("audio.wav", audio, "audio/wav")},
        )
    assert response.status_code == 500
    assert "Transcription failed" in response.json()["detail"]
