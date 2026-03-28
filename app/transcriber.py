import whisper
import tempfile
import time
import os

# Cargamos el modelo UNA sola vez cuando arranca el servidor.
# Esto es importante — cargar el modelo tarda varios segundos.
# Si lo cargáramos dentro de la función, cada request tardaría mucho.
model = whisper.load_model("base")

def transcribe_audio(audio_bytes: bytes) -> dict:
    """
    Recibe el audio como bytes, lo transcribe con Whisper,
    y devuelve texto, idioma detectado, y duración.
    """
    
    # Creamos un archivo temporal en disco para guardar el audio.
    # delete=False significa que no se borra automáticamente al cerrarlo
    # lo borraremos nosotros manualmente al final.
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(audio_bytes)       # escribimos los bytes al archivo
        tmp_path = tmp.name          # guardamos la ruta, ej: C:\Temp\tmpXYZ.wav

    try:
        # Empezamos a medir el tiempo
        start_time = time.time()

        # Le decimos a Whisper que transcriba el archivo.
        # result es un diccionario con muchísima información —
        # nosotros solo necesitamos el texto y el idioma detectado.
        result = model.transcribe(tmp_path)

        # Calculamos cuántos segundos tardó
        duration = round(time.time() - start_time, 2)

        # Devolvemos solo lo que nos interesa
        return {
            "text": result["text"].strip(),
            "language": result["language"],
            "duration_seconds": duration
        }

    finally:
        # El bloque finally se ejecuta SIEMPRE, haya error o no.
        # Esto garantiza que el archivo temporal siempre se borre,
        # incluso si Whisper lanza una excepción.
        os.remove(tmp_path)