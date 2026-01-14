"""
Procesador de mensajes con Inteligencia Artificial.
Gestiona la lógica de conversación, detección de intenciones y consultas a la base de conocimientos.
"""
import json
import os
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Platform
from utils.entity_extractor import EntityExtractor
from utils.logger import app_logger
from services.reservation_service import ReservationService
from services.notification_service import NotificationService
from services.message_history_service import MessageHistoryService
from services.meta_api_client import meta_api_client
from config import settings

class MessageProcessor:
    """
    Procesador central de mensajes.
    Próximamente integrará un modelo LLM (GPT-4/Gemini) para respuestas fluidas.
    """
    
    def __init__(self):
        self.kb_path = "restaurant_info.json"
        self.restaurant_info = self._load_knowledge_base()

    def _load_knowledge_base(self) -> Dict:
        """Carga la información del restaurante desde el JSON."""
        if os.path.exists(self.kb_path):
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                return json.load(f).get("restaurant", {})
        return {}

    def _generate_ai_response(self, message_text: str) -> str:
        """
        Lógica de respuesta basada en la base de conocimientos.
        Busca coincidencias en la configuración general y en la lista de FAQs.
        """
        msg = message_text.lower()
        
        # 1. Saludos
        if any(k in msg for k in ["hola", "buenos dias", "buenas tardes", "buenas noches"]):
            return self.restaurant_info.get("message_examples", {}).get("greeting", "¡Hola!")

        # 2. Ubicación
        if any(k in msg for k in ["donde", "ubicacion", "ubicación", "llegar", "direccion", "dirección"]):
            return f"Estamos ubicados en: {self.restaurant_info.get('location')}"
        
        # 3. Horarios
        if any(k in msg for k in ["horario", "abren", "hora", "cuándo", "cuando"]):
            schedule = self.restaurant_info.get("schedule", {})
            sched_str = "\n".join([f"- {d.capitalize()}: {h}" for d, h in schedule.items()])
            return f"Nuestros horarios son:\n{sched_str}"

        # 4. Buscar en la lista de FAQs del JSON
        faqs = self.restaurant_info.get("faqs", [])
        for faq in faqs:
            # Si alguna palabra significativa de la pregunta está en el mensaje
            question_text = faq.get("question", "").lower()
            # Dividir en palabras y filtrar conectores cortos
            keywords = [w for w in question_text.split() if len(w) > 3]
            if any(k in msg for k in keywords):
                return faq.get("answer")

        return "Lo siento, no tengo esa información específica. ¿Te gustaría que te comunique con un agente?"

    async def process_message(
        self,
        db: Session,
        platform: Platform,
        customer_id: str,
        customer_name: Optional[str],
        message_text: str,
        message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Procesa un mensaje entrante de cualquier plataforma."""
        
        # 1. Guardar en historial
        MessageHistoryService.save_message(
            db=db, platform=platform, customer_id=customer_id,
            message_text=message_text, is_from_customer=True, message_id=message_id
        )

        msg_lower = message_text.lower()

        # 2. Detectar si pide hablar con un agente
        if any(k in msg_lower for k in ["agente", "hablar con alguien", "ayuda", "persona"]):
            # Notificar al agente vía WhatsApp
            agent_msg = f"⚠️ ATENCIÓN: El cliente {customer_name or customer_id} en {platform.value} solicita hablar con un agente.\n\nÚltimo mensaje: '{message_text}'"
            try:
                await meta_api_client.send_whatsapp_message(
                    recipient_number=settings.agent_whatsapp_number,
                    message_text=agent_msg
                )
            except Exception as e:
                app_logger.error(f"Error notificando al agente vía WhatsApp: {e}")

            return {
                "type": "agent_request",
                "response_message": self.restaurant_info.get("message_examples", {}).get("agent_requested")
            }

        # 3. Detectar intención de reserva
        if any(k in msg_lower for k in ["reserva", "mesa", "turno", "cita"]):
            entities = EntityExtractor.extract_all(message_text)
            reservation = ReservationService.create_reservation(
                db=db, platform=platform, customer_id=customer_id,
                customer_name=customer_name,
                reservation_date=entities.get("date"),
                reservation_time=entities.get("time"),
                party_size=entities.get("party_size"),
                notes=message_text
            )
            
            NotificationService.create_notification(
                db=db,
                message=f"Nueva reserva de {customer_name or 'Cliente'} vía {platform.value}",
                reservation_id=reservation.id
            )

            return {
                "type": "reservation_request",
                "response_message": self.restaurant_info.get("message_examples", {}).get("reservation_detected")
            }

        # 4. Respuesta general de la "IA" (Base de conocimientos)
        return {
            "type": "knowledge_response",
            "response_message": self._generate_ai_response(message_text)
        }

# Instancia global
message_processor = MessageProcessor()
