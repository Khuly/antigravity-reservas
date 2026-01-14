"""
Aplicación principal FastAPI.
Punto de entrada del servidor de webhooks.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import init_db
from routers import instagram_webhook, messenger_webhook, whatsapp_webhook
from utils.logger import app_logger
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicación.
    Se ejecuta al inicio y al final.
    """
    # Startup
    app_logger.info("Iniciando aplicación...")
    app_logger.info(f"Modo debug: {settings.debug}")
    
    # Inicializar base de datos
    init_db()
    
    yield
    
    # Shutdown
    app_logger.info("Cerrando aplicación...")


# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Gestión de Reservas Multi-Plataforma",
    description="Backend para gestionar reservas desde Instagram, Messenger y WhatsApp",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(instagram_webhook.router)
app.include_router(messenger_webhook.router)
app.include_router(whatsapp_webhook.router)


@app.get("/")
async def root():
    """
    Endpoint raíz para verificar que el servidor está funcionando.
    """
    return {
        "status": "ok",
        "message": "Sistema de Gestión de Reservas Multi-Plataforma",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Endpoint de health check.
    """
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    
    app_logger.info(f"Iniciando servidor en {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )