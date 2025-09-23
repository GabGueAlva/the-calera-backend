from typing import List, Optional, Dict
from datetime import datetime

from ...domain.entities.prediction import Prediction
from ...domain.repositories.prediction_repository import PredictionRepository


class MemoryPredictionRepository(PredictionRepository):
    def __init__(self):
        self._predictions: List[Prediction] = []

    async def save_prediction(self, prediction: Prediction) -> None:
        self._predictions.append(prediction)

    async def get_latest_prediction(self) -> Optional[Prediction]:
        if not self._predictions:
            return None
        return max(self._predictions, key=lambda p: p.created_at)

    async def get_predictions_by_date(self, date: str) -> List[Prediction]:
        target_date = datetime.fromisoformat(date).date()
        return [
            prediction for prediction in self._predictions
            if prediction.created_at.date() == target_date
        ]