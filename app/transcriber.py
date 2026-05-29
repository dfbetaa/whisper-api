import os
import tempfile

import whisper

model = whisper.load_model("base")


def transcribe_audio(audio_bytes: bytes, suffix: str = ".wav") -> dict:
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path)
        segments = result.get("segments", [])
        duration = round(segments[-1]["end"], 2) if segments else 0.0
        return {
            "text": result["text"].strip(),
            "language": result["language"],
            "duration_seconds": duration,
        }
    finally:
        os.remove(tmp_path)
