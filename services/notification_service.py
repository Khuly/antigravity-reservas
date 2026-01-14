"""
Servicio de notificaciones para el agente.
"""
from typing import List
from sqlalchemy.orm import Session
from database.models import Notification
from utils.logger import app_logger


class NotificationService:
    @staticmethod
    def create_notification(db: Session, message: str, reservation_id: int = None):
        notification = Notification(message=message, reservation_id=reservation_id, is_read=False)
        db.add(notification)
        db.commit()
        db.refresh(notification)
        app_logger.info(f"Notificación creada: ID={notification.id}")
        return notification

    @staticmethod
    def mark_all_as_read(db: Session):
        db.query(Notification).filter(Notification.is_read == False).update({"is_read": True})
        db.commit()

    @staticmethod
    def get_unread_notifications(db: Session):
        return db.query(Notification).filter(Notification.is_read == False).order_by(Notification.created_at.desc()).all()

    @staticmethod
    def get_unread_count(db: Session):
        return db.query(Notification).filter(Notification.is_read == False).count()
