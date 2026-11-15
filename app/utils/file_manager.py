import os
import shutil
import tempfile
import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

class FileManager:
    """
    Utilidad centralizada para el manejo seguro de archivos temporales, 
    validación de formatos y limpieza de disco en el backend.
    """

    # Extensiones de vídeo permitidas para Clipofia
    ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

    @classmethod
    def validate_video_extension(cls, filename: str) -> bool:
        """
        Verifica que la extensión del archivo subido esté dentro de las permitidas.
        """
        if not filename:
            return False
        ext = os.path.splitext(filename)[1].lower()
        return ext in cls.ALLOWED_EXTENSIONS

    @classmethod
    def save_upload_to_temp(cls, upload_file: UploadFile) -> str:
        """
        Guarda un UploadFile de FastAPI en un directorio temporal del sistema operativo
        de forma segura y retorna su ruta absoluta.
        """
        if not upload_file.filename or not cls.validate_video_extension(upload_file.filename):
            raise HTTPException(
                status_code=400, 
                detail="Formato de archivo no soportado. Por favor, sube un vídeo válido (.mp4, .mov, .mkv, etc.)."
            )
        
        suffix = os.path.splitext(upload_file.filename)[1].lower()
        
        try:
            # Creamos un archivo temporal que persiste en disco hasta que lo eliminemos manualmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                shutil.copyfileobj(upload_file.file, temp_file)
                temp_path = temp_file.name
                
            logger.info(f"Archivo subido guardado temporalmente en: {temp_path}")
            return temp_path
            
        except Exception as e:
            logger.error(f"Error al almacenar el archivo temporalmente: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail="Error interno al procesar y almacenar el archivo en el servidor."
            )

    @staticmethod
    def safe_delete(file_path: str) -> None:
        """
        Elimina un archivo de forma segura si existe en el disco, 
        capturando cualquier excepción para evitar romper el flujo principal.
        """
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
                logger.info(f"Archivo temporal eliminado correctamente: {file_path}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar el archivo {file_path}: {str(e)}")