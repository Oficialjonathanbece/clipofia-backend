import os
import logging
from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

class SubtitleService:
    """
    Servicio local para transcripción de audio y generación de subtítulos 
    en formato .srt utilizando faster-whisper.
    """
    
    def __init__(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        """
        Inicializa el modelo de faster-whisper.
        Por defecto usa 'cpu' e 'int8' para que funcione en cualquier ordenador sin requerir tarjeta gráfica dedicada.
        """
        logger.info(f"Cargando modelo faster-whisper '{model_size}' en dispositivo '{device}'...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def _format_time(self, seconds: float) -> str:
        """
        Convierte segundos en formato de tiempo estándar para subtítulos SRT (HH:MM:SS,mmm).
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    def generate_srt(self, video_path: str, output_srt_path: str) -> str:
        """
        Toma un archivo de vídeo, extrae su audio internamente, lo transcribe 
        y genera el archivo .srt listo para ser quemado por FFmpeg.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"El archivo de vídeo no existe en la ruta: {video_path}")

        logger.info(f"Iniciando transcripción con Whisper para: {video_path}")
        
        # Ejecutamos la transcripción (beam_size=5 mejora la precisión del texto)
        segments, info = self.model.transcribe(video_path, beam_size=5)
        
        srt_lines = []
        for index, segment in enumerate(segments, start=1):
            start_time_str = self._format_time(segment.start)
            end_time_str = self._format_time(segment.end)
            text = segment.text.strip()
            
            # Construimos el bloque del formato SRT oficial
            srt_lines.append(f"{index}\n{start_time_str} --> {end_time_str}\n{text}\n")

        # Guardamos el archivo físico .srt resultante
        with open(output_srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(srt_lines))

        logger.info(f"Archivo de subtítulos .srt generado exitosamente en: {output_srt_path}")
        return output_srt_path