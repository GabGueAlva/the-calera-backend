from typing import Dict, Any, Optional
from pydantic import BaseModel


class TTSWebhookPayload(BaseModel):
    end_device_ids: Dict[str, Any]
    uplink_message: Dict[str, Any]
    received_at: str


class WebhookResponse(BaseModel):
    status: str
    message: str
    timestamp: Optional[str] = None