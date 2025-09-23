from application.services.prediction_service import PredictionService
from application.use_cases.generate_frost_prediction import GenerateFrostPredictionUseCase
from application.use_cases.send_frost_alert import SendFrostAlertUseCase

from infrastructure.external.tts_client import TTSClient
from infrastructure.external.twilio_client import TwilioWhatsAppClient
from infrastructure.external.twilio_notification_service import TwilioNotificationService
from infrastructure.repositories.tts_sensor_data_repository import TTSSensorDataRepository
from infrastructure.repositories.memory_prediction_repository import MemoryPredictionRepository
from infrastructure.models.sarima_model import SARIMAModelService
from infrastructure.models.lstm_model import LSTMModelService

from interfaces.controllers.webhook_controller import WebhookController
from interfaces.controllers.prediction_controller import PredictionController


class DependencyContainer:
    def __init__(self):
        # External services
        self.tts_client = TTSClient()
        self.twilio_client = TwilioWhatsAppClient()
        
        # Repositories
        self.sensor_data_repository = TTSSensorDataRepository(self.tts_client)
        self.prediction_repository = MemoryPredictionRepository()
        
        # ML Models
        self.sarima_service = SARIMAModelService()
        self.lstm_service = LSTMModelService()
        
        # Services
        self.notification_service = TwilioNotificationService(self.twilio_client)
        
        # Use cases
        self.generate_prediction_use_case = GenerateFrostPredictionUseCase(
            self.sensor_data_repository,
            self.prediction_repository,
            self.sarima_service,
            self.lstm_service,
        )
        
        self.send_alert_use_case = SendFrostAlertUseCase(
            self.prediction_repository,
            self.notification_service,
        )
        
        # Application services
        self.prediction_service = PredictionService(
            self.generate_prediction_use_case,
            self.send_alert_use_case,
        )
        
        # Controllers
        self.webhook_controller = WebhookController()
        self.prediction_controller = PredictionController(self.prediction_service)


# Global dependency container
dependencies = DependencyContainer()