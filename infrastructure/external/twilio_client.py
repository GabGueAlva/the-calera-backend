from twilio.rest import Client

from ...domain.entities.prediction import Prediction, FrostLevel
from ..config.settings import settings


class TwilioWhatsAppClient:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_number = f"whatsapp:{settings.twilio_whatsapp_number}"
        self.to_number = f"whatsapp:{settings.recipient_whatsapp_number}"

    def _get_message_for_frost_level(self, prediction: Prediction) -> str:
        messages = {
            FrostLevel.FROST_EXPECTED: f"🥶 **FROST ALERT** 🥶\n\nFrost is expected tonight!\nProbability: {prediction.probability:.1%}\n\nPlease take protective measures for your crops.",
            FrostLevel.POSSIBLE_FROST: f"⚠️ **FROST WARNING** ⚠️\n\nPossible frost conditions tonight.\nProbability: {prediction.probability:.1%}\n\nMonitor conditions and be prepared.",
            FrostLevel.NO_FROST: f"✅ **NO FROST EXPECTED** ✅\n\nNo frost expected tonight.\nProbability: {prediction.probability:.1%}\n\nConditions look favorable!",
        }
        return messages.get(prediction.frost_level, "Weather update available.")

    async def send_frost_alert(self, prediction: Prediction) -> None:
        try:
            message_body = self._get_message_for_frost_level(prediction)
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=self.to_number
            )
            
            print(f"WhatsApp message sent successfully. SID: {message.sid}")
            
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            raise