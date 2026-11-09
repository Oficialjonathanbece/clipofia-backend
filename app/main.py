from fastapi import FastAPI

# Inicializamos la aplicación FastAPI con metadatos descriptivos
app = FastAPI(
    title="Video Editor Backend",
    description="API modular para procesamiento y recorte de vídeo 🚀",
    version="1.0.0"
)

@app.get("/")
def read_root():
    """
    Endpoint raíz para verificar que el servidor está activo y funcionando.
    """
    return {
        "status": "online",
        "message": "Bienvenido al backend del editor de vídeo 🚀"
    }