from twilio.rest import Client

from domain.entities.prediction import Prediction, FrostLevel
from ..config.settings import settings


class TwilioWhatsAppClient:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_number = f"whatsapp:{settings.twilio_whatsapp_number}"
        self.to_number = f"whatsapp:{settings.recipient_whatsapp_number}"

    def _get_message_for_frost_level(self, prediction: Prediction, farmer_name: str = None) -> str:
        # Add personalized greeting if farmer name is provided
        greeting = f"¡Hola! {farmer_name}\n\n" if farmer_name else ""

        messages = {
            FrostLevel.FROST_EXPECTED: f"{greeting}🥶 *ALERTA DE HELADA* 🥶\n\n¡Se esperan heladas esta noche!\nProbabilidad: {prediction.probability:.1%}\n\nPor favor, tome medidas de protección para sus cultivos.",
            FrostLevel.POSSIBLE_FROST: f"{greeting}⚠️ *ADVERTENCIA DE HELADA* ⚠️\n\nPosibles condiciones de helada esta noche.\nProbabilidad: {prediction.probability:.1%}\n\nMonitoree las condiciones y esté preparado.",
            FrostLevel.NO_FROST: f"{greeting}✅ *SIN HELADA ESPERADA* ✅\n\nNo se esperan heladas esta noche.\nProbabilidad: {prediction.probability:.1%}\n\n¡Las condiciones se ven favorables!",
        }
        return messages.get(prediction.frost_level, "Actualización meteorológica disponible.")

    async def send_frost_alert(self, prediction: Prediction, phone_number: str, farmer_name: str = None) -> None:
        """
        Send a WhatsApp frost alert to a specific phone number.

        Args:
            prediction: The frost prediction to send
            phone_number: Recipient's phone number (e.g., "+573012592676")
            farmer_name: Optional farmer's name for personalized greeting
        """
        try:
            message_body = self._get_message_for_frost_level(prediction, farmer_name)

            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=f"whatsapp:{phone_number}"
            )

            print(f"WhatsApp message sent successfully to {phone_number}. SID: {message.sid}")

        except Exception as e:
            print(f"Error sending WhatsApp message to {phone_number}: {e}")
            raise