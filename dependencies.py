from application.services.prediction_service import PredictionService
from application.services.farmer_service import FarmerService
from application.services.sensor_data_service import SensorDataService
from application.use_cases.generate_frost_prediction import GenerateFrostPredictionUseCase
from application.use_cases.send_frost_alert import SendFrostAlertUseCase
from application.use_cases.register_farmer import RegisterFarmerUseCase
from application.use_cases.get_all_farmers import GetAllFarmersUseCase

from infrastructure.external.tts_client import TTSClient
from infrastructure.external.twilio_client import TwilioWhatsAppClient
from infrastructure.external.twilio_notification_service import TwilioNotificationService
from infrastructure.repositories.tts_sensor_data_repository import TTSSensorDataRepository
from infrastructure.repositories.database_sensor_data_repository import DatabaseSensorDataRepository
from infrastructure.repositories.memory_prediction_repository import MemoryPredictionRepository
from infrastructure.repositories.json_farmer_repository import JSONFarmerRepository
from infrastructure.database.database import SensorDatabase
from infrastructure.models.sarima_model import SARIMAModelService
from infrastructure.models.lstm_model import LSTMModelService

from interfaces.controllers.webhook_controller import WebhookController
from interfaces.controllers.prediction_controller import PredictionController
from interfaces.controllers.farmer_controller import FarmerController


class DependencyContainer:
    def __init__(self):
        # External services
        # Using real TTS client with configured credentials
        self.tts_client = TTSClient()

        # Using real Twilio client for WhatsApp notifications
        self.twilio_client = TwilioWhatsAppClient()

        # Database
        self.sensor_database = SensorDatabase(db_path="data/sensor_data.db")

        # Repositories
        # Use database repository for sensor data storage
        self.sensor_data_repository = DatabaseSensorDataRepository(self.sensor_database)
        self.prediction_repository = MemoryPredictionRepository()
        self.farmer_repository = JSONFarmerRepository()  # Stores farmers in data/farmers.json
        
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
            self.farmer_repository,  # Inject farmer repository for personalized messages
        )

        self.register_farmer_use_case = RegisterFarmerUseCase(
            self.farmer_repository
        )

        self.get_all_farmers_use_case = GetAllFarmersUseCase(
            self.farmer_repository
        )
        
        # Application services
        self.prediction_service = PredictionService(
            self.generate_prediction_use_case,
            self.send_alert_use_case,
        )

        self.farmer_service = FarmerService(
            self.register_farmer_use_case,
            self.get_all_farmers_use_case
        )

        self.sensor_data_service = SensorDataService(
            self.sensor_data_repository
        )

        # Controllers
        self.webhook_controller = WebhookController(
            sensor_repository=self.sensor_data_repository  # Inject database repository to save webhook data
        )
        self.prediction_controller = PredictionController(
            self.prediction_service,
            self.sensor_data_service,  # Inject sensor data service
            self.farmer_repository  # Inject farmer repository for auto-sending alerts
        )
        self.farmer_controller = FarmerController(self.farmer_service)


# Global dependency container
dependencies = DependencyContainer()