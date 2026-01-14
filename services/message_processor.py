"""
Procesador de mensajes entrantes.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Platform
from utils.entity_extractor import EntityExtractor
from utils.logger import app_logger
from services.reservation_service import ReservationService
from services.notification_service import NotificationService
from services.message_history_service import MessageHistoryService

class MessageProcessor:
    RESERVATION_KEYWORDS = ["reserva", "reservar", "mesa", "turno", "cita"]

    @staticmethod
    def detect_reservation_intent(message_text: str) -> bool:
        message_lower = message_text.lower()
        return any(keyword in message_lower for keyword in MessageProcessor.RESERVATION_KEYWORDS)

    @staticmethod
    async def process_message(db: Session, platform: Platform, customer_id: str, customer_name: Optional[str], message_text: str, message_id: Optional[str] = None) -> Dict[str, Any]:
        MessageHistoryService.save_message(db=db, platform=platform, customer_id=customer_id, message_text=message_text, is_from_customer=True, message_id=message_id)
        if MessageProcessor.detect_reservation_intent(message_text):
            entities = EntityExtractor.extract_all(message_text)
            reservation = ReservationService.create_reservation(db=db, platform=platform, customer_id=customer_id, customer_name=customer_name, reservation_date=entities.get("date"), reservation_time=entities.get("time"), party_size=entities.get("party_size"), notes=message_text)
            NotificationService.create_notification(db=db, message=f"Nueva reserva de {customer_name or 'Cliente'}", reservation_id=reservation.id)
            return {"type": "reservation_request", "response_message": "Gracias por tu solicitud. Un agente la revisará pronto."}
        return {"type": "general_message", "response_message": None}
