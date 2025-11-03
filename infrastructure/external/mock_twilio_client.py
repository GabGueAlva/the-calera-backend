from domain.entities.prediction import Prediction, FrostLevel


class MockTwilioWhatsAppClient:
    """
    Mock Twilio WhatsApp Client for testing without real Twilio credentials.
    Simulates sending WhatsApp messages and logs them instead.
    """

    def __init__(self):
        print("\n" + "="*60)
        print("[MOCK TWILIO] Using Mock Twilio Client for testing")
        print("[MOCK TWILIO] WhatsApp messages will be simulated (not sent)")
        print("="*60 + "\n")
        self.from_number = "whatsapp:+15555551234"
        self.to_number = "whatsapp:+15555555678"

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
        Simulate sending a WhatsApp alert to a specific phone number.
        In production, replace with real TwilioWhatsAppClient.

        Args:
            prediction: The frost prediction to send
            phone_number: Recipient's phone number (e.g., "+573012592676")
            farmer_name: Optional farmer's name for personalized greeting
        """
        try:
            message_body = self._get_message_for_frost_level(prediction, farmer_name)

            print("\n" + "="*60)
            print("[MOCK TWILIO] 📱 Simulated WhatsApp Message:")
            print("="*60)
            print(f"From: {self.from_number}")
            print(f"To: whatsapp:{phone_number}")
            print("-"*60)
            print(message_body)
            print("="*60)
            print("[MOCK TWILIO] ✓ Message 'sent' successfully (simulated)")
            print(f"[MOCK TWILIO] Message SID: SM_mock_{abs(hash(phone_number)) % 10**16}")
            print("="*60 + "\n")

        except Exception as e:
            print(f"[MOCK TWILIO] Error simulating WhatsApp message: {e}")
            raise
