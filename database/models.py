"""
Modelos de base de datos usando SQLAlchemy ORM.
Define las tablas para reservas, mensajes y notificaciones.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
import enum
from .database import Base


class Platform(str, enum.Enum):
    """Plataformas soportadas"""
    INSTAGRAM = "instagram"
    MESSENGER = "messenger"
    WHATSAPP = "whatsapp"


class ReservationStatus(str, enum.Enum):
    """Estados de una reserva"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class PendingReservation(Base):
    """
    Tabla de reservas (pendientes y confirmadas).
    
    REGLA CRÍTICA: Al confirmar una reserva, se actualiza el campo 'status'
    de PENDING a CONFIRMED. NO se duplica el registro.
    """
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información de la plataforma
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    customer_id = Column(String(255), nullable=False, index=True)  # PSID, Instagram ID, WhatsApp number
    customer_name = Column(String(255), nullable=True)
    
    # Detalles de la reserva
    reservation_date = Column(DateTime, nullable=True)  # Fecha de la reserva
    reservation_time = Column(String(10), nullable=True)  # Hora (formato: "20:00")
    party_size = Column(Integer, nullable=True)  # Cantidad de personas
    
    # Estado y metadata
    status = Column(SQLEnum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False, index=True)
    notes = Column(Text, nullable=True)  # Notas adicionales
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    notifications = relationship("Notification", back_populates="reservation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, platform={self.platform}, status={self.status}, customer={self.customer_name})>"


class MessagesHistory(Base):
    """
    Historial de mensajes entre el sistema y los clientes.
    Almacena tanto mensajes entrantes como salientes.
    """
    __tablename__ = "messages_history"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Información de la plataforma
    platform = Column(SQLEnum(Platform), nullable=False, index=True)
    customer_id = Column(String(255), nullable=False, index=True)
    
    # Contenido del mensaje
    message_text = Column(Text, nullable=False)
    is_from_customer = Column(Boolean, default=True, nullable=False)  # True si es del cliente, False si es del bot
    
    # Metadata
    message_id = Column(String(255), nullable=True)  # ID del mensaje de la plataforma
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        direction = "FROM" if self.is_from_customer else "TO"
        return f"<Message(id={self.id}, {direction} customer, platform={self.platform})>"


class Notification(Base):
    """
    Notificaciones para el agente.
    Se crean cuando llega una nueva reserva o mensaje importante.
    """
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Relación con reserva (opcional)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=True, index=True)
    
    # Contenido de la notificación
    message = Column(Text, nullable=False)
    
    # Estado
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relaciones
    reservation = relationship("PendingReservation", back_populates="notifications")
    
    def __repr__(self):
        status = "READ" if self.is_read else "UNREAD"
        return f"<Notification(id={self.id}, {status}, reservation_id={self.reservation_id})>"