from pydantic import BaseModel, Field, model_validator
from typing import Optional

class VideoProcessSchema(BaseModel):
    """
    Esquema de validación para los parámetros de recorte, reencuadre 
    y generación de subtítulos automáticos.
    """
    start_time: float = Field(
        ..., 
        ge=0.0, 
        description="Tiempo de inicio del corte en segundos (debe ser mayor o igual a 0)"
    )
    end_time: float = Field(
        ..., 
        gt=0.0, 
        description="Tiempo de fin del corte en segundos"
    )
    aspect_ratio: str = Field(
        default="9:16", 
        description="Relación de aspecto deseada para el reencuadre inteligente"
    )
    
    # Nuevos campos para configurar los subtítulos
    enable_subtitles: bool = Field(
        default=True,
        description="Activa o desactiva la generación y quemado de subtítulos automáticos"
    )
    subtitle_font_size: int = Field(
        default=24,
        ge=12,
        le=72,
        description="Tamaño de la fuente para los subtítulos quemados en el vídeo"
    )
    subtitle_font_color: str = Field(
        default="white",
        description="Color de la fuente de los subtítulos (ej. white, yellow, cyan)"
    )

    @model_validator(mode='after')
    def validate_time_range(self) -> 'VideoProcessSchema':
        """
        Valida que el tiempo de fin sea estrictamente mayor que el tiempo de inicio.
        """
        if self.end_time <= self.start_time:
            raise ValueError(
                "El tiempo de fin (end_time) debe ser mayor que el tiempo de inicio (start_time)."
            )
        return self