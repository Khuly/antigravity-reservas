"""
Cliente unificado para las APIs de Meta.
"""
import httpx
from typing import Dict, Any, Optional
from config import settings
from utils.logger import app_logger

class MetaAPIClient:
    def __init__(self):
        self.base_url = settings.graph_api_url
    
    async def send_instagram_message(self, recipient_id: str, message_text: str):
        url = f"{self.base_url}/me/messages"
        payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
        headers = {"Authorization": f"Bearer {settings.instagram_page_access_token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers=headers)

    async def send_messenger_message(self, recipient_id: str, message_text: str):
        url = f"{self.base_url}/me/messages"
        payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
        headers = {"Authorization": f"Bearer {settings.messenger_page_access_token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers=headers)

    async def send_whatsapp_message(self, recipient_number: str, message_text: str):
        url = f"{self.base_url}/{settings.whatsapp_phone_number_id}/messages"
        payload = {"messaging_product": "whatsapp", "to": recipient_number, "text": {"body": message_text}}
        headers = {"Authorization": f"Bearer {settings.whatsapp_access_token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload, headers=headers)

meta_api_client = MetaAPIClient()
