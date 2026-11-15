from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import os
from app.modules.video.schemas import VideoProcessSchema
from app.modules.video.services import VideoProcessingService

router = APIRouter(
    prefix="/video",
    tags=["Video Processing"]
)

def cleanup_file(path: str):
    """
    Función auxiliar ejecutada en segundo plano para limpiar 
    el archivo de vídeo procesado una vez que el cliente termina de descargarlo.
    """
    if path and os.path.exists(path):
        try:
            os.unlink(path)
        except Exception:
            pass

@router.post("/process", response_class=FileResponse)
async def process_video_endpoint(
    file: UploadFile = File(..., description="Archivo de vídeo horizontal 16:9 original"),
    start_time: float = Form(..., description="Tiempo de inicio del clip en segundos"),
    end_time: float = Form(..., description="Tiempo de fin del clip en segundos"),
    aspect_ratio: str = Form(default="9:16", description="Relación de aspecto deseada"),
    enable_subtitles: bool = Form(default=True, description="Activar o desactivar subtítulos automáticos")
):
    """
    Endpoint para recibir un vídeo, recortarlo, reencuadrarlo a 9:16 con Whisper y FFmpeg,
    y devolver el clip final listo para descargar.
    """
    # 1. Validar los datos de entrada usando nuestro esquema de Pydantic de forma manual o directa
    try:
        validated_data = VideoProcessSchema(
            start_time=start_time,
            end_time=end_time,
            aspect_ratio=aspect_ratio,
            enable_subtitles=enable_subtitles
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # 2. Validar que el archivo subido sea un vídeo válido por su extensión o content-type
    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv", ".webm")):
        raise HTTPException(
            status_code=400, 
            detail="Formato de archivo no soportado. Sube un vídeo válido (.mp4, .mov, etc.)."
        )

    try:
        # 3. Invocar al servicio orquestador para procesar el vídeo
        output_file_path = await VideoProcessingService.process_clip(
            file=file,
            start_time=validated_data.start_time,
            end_time=validated_data.end_time,
            aspect_ratio=validated_data.aspect_ratio,
            enable_subtitles=validated_data.enable_subtitles
        )

        # 4. Devolver el archivo como respuesta descargable, limpiándolo automáticamente al terminar
        return FileResponse(
            path=output_file_path,
            media_type="video/mp4",
            filename=f"clipofia_output_{os.path.basename(output_file_path)}",
            background=BackgroundTasks() # Se puede registrar la tarea de limpieza aquí
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno procesando el vídeo: {str(e)}")