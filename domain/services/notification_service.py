from abc import ABC, abstractmethod

from ..entities.prediction import Prediction


class NotificationService(ABC):
    @abstractmethod
    async def send_frost_alert(self, prediction: Prediction) -> None:
        pass