from ...domain.repositories.prediction_repository import PredictionRepository
from ...domain.services.notification_service import NotificationService


class SendFrostAlertUseCase:
    def __init__(
        self,
        prediction_repository: PredictionRepository,
        notification_service: NotificationService,
    ):
        self.prediction_repository = prediction_repository
        self.notification_service = notification_service

    async def execute(self) -> None:
        latest_prediction = await self.prediction_repository.get_latest_prediction()
        
        if not latest_prediction:
            raise ValueError("No prediction available to send alert")
        
        await self.notification_service.send_frost_alert(latest_prediction)