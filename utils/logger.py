"""
Sistema de logging estructurado usando loguru.
Configura logs a archivo y consola con formato apropiado.
"""
import sys
from loguru import logger
from config import settings


def setup_logger():
    """
    Configura el sistema de logging global.
    - Logs a consola con formato colorizado
    - Logs a archivo con rotación
    """
    # Remover configuración por defecto
    logger.remove()
    
    # Configurar log a consola
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Configurar log a archivo con rotación
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="10 MB",  # Rotar cuando alcance 10MB
        retention="30 days",  # Mantener logs por 30 días
        compression="zip"  # Comprimir logs antiguos
    )
    
    logger.info("Sistema de logging inicializado")
    return logger


# Instancia global del logger
app_logger = setup_logger()