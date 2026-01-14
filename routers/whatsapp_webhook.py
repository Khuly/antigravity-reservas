"""
Router de webhooks para WhatsApp.
"""
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from database import get_db
from database.models import Platform
from services.message_processor import MessageProcessor
from services.meta_api_client import meta_api_client

router = APIRouter(prefix="/webhooks/whatsapp", tags=["WhatsApp"])

@router.post("")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                sender_id = message.get("from")
                text = message.get("text", {}).get("body")
                name = value.get("contacts", [{}])[0].get("profile", {}).get("name")
                if text:
                    result = await MessageProcessor.process_message(db=db, platform=Platform.WHATSAPP, customer_id=sender_id, customer_name=name, message_text=text)
                    if result.get("response_message"):
                        await meta_api_client.send_whatsapp_message(sender_id, result["response_message"])
    return {"status": "ok"}
