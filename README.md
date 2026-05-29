# Whisper Transcription API

A production-ready REST API that transcribes audio to text using [OpenAI Whisper](https://github.com/openai/whisper), built with FastAPI and fully containerised with Docker. Whisper runs entirely on-device, so audio never leaves the server, which makes it suitable for privacy-sensitive use cases such as healthcare and conversational systems.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Speech-to-text** for `.wav`, `.mp3`, `.m4a`, `.ogg`, `.flac`, and `.mp4`
- **Automatic language detection** returned with every transcription
- **Local inference** — no third-party API calls, no audio leaves the machine
- **Input validation** — rejects unsupported formats, empty files, and files over 25 MB
- **Auto-generated OpenAPI docs** at `/docs`
- **Single-command Docker deployment**

## Tech stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Web framework | FastAPI + Uvicorn (ASGI) |
| ML model | OpenAI Whisper (`base`, runs locally) |
| Containerisation | Docker + Docker Compose |

## Quick start (Docker)

The fastest way to run the API. Requires only Docker installed.

```bash
git clone https://github.com/dfbetaa/whisper-api.git
cd whisper-api
docker compose up --build
```

The API is then available at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.

## Local setup (without Docker)

Requires Python 3.8+ and [ffmpeg](https://ffmpeg.org/) installed on your system.

```bash
git clone https://github.com/dfbetaa/whisper-api.git
cd whisper-api

# create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# install dependencies and run
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API reference

### `GET /`
Health check. Confirms the server is running.

```json
{ "status": "ok", "message": "Whisper API is running" }
```

### `POST /transcribe`
Transcribes an uploaded audio file.

**Request:** `multipart/form-data` with a single `file` field. Maximum file size: **25 MB**.

```bash
curl -X POST "http://localhost:8000/transcribe" -F "file=@audio.mp3"
```

**Response `200 OK`:**

```json
{
  "text": "Hello, this is a transcription test",
  "language": "en",
  "duration_seconds": 3.45
}
```

`duration_seconds` reflects the duration of the audio clip as detected by Whisper.

**Error responses:**

| Status | Cause |
|--------|-------|
| `400` | Unsupported file format, missing filename, or empty file |
| `413` | File exceeds the 25 MB limit |
| `500` | Transcription failure |

## Project structure

```
whisper-api/
├── app/
│   ├── __init__.py
│   ├── models.py          # Pydantic response schema
│   ├── transcriber.py     # Whisper inference logic
│   └── main.py            # FastAPI endpoints and request validation
├── tests/
│   └── test_api.py        # pytest test suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt       # pinned runtime dependencies
├── requirements-dev.txt   # test dependencies
└── README.md
```

## Running tests

```bash
pip install -r requirements-dev.txt
pytest tests/
```

Tests cover the health check, input validation (format, empty file, size limit), the success path, and error handling — without requiring the Whisper model to be loaded.

## Choosing a Whisper model

The API loads the `base` model (~145 MB) by default, a good balance of speed and accuracy. To use a different size, edit the model name in `app/transcriber.py`:

```python
model = whisper.load_model("base")  # options: tiny, base, small, medium, large
```

Larger models are more accurate but slower and need more memory.

## Notes

The Whisper model is loaded once at startup rather than per request, so the first launch downloads the model weights and subsequent requests are fast. Uploaded audio is written to a temporary file that is always cleaned up, even if transcription fails.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
