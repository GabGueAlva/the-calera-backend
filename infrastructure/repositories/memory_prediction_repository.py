from typing import List, Optional, Dict
from datetime import datetime

from domain.entities.prediction import Prediction
from domain.repositories.prediction_repository import PredictionRepository


class MemoryPredictionRepository(PredictionRepository):
    def __init__(self):
        self._predictions: List[Prediction] = []

    async def save_prediction(self, prediction: Prediction) -> None:
        self._predictions.append(prediction)
        today_count = len(await self.get_predictions_by_date(datetime.utcnow().date().isoformat()))
        print(f"[REPOSITORY] ✓ Prediction saved (Daily count: {today_count}/3)")

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

    async def get_todays_predictions(self) -> List[Prediction]:
        """Get all predictions made today"""
        today = datetime.utcnow().date()
        print(f"[REPOSITORY] Looking for predictions from date: {today}")
        print(f"[REPOSITORY] Total predictions in memory: {len(self._predictions)}")

        if self._predictions:
            for p in self._predictions:
                print(f"[REPOSITORY]   - Prediction date: {p.created_at.date()}, Probability: {p.probability:.2%}")

        matching = [
            prediction for prediction in self._predictions
            if prediction.created_at.date() == today
        ]
        print(f"[REPOSITORY] Found {len(matching)} predictions for today")
        return matching

    async def calculate_daily_average_probability(self) -> Optional[float]:
        """Calculate the average frost probability from all predictions made today"""
        todays_predictions = await self.get_todays_predictions()

        if not todays_predictions:
            return None

        avg_probability = sum(p.probability for p in todays_predictions) / len(todays_predictions)
        print(f"[REPOSITORY] Averaging {len(todays_predictions)} predictions: {avg_probability:.2%}")
        return avg_probability