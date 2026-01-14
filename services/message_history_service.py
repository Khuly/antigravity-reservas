"""
Servicio de historial de mensajes.
"""
from sqlalchemy.orm import Session
from database.models import MessagesHistory, Platform

class MessageHistoryService:
    @staticmethod
    def save_message(db: Session, platform: Platform, customer_id: str, message_text: str, is_from_customer: bool = True, message_id: str = None):
        message = MessagesHistory(platform=platform, customer_id=customer_id, message_text=message_text, is_from_customer=is_from_customer, message_id=message_id)
        db.add(message)
        db.commit()
        return message
