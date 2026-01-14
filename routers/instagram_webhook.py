"""
Router de webhooks para Instagram.
"""
from fastapi import APIRouter, Request, Response, Depends
from sqlalchemy.orm import Session
from database import get_db
from database.models import Platform
from services.message_processor import MessageProcessor
from services.meta_api_client import meta_api_client

router = APIRouter(prefix="/webhooks/instagram", tags=["Instagram"])

@router.post("")
async def receive_webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            sender_id = event.get("sender", {}).get("id")
            text = event.get("message", {}).get("text")
            if text:
                result = await MessageProcessor.process_message(db=db, platform=Platform.INSTAGRAM, customer_id=sender_id, customer_name=None, message_text=text)
                if result.get("response_message"):
                    await meta_api_client.send_instagram_message(sender_id, result["response_message"])
    return {"status": "ok"}
