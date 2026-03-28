# Whisper Transcription API

API REST para transcribir audio a texto usando OpenAI Whisper.
Desarrollada con FastAPI y pensada para integrarse en sistemas conversacionales
y aplicaciones de salud que requieren procesamiento de voz en tiempo real.

## Tecnologías

- **Python 3.11**
- **FastAPI** — framework web moderno con validación automática de datos
- **OpenAI Whisper** — modelo de Speech-to-Text que corre completamente local
- **Uvicorn** — servidor ASGI de alto rendimiento
- **Docker** — containerización para despliegue reproducible

## Requisitos previos

- Python 3.8 o superior
- ffmpeg instalado en el sistema
- Docker (opcional, para correr en contenedor)

## Instalación local

1. Clona el repositorio
```
git clone https://github.com/TU_USUARIO/whisper-api.git
cd whisper-api
```

2. Crea y activa un entorno virtual
```
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

3. Instala las dependencias
```
pip install -r requirements.txt
```

4. Arranca el servidor
```
uvicorn app.main:app --reload
```

El servidor estará corriendo en `http://127.0.0.1:8000`

## Uso

### Documentación interactiva
Visita `http://127.0.0.1:8000/docs` para explorar y probar la API
desde una interfaz visual generada automáticamente por FastAPI.

### Health check
```
GET /
```
Respuesta:
```json
{"status": "ok", "message": "Whisper API corriendo"}
```

### Transcribir audio
```
POST /transcribe
```
Parámetros:
- `file` — archivo de audio (formatos soportados: .wav, .mp3, .m4a, .ogg, .flac, .mp4)

Ejemplo con curl:
```
curl.exe -X POST "http://127.0.0.1:8000/transcribe" -F "file=@audio.mp3"
```

Respuesta:
```json
{
  "text": "Hola, esto es una prueba de transcripción",
  "language": "es",
  "duration_seconds": 3.45
}
```

## Estructura del proyecto
```
whisper-api/
├── app/
│   ├── __init__.py       # marca la carpeta como módulo Python
│   ├── models.py         # schemas de datos con Pydantic
│   ├── transcriber.py    # lógica de transcripción con Whisper
│   └── main.py           # endpoints de FastAPI
├── requirements.txt      # dependencias del proyecto
├── Dockerfile            # instrucciones para construir el contenedor
└── README.md             # este archivo
```

## Modelo de Whisper

Por defecto se usa el modelo `base` (145 MB), que ofrece un buen balance
entre velocidad y precisión. Para cambiar el modelo, edita esta línea
en `transcriber.py`:
```python
model = whisper.load_model("base")  # opciones: tiny, base, small, medium
```