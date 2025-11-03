from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..schemas.webhook_schemas import TTSWebhookPayload, WebhookResponse


class WebhookController:
    def __init__(self):
        self.router = APIRouter()
        self.router.add_api_route(
            "/webhook",
            self.handle_tts_webhook,
            methods=["POST"],
            response_model=WebhookResponse
        )

    async def handle_tts_webhook(self, payload: Dict[Any, Any]) -> WebhookResponse:
        try:
            print(f"Received TTS webhook: {payload}")
            
            return WebhookResponse(
                status="success",
                message="Webhook received successfully",
                timestamp=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            print(f"Error processing webhook: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")