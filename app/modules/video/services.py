import os
import shutil
import tempfile
import logging
from fastapi import UploadFile
from app.modules.video.ffmpeg import FFmpegService
from app.modules.video.subtitles import SubtitleService
from app.utils.file_manager import FileManager

logger = logging.getLogger(__name__)

# Instanciamos el servicio de Whisper una sola vez para mantener el modelo cargado en memoria RAM
# (puedes cambiar a "tiny" o "small" según la velocidad y recursos de tu ordenador)
subtitle_service = SubtitleService(model_size="base", device="cpu", compute_type="int8")

class VideoProcessingService:
    """
    Orquestador principal del pipeline de Clipofia:
    Gestiona archivos temporales, transcripción con Whisper y renderizado con FFmpeg.
    """

    @staticmethod
    async def process_clip(
        file: UploadFile,
        start_time: float,
        end_time: float,
        aspect_ratio: str,
        enable_subtitles: bool
    ) -> str:
        """
        Orquesta todo el flujo de procesamiento y devuelve la ruta del archivo final listo para descarga.
        """
        temp_input_path = None
        temp_output_path = None
        temp_srt_path = None

        try:
            # 1. Guardar el archivo subido usando el FileManager centralizado
            temp_input_path = FileManager.save_upload_to_temp(file)

            # 2. Definir la ruta temporal para el vídeo final procesado
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_output:
                temp_output_path = temp_output.name

            # 3. Generar subtítulos automáticos con faster-whisper si el usuario los activó
            srt_path_to_use = None
            if enable_subtitles:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as temp_srt:
                    temp_srt_path = temp_srt.name
                
                logger.info("Paso 1/2: Generando subtítulos automáticos con faster-whisper...")
                subtitle_service.generate_srt(temp_input_path, temp_srt_path)
                srt_path_to_use = temp_srt_path

            # 4. Procesar el vídeo con FFmpeg (corte, recorte 9:16 y quemado de subtítulos)
            logger.info("Paso 2/2: Ejecutando reencuadre inteligente y FFmpeg...")
            FFmpegService.process_video_clip(
                input_path=temp_input_path,
                output_path=temp_output_path,
                start_time=start_time,
                end_time=end_time,
                aspect_ratio=aspect_ratio,
                subtitle_path=srt_path_to_use
            )

            return temp_output_path
    
        except Exception as e:
            logger.exception(f"Error crítico en el servicio de vídeo:")
            if temp_output_path:
                FileManager.safe_delete(temp_output_path)
            raise e

        finally:
            # Limpiar archivos temporales de entrada y subtítulos de manera segura
            FileManager.safe_delete(temp_input_path)
            FileManager.safe_delete(temp_srt_path)