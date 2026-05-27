import whisper
import tempfile
import time
import os

# Load the model ONCE at server startup.
# This matters — loading the model takes several seconds.
# If we loaded it inside the function, every request would be slow.
model = whisper.load_model("base")

def transcribe_audio(audio_bytes: bytes) -> dict:
    """
    Takes audio as bytes, transcribes it with Whisper,
    and returns the text, detected language, and duration.
    """

    # Write the audio to a temporary file on disk.
    # delete=False means it is not removed automatically when closed;
    # we remove it manually at the end.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)       # write the bytes to the file
        tmp_path = tmp.name          # keep the path, e.g. /tmp/tmpXYZ.wav

    try:
        # Start the timer.
        start_time = time.time()

        # Ask Whisper to transcribe the file.
        # result is a dict with a lot of information —
        # we only need the text and the detected language.
        result = model.transcribe(tmp_path)

        # Measure how long it took.
        duration = round(time.time() - start_time, 2)

        # Return only what we care about.
        return {
            "text": result["text"].strip(),
            "language": result["language"],
            "duration_seconds": duration
        }

    finally:
        # The finally block always runs, error or not.
        # This guarantees the temporary file is always removed,
        # even if Whisper raises an exception.
        os.remove(tmp_path)
