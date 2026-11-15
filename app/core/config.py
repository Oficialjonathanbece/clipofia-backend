from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """
    Configuración global de la aplicación utilizando Pydantic Settings.
    Lee automáticamente las variables del archivo .env si existe.
    """
    PROJECT_NAME: str = "Clipofia Backend"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Orígenes permitidos para CORS (puedes sobreescribirlos desde un archivo .env)
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://creofia.com"
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# Instancia global de configuración que puedes importar en cualquier parte del proyecto
settings = Settings()