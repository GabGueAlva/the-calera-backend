from datetime import datetime
from typing import List

from ...domain.entities.prediction import Prediction, PredictionModel, FrostLevel
from ...domain.entities.sensor_data import SensorData
from ...domain.repositories.sensor_data_repository import SensorDataRepository
from ...domain.repositories.prediction_repository import PredictionRepository
from ...domain.services.ml_model_service import MLModelService
from ...domain.value_objects.time_range import TimeRange


class GenerateFrostPredictionUseCase:
    def __init__(
        self,
        sensor_data_repository: SensorDataRepository,
        prediction_repository: PredictionRepository,
        sarima_service: MLModelService,
        lstm_service: MLModelService,
    ):
        self.sensor_data_repository = sensor_data_repository
        self.prediction_repository = prediction_repository
        self.sarima_service = sarima_service
        self.lstm_service = lstm_service

    async def execute(self) -> Prediction:
        time_range = TimeRange.last_n_days(10)
        sensor_data = await self.sensor_data_repository.get_sensor_data_in_range(time_range)
        
        if not sensor_data:
            raise ValueError("No sensor data available for prediction")

        sarima_probability = await self.sarima_service.predict_frost_probability(sensor_data)
        lstm_probability = await self.lstm_service.predict_frost_probability(sensor_data)
        
        hybrid_probability = (sarima_probability * 0.5) + (lstm_probability * 0.5)
        
        frost_level = Prediction.determine_frost_level(hybrid_probability)
        
        prediction = Prediction(
            probability=hybrid_probability,
            frost_level=frost_level,
            model_type=PredictionModel.HYBRID,
            created_at=datetime.utcnow(),
            sarima_probability=sarima_probability,
            lstm_probability=lstm_probability,
        )
        
        await self.prediction_repository.save_prediction(prediction)
        
        return prediction