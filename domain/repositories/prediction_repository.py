from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.prediction import Prediction


class PredictionRepository(ABC):
    @abstractmethod
    async def save_prediction(self, prediction: Prediction) -> None:
        pass

    @abstractmethod
    async def get_latest_prediction(self) -> Optional[Prediction]:
        pass

    @abstractmethod
    async def get_predictions_by_date(self, date: str) -> List[Prediction]:
        pass