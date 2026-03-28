from fastapi import FastAPI, UploadFile, File, HTTPException
from app.models import TranscriptionResponse
from app.transcriber import transcribe_audio

# Creamos la aplicación FastAPI.
# title y description aparecen en la documentación automática.
app = FastAPI(
    title="Whisper Transcription API",
    description="API para transcribir audio a texto usando OpenAI Whisper",
    version="1.0.0"
)

# Los formatos de audio que aceptamos.
# Si alguien manda un .pdf o una imagen, lo rechazamos antes de intentar transcribir algo que no tiene sentido.
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac", ".mp4"}

@app.get("/")
def root():
    """
    Endpoint raíz — sirve para verificar que el servidor está vivo.
    Este patrón se llama 'health check'.
    """
    return {"status": "ok", "message": "Whisper API corriendo"}

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)):
    """
    Endpoint principal — recibe un archivo de audio
    y devuelve la transcripción.
    """
    
    # Extraemos la extensión del archivo para validarla.
    # Por ejemplo, de "audio.mp3" extraemos ".mp3"
    import os
    extension = os.path.splitext(file.filename)[1].lower()
    
    if extension not in ALLOWED_EXTENSIONS:
        # HTTPException detiene la ejecución y devuelve un error HTTP.
        # 400 significa "Bad Request" — el cliente mandó algo incorrecto.
        raise HTTPException(
            status_code=400,
            detail=f"Formato no soportado: {extension}. Usa: {ALLOWED_EXTENSIONS}"
        )
    
    # Leemos el contenido del archivo como bytes.
    # await es necesario porque leer un archivo es una operación que puede tardar
    # async/await permite que el servidor atienda otros requests mientras espera.
    audio_bytes = await file.read()
    
    # Validamos que el archivo no esté vacío
    if len(audio_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail="El archivo está vacío"
        )
    
    # Llamamos a nuestra función de transcripción.
    # Si algo falla aquí, FastAPI automáticamente devuelve un error 500.
    result = transcribe_audio(audio_bytes)
    
    # Convertimos el diccionario al modelo Pydantic.
    # Pydantic valida que todos los campos estén presentes y sean del tipo correcto.
    return TranscriptionResponse(**result)