from domain.entities.prediction import Prediction
from domain.services.notification_service import NotificationService
from .twilio_client import TwilioWhatsAppClient


class TwilioNotificationService(NotificationService):
    def __init__(self, twilio_client: TwilioWhatsAppClient):
        self.twilio_client = twilio_client

    async def send_frost_alert(self, prediction: Prediction, phone_number: str, farmer_name: str = None) -> None:
        await self.twilio_client.send_frost_alert(prediction, phone_number, farmer_name)