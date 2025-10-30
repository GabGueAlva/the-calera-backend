from typing import Optional, List

from ..use_cases.generate_frost_prediction import GenerateFrostPredictionUseCase
from ..use_cases.send_frost_alert import SendFrostAlertUseCase
from ..dtos.prediction_dto import PredictionDTO


class PredictionService:
    def __init__(
        self,
        generate_prediction_use_case: GenerateFrostPredictionUseCase,
        send_alert_use_case: SendFrostAlertUseCase,
    ):
        self.generate_prediction_use_case = generate_prediction_use_case
        self.send_alert_use_case = send_alert_use_case
        # Expose repository for test endpoint
        self.prediction_repository = generate_prediction_use_case.prediction_repository

    async def generate_prediction(self) -> PredictionDTO:
        prediction = await self.generate_prediction_use_case.execute()
        
        return PredictionDTO(
            probability=prediction.probability,
            frost_level=prediction.frost_level,
            model_type=prediction.model_type,
            created_at=prediction.created_at,
            sarima_probability=prediction.sarima_probability,
            lstm_probability=prediction.lstm_probability,
        )

    async def send_daily_alert(self, phone_numbers: List[str]) -> None:
        await self.send_alert_use_case.execute(phone_numbers)