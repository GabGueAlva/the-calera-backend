from abc import ABC, abstractmethod

from ..entities.prediction import Prediction


class NotificationService(ABC):
    @abstractmethod
    async def send_frost_alert(self, prediction: Prediction, phone_number: str, farmer_name: str = None) -> None:
        """
        Send a frost alert to a specific phone number.

        Args:
            prediction: The frost prediction to send
            phone_number: Phone number in format "+573012592676"
            farmer_name: Optional farmer's full name for personalized greeting
        """
        pass