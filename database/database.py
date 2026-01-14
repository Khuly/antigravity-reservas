"""
Configuración de SQLAlchemy para la base de datos.
Implementa connection pooling y dependency injection para FastAPI.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from config import settings
from utils.logger import app_logger

# Crear engine de SQLAlchemy
# Para SQLite: check_same_thread=False permite usar en múltiples threads
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug  # Log de queries SQL en modo debug
)

# Crear SessionLocal para dependency injection
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para los modelos ORM
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency injection para obtener sesión de base de datos.
    
    Uso en FastAPI:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    
    Yields:
        Session: Sesión de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    Debe llamarse al inicio de la aplicación.
    """
    app_logger.info("Inicializando base de datos...")
    Base.metadata.create_all(bind=engine)
    app_logger.info("Base de datos inicializada correctamente")