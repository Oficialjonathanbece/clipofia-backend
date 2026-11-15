import subprocess
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class FFmpegService:
    """
    Adaptador para ejecutar comandos de FFmpeg orientados al recorte, 
    reencuadre inteligente 9:16 y quemado de subtítulos.
    """

    @staticmethod
    def process_video_clip(
        input_path: str, 
        output_path: str, 
        start_time: float, 
        end_time: float, 
        aspect_ratio: str = "9:16",
        subtitle_path: Optional[str] = None
    ) -> None:
        """
        Recorta un segmento por tiempo, reencuadra a 9:16 y quema los subtítulos si se proporcionan.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"El archivo de entrada no existe en la ruta: {input_path}")

        # 1. Definir el filtro de recorte (Crop) para 9:16 centrado
        if aspect_ratio == "9:16":
            video_filter = "crop=ih*(9/16):ih:(iw-ih*(9/16))/2:0"
        else:
            video_filter = "scale=1080:1920"

        # 2. Agregar subtítulos si el archivo .srt existe y es válido
        if subtitle_path and os.path.exists(subtitle_path):
            # Normalizamos la ruta absoluta para evitar conflictos con barras invertidas en Windows
            safe_sub_path = os.path.abspath(subtitle_path).replace("\\", "/")
            
            # En Windows, FFmpeg requiere escapar los dos puntos de la letra de la unidad (ej. C\:/ruta/archivo.srt)
            if ":" in safe_sub_path:
                drive, path_part = safe_sub_path.split(":", 1)
                safe_sub_path = f"{drive}\\:{path_part}"
            
            # Encadenamos el filtro de subtítulos al filtro de vídeo existente
            video_filter = f"{video_filter},subtitles='{safe_sub_path}'"

        # 3. Construcción del comando de FFmpeg
        command = [
            "ffmpeg",
            "-y",
            "-ss", str(start_time),
            "-to", str(end_time),
            "-i", input_path,
            "-vf", video_filter,
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            output_path
        ]

        logger.info(f"Ejecutando comando FFmpeg con filtros: {video_filter}")

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            logger.info("Proceso de FFmpeg y subtitulado completado con éxito.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error en FFmpeg: {e.stderr}")
            raise RuntimeError(f"Fallo al procesar el vídeo y subtítulos con FFmpeg: {e.stderr}")