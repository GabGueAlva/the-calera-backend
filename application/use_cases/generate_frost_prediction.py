from datetime import datetime
from typing import List

from domain.entities.prediction import Prediction, PredictionModel, FrostLevel
from domain.entities.sensor_data import SensorData
from domain.repositories.sensor_data_repository import SensorDataRepository
from domain.repositories.prediction_repository import PredictionRepository
from domain.services.ml_model_service import MLModelService
from domain.value_objects.time_range import TimeRange


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
        print("\n" + "🌡️ " + "="*56 + " 🌡️")
        print("     STARTING FROST PREDICTION PROCESS")
        print("🌡️ " + "="*56 + " 🌡️\n")

        print("[PREDICTION] Step 1: Fetching sensor data from last 10 days...")
        time_range = TimeRange.last_n_days(10)
        sensor_data = await self.sensor_data_repository.get_sensor_data_in_range(time_range)

        if not sensor_data:
            raise ValueError("No sensor data available for prediction")

        print(f"[PREDICTION] ✓ Retrieved {len(sensor_data)} sensor readings\n")

        print("[PREDICTION] Step 2: Running SARIMA model prediction...")
        sarima_probability = await self.sarima_service.predict_frost_probability(sensor_data)
        print(f"[PREDICTION] ✓ SARIMA probability: {sarima_probability:.2%}\n")

        print("[PREDICTION] Step 3: Running LSTM model prediction...")
        lstm_probability = await self.lstm_service.predict_frost_probability(sensor_data)
        print(f"[PREDICTION] ✓ LSTM probability: {lstm_probability:.2%}\n")

        hybrid_probability = (sarima_probability * 0.4) + (lstm_probability * 0.6)
        print("[PREDICTION] Step 4: Calculating hybrid prediction...")
        print(f"[PREDICTION] Hybrid formula: (SARIMA * 0.4) + (LSTM * 0.6)")
        print(f"[PREDICTION] ✓ Hybrid probability: {hybrid_probability:.2%}\n")

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

        print("="*60)
        print(f"✓ PREDICTION COMPLETE")
        print(f"  Frost Level: {frost_level.value}")
        print(f"  Probability: {hybrid_probability:.2%}")
        print("="*60 + "\n")

        return prediction